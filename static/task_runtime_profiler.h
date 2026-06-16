#pragma once

#include "esphome/core/log.h"

#include <cstring>

#include <esp_heap_caps.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

namespace atmosfera_diag {

static const char *const TASK_PROF_TAG = "task.prof";

struct TaskRuntimePrev {
  UBaseType_t number{0};
  uint64_t runtime{0};
  bool valid{false};
};

struct TaskRuntimeRow {
  const char *name{nullptr};
  uint64_t delta{0};
  UBaseType_t priority{0};
  uint32_t stack_watermark{0};
  int32_t core{-2};
  eTaskState state{eInvalid};
};

inline const char *task_state_name(eTaskState state) {
  switch (state) {
    case eRunning:
      return "run";
    case eReady:
      return "ready";
    case eBlocked:
      return "block";
    case eSuspended:
      return "suspend";
    case eDeleted:
      return "delete";
    default:
      return "?";
  }
}

inline bool task_is_idle(const char *name) {
  return name != nullptr && (std::strstr(name, "IDLE") != nullptr || std::strstr(name, "Idle") != nullptr ||
                             std::strstr(name, "idle") != nullptr);
}

inline int32_t task_core_id(const TaskStatus_t &task) {
#if (configUSE_CORE_AFFINITY == 1) && (configNUMBER_OF_CORES > 1)
  return static_cast<int32_t>(task.uxCoreAffinityMask);
#else
  return 0;
#endif
}

inline void insert_top_task(TaskRuntimeRow *top, size_t top_count, const TaskRuntimeRow &row) {
  for (size_t i = 0; i < top_count; i++) {
    if (row.delta <= top[i].delta) {
      continue;
    }
    for (size_t j = top_count - 1; j > i; j--) {
      top[j] = top[j - 1];
    }
    top[i] = row;
    break;
  }
}

inline void log_task_runtime_profile() {
#if configGENERATE_RUN_TIME_STATS
  static constexpr UBaseType_t MAX_TASKS = 64;
  static constexpr size_t TOP_TASKS = 10;
  static TaskStatus_t tasks[MAX_TASKS];
  static TaskRuntimePrev previous[MAX_TASKS];
  static bool initialized = false;

  configRUN_TIME_COUNTER_TYPE total_runtime = 0;
  const UBaseType_t count = uxTaskGetSystemState(tasks, MAX_TASKS, &total_runtime);
  if (count == 0) {
    ESP_LOGW(TASK_PROF_TAG, "task profile unavailable: no task stats");
    return;
  }

  uint64_t sum_delta = 0;
  uint64_t idle_delta = 0;
  TaskRuntimeRow top[TOP_TASKS];

  for (UBaseType_t i = 0; i < count; i++) {
    const UBaseType_t number = tasks[i].xTaskNumber;
    const uint64_t runtime = static_cast<uint64_t>(tasks[i].ulRunTimeCounter);
    uint64_t last_runtime = runtime;
    bool found = false;

    for (auto &prev : previous) {
      if (prev.valid && prev.number == number) {
        last_runtime = prev.runtime;
        prev.runtime = runtime;
        found = true;
        break;
      }
    }

    if (!found) {
      for (auto &prev : previous) {
        if (!prev.valid) {
          prev.number = number;
          prev.runtime = runtime;
          prev.valid = true;
          break;
        }
      }
    }

    if (!initialized) {
      continue;
    }

    const uint64_t delta = runtime >= last_runtime ? runtime - last_runtime : 0;
    sum_delta += delta;
    if (task_is_idle(tasks[i].pcTaskName)) {
      idle_delta += delta;
    }

    TaskRuntimeRow row;
    row.name = tasks[i].pcTaskName;
    row.delta = delta;
    row.priority = tasks[i].uxCurrentPriority;
    row.stack_watermark = static_cast<uint32_t>(tasks[i].usStackHighWaterMark);
    row.core = task_core_id(tasks[i]);
    row.state = tasks[i].eCurrentState;
    insert_top_task(top, TOP_TASKS, row);
  }

  if (!initialized) {
    initialized = true;
    ESP_LOGW(TASK_PROF_TAG, "task profiler initialized tasks=%u total_runtime=%llu", static_cast<unsigned>(count),
             static_cast<unsigned long long>(total_runtime));
    return;
  }

  if (sum_delta == 0) {
    ESP_LOGW(TASK_PROF_TAG, "task profile empty delta tasks=%u total_runtime=%llu", static_cast<unsigned>(count),
             static_cast<unsigned long long>(total_runtime));
    return;
  }

  const uint32_t busy_x10 = static_cast<uint32_t>(((sum_delta - idle_delta) * 1000ULL) / sum_delta);
  const uint32_t idle_x10 = static_cast<uint32_t>((idle_delta * 1000ULL) / sum_delta);
  ESP_LOGW(TASK_PROF_TAG,
           "task profile: busy=%u.%u%% idle=%u.%u%% tasks=%u internal=%uKiB psram=%uKiB",
           busy_x10 / 10, busy_x10 % 10, idle_x10 / 10, idle_x10 % 10,
           static_cast<unsigned>(count), static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_INTERNAL) / 1024),
           static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_SPIRAM) / 1024));

  for (size_t i = 0; i < TOP_TASKS && top[i].delta > 0; i++) {
    const uint32_t pct_x10 = static_cast<uint32_t>((top[i].delta * 1000ULL) / sum_delta);
    ESP_LOGW(TASK_PROF_TAG, "  #%u %s %u.%u%% core=%d prio=%u stack=%u state=%s",
             static_cast<unsigned>(i + 1), top[i].name == nullptr ? "<null>" : top[i].name, pct_x10 / 10,
             pct_x10 % 10, static_cast<int>(top[i].core), static_cast<unsigned>(top[i].priority),
             static_cast<unsigned>(top[i].stack_watermark), task_state_name(top[i].state));
  }
#else
  ESP_LOGW(TASK_PROF_TAG, "task profiler disabled: enable CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS");
#endif
}

}  // namespace atmosfera_diag
