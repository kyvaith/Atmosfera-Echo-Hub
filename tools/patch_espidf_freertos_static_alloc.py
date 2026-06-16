# ESP-IDF 6.0.1 workaround for ESP32-P4 boot-time FreeRTOS heap starvation.
#
# IDF's common FreeRTOS port allocates IDLE and Timer task buffers from
# pvPortMalloc() even when static allocation is enabled. On our large ESP32-P4
# build this can fail before ESPHome starts, because the early FreeRTOS heap may
# not contain a contiguous 2 KiB block for the timer task stack yet.
#
# Keep the workaround local and easy to remove once the framework package no
# longer needs it.

# ruff: noqa: F821
# pylint: disable=undefined-variable
from contextlib import suppress
from pathlib import Path
import re

env = None
with suppress(NameError):
    Import("env")  # type: ignore[name-defined]


PATCHED_BODY = r'''#if ( configSUPPORT_STATIC_ALLOCATION == 1 )

static StaticTask_t s_idle_task_tcb[configNUMBER_OF_CORES];
static StackType_t s_idle_task_stack[configNUMBER_OF_CORES][configMINIMAL_STACK_SIZE];
static BaseType_t s_idle_task_next;

void vApplicationGetIdleTaskMemory(StaticTask_t **ppxIdleTaskTCBBuffer,
                                   StackType_t **ppxIdleTaskStackBuffer,
                                   configSTACK_DEPTH_TYPE *pulIdleTaskStackSize)
{
    BaseType_t idle_index = s_idle_task_next;
    if (idle_index >= configNUMBER_OF_CORES) {
        idle_index = 0;
    }
    s_idle_task_next = idle_index + 1;
    *ppxIdleTaskTCBBuffer = &s_idle_task_tcb[idle_index];
    *ppxIdleTaskStackBuffer = &s_idle_task_stack[idle_index][0];
    *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
}

#if ( ( CONFIG_FREERTOS_SMP ) && ( configNUMBER_OF_CORES > 1 ) )
void vApplicationGetPassiveIdleTaskMemory(StaticTask_t **ppxIdleTaskTCBBuffer,
                                          StackType_t **ppxIdleTaskStackBuffer,
                                          configSTACK_DEPTH_TYPE *pulIdleTaskStackSize,
                                          BaseType_t xPassiveIdleTaskIndex)
{
    BaseType_t idle_index = xPassiveIdleTaskIndex + 1;
    if (idle_index >= configNUMBER_OF_CORES) {
        idle_index = 0;
    }
    *ppxIdleTaskTCBBuffer = &s_idle_task_tcb[idle_index];
    *ppxIdleTaskStackBuffer = &s_idle_task_stack[idle_index][0];
    *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
}
#endif /* ( ( CONFIG_FREERTOS_SMP ) && ( configNUMBER_OF_CORES > 1 ) ) */

#if configUSE_TIMERS
static StaticTask_t s_timer_task_tcb;
static StackType_t s_timer_task_stack[configTIMER_TASK_STACK_DEPTH];

void vApplicationGetTimerTaskMemory(StaticTask_t **ppxTimerTaskTCBBuffer,
                                    StackType_t **ppxTimerTaskStackBuffer,
                                    configSTACK_DEPTH_TYPE *pulTimerTaskStackSize)
{
    *ppxTimerTaskTCBBuffer = &s_timer_task_tcb;
    *ppxTimerTaskStackBuffer = &s_timer_task_stack[0];
    *pulTimerTaskStackSize = configTIMER_TASK_STACK_DEPTH;
}
#endif //configUSE_TIMERS

#endif // configSUPPORT_STATIC_ALLOCATION == 1'''


MAIN_CREATE_DYNAMIC = r'''    BaseType_t res = xTaskCreatePinnedToCore(main_task, "main",
                                             ESP_TASK_MAIN_STACK, NULL,
                                             ESP_TASK_MAIN_PRIO, NULL, ESP_TASK_MAIN_CORE);
    assert(res == pdTRUE);
    (void)res;'''


MAIN_CREATE_STATIC = r'''#if ( configSUPPORT_STATIC_ALLOCATION == 1 )
    static StaticTask_t s_main_task_tcb;
    static StackType_t s_main_task_stack[ESP_TASK_MAIN_STACK];
    TaskHandle_t main_handle = xTaskCreateStaticPinnedToCore(main_task, "main",
                                                             ESP_TASK_MAIN_STACK, NULL,
                                                             ESP_TASK_MAIN_PRIO,
                                                             s_main_task_stack,
                                                             &s_main_task_tcb,
                                                             ESP_TASK_MAIN_CORE);
    assert(main_handle != NULL);
#else
    BaseType_t res = xTaskCreatePinnedToCore(main_task, "main",
                                             ESP_TASK_MAIN_STACK, NULL,
                                             ESP_TASK_MAIN_PRIO, NULL, ESP_TASK_MAIN_CORE);
    assert(res == pdTRUE);
    (void)res;
#endif'''


def _read_idf_version(framework_dir: Path) -> tuple[int, int, int]:
    version_file = framework_dir / "version.txt"
    if not version_file.exists():
        raise RuntimeError("ESP-IDF version.txt not found; FreeRTOS patch needs review")
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", version_file.read_text(encoding="utf-8"))
    if match is None:
        raise RuntimeError("Unsupported ESP-IDF version string; FreeRTOS patch needs review")
    return tuple(int(part) for part in match.groups())


def _patch_port_common(framework_path: Path) -> None:
    target = framework_path / "components" / "freertos" / "port_common.c"
    text = target.read_text(encoding="utf-8")
    if "static BaseType_t s_idle_task_next" in text:
        print("FreeRTOS static allocation patch: port_common already present")
        return

    start = text.find("#if ( configSUPPORT_STATIC_ALLOCATION == 1 )")
    end_marker = "#endif // configSUPPORT_STATIC_ALLOCATION == 1"
    end = text.find(end_marker, start)
    if start < 0 or end < 0:
        raise RuntimeError("FreeRTOS static allocation block not found; patch needs review")
    end += len(end_marker)

    if (
        "pvPortMalloc(configTIMER_TASK_STACK_DEPTH)" not in text[start:end]
        and "s_timer_task_stack[configTIMER_TASK_STACK_DEPTH]" not in text[start:end]
    ):
        raise RuntimeError("Unexpected FreeRTOS static allocation block; patch needs review")

    target.write_text(text[:start] + PATCHED_BODY + text[end:], encoding="utf-8")
    print("FreeRTOS static allocation patch: applied static idle/timer buffers")


def _restore_app_startup(framework_path: Path) -> None:
    target = framework_path / "components" / "freertos" / "app_startup.c"
    text = target.read_text(encoding="utf-8")
    if "s_main_task_stack[ESP_TASK_MAIN_STACK]" not in text:
        print("FreeRTOS static allocation patch: app_startup uses framework default")
        return

    if MAIN_CREATE_STATIC not in text:
        raise RuntimeError("patched main_task creation block not found; patch needs review")

    target.write_text(text.replace(MAIN_CREATE_STATIC, MAIN_CREATE_DYNAMIC, 1), encoding="utf-8")
    print("FreeRTOS static allocation patch: restored framework main task creation")


def main() -> None:
    framework_dir = env.PioPlatform().get_package_dir("framework-espidf")
    if not framework_dir:
        raise RuntimeError("framework-espidf package directory not found")

    framework_path = Path(framework_dir)
    idf_version = _read_idf_version(framework_path)
    if idf_version[0] != 6:
        print(
            "FreeRTOS static allocation patch: skipped "
            f"ESP-IDF {idf_version[0]}.{idf_version[1]}.{idf_version[2]}"
        )
        return

    _patch_port_common(framework_path)
    _restore_app_startup(framework_path)


if env is not None:
    main()
