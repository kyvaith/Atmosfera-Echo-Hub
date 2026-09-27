"""Display-oriented MJPEG proxy for Home Assistant camera entities."""

from __future__ import annotations

import asyncio
from io import BytesIO
import logging
import shlex
import shutil

from aiohttp import web
from haffmpeg.camera import CameraMjpeg
from PIL import Image as PilImage, ImageOps, UnidentifiedImageError

from homeassistant.components.camera import Camera, async_get_image, async_get_still_stream
from homeassistant.components.camera.helper import get_camera_from_entity_id
from homeassistant.components.ffmpeg import get_ffmpeg_manager
from homeassistant.components.http import KEY_AUTHENTICATED, HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DEFAULT_STREAM_FPS,
    DEFAULT_STREAM_HEIGHT,
    DEFAULT_STREAM_WIDTH,
    MAX_STREAM_FPS,
    MIN_STREAM_FPS,
)

_LOGGER = logging.getLogger(__name__)

_JPEG_QUALITY = 82
_FFMPEG_JPEG_QSCALE = 7


def _bounded_query_int(
    request: web.Request, key: str, default: int, minimum: int, maximum: int
) -> int:
    """Read and clamp one integer query parameter."""
    try:
        value = int(request.query.get(key, default))
    except (TypeError, ValueError):
        value = default
    return min(maximum, max(minimum, value))


def _normalize_jpeg_frame(frame: bytes, width: int, height: int) -> bytes | None:
    """Center-crop a camera frame into one native-size baseline JPEG."""
    try:
        with PilImage.open(BytesIO(frame)) as source:
            source_format = source.format
            source = ImageOps.exif_transpose(source)
            if source_format == "JPEG" and source.size == (width, height):
                return frame
            if source.mode != "RGB":
                source = source.convert("RGB")
            fitted = ImageOps.fit(
                source,
                (width, height),
                method=PilImage.Resampling.BILINEAR,
                centering=(0.5, 0.5),
            )
            output = BytesIO()
            fitted.save(
                output,
                format="JPEG",
                quality=_JPEG_QUALITY,
                optimize=False,
                progressive=False,
                subsampling=2,
            )
            return output.getvalue()
    except (OSError, UnidentifiedImageError, ValueError):
        return None


class AtmosferaCameraStreamView(HomeAssistantView):
    """Serve selected HA cameras as native-size MJPEG for the display."""

    url = "/api/atmosfera_echo_hub/camera_stream/{entity_id}"
    name = "api:atmosfera_echo_hub:camera_stream"
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the camera stream proxy."""
        self.hass = hass

    async def get(self, request: web.Request, entity_id: str) -> web.StreamResponse:
        """Return a bounded, hardware-decoder-friendly MJPEG stream."""
        try:
            camera = get_camera_from_entity_id(self.hass, entity_id)
        except HomeAssistantError as err:
            raise web.HTTPNotFound from err

        authenticated = request[KEY_AUTHENTICATED] or request.query.get(
            "token"
        ) in camera.access_tokens
        if not authenticated:
            raise web.HTTPForbidden
        if not camera.is_on:
            raise web.HTTPServiceUnavailable

        width = _bounded_query_int(
            request, "width", DEFAULT_STREAM_WIDTH, 160, 1920
        )
        height = _bounded_query_int(
            request, "height", DEFAULT_STREAM_HEIGHT, 160, 1920
        )
        fps = _bounded_query_int(
            request,
            "fps",
            DEFAULT_STREAM_FPS,
            MIN_STREAM_FPS,
            MAX_STREAM_FPS,
        )

        try:
            stream_source = await camera.stream_source()
        except HomeAssistantError:
            stream_source = None
        if stream_source:
            manager = get_ffmpeg_manager(self.hass)
            if shutil.which(manager.binary) is None:
                _LOGGER.debug(
                    "FFmpeg binary %s is unavailable; using still frames for %s",
                    manager.binary,
                    entity_id,
                )
                stream_source = None

        if stream_source:
            stream = CameraMjpeg(manager.binary)
            input_source = stream_source
            source_lower = stream_source.lower()
            pace_hls_output = False
            if source_lower.startswith(("rtsp://", "rtsps://")):
                input_source = (
                    "-rtsp_transport tcp -i " + shlex.quote(stream_source)
                )
            elif source_lower.startswith(("http://", "https://")) and ".m3u8" in source_lower:
                # Let the demux thread prefetch the next HLS segment while the
                # video filter paces completed frames. Input-side -re blocks
                # segment prefetch and exposes each CDN boundary as a visible
                # 300-700 ms pause on the display.
                input_source = (
                    "-thread_queue_size 1024 -i " + shlex.quote(stream_source)
                )
                pace_hls_output = True
                _LOGGER.debug(
                    "Applying buffered output pacing to HLS camera %s", entity_id
                )
            video_filter = (
                f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height}"
            )
            if pace_hls_output:
                video_filter += ",realtime=limit=2:speed=1"
            opened = await stream.open_camera(
                input_source,
                extra_cmd=(
                    f"-vf {shlex.quote(video_filter)} -r {fps} "
                    f"-pix_fmt yuvj420p -q:v {_FFMPEG_JPEG_QSCALE}"
                ),
            )
            if opened:
                try:
                    stream_reader = await stream.get_reader()
                    try:
                        # HLS sources commonly need one segment before FFmpeg
                        # can emit its first MJPEG frame. Five seconds was on
                        # the boundary for the public aquarium stream and sent
                        # otherwise healthy streams through every slow
                        # fallback. Keep this below the device-side HTTP
                        # timeout, but leave enough margin for one cold start.
                        async with asyncio.timeout(12):
                            first_chunk = await stream_reader.read(8192)
                    except TimeoutError:
                        first_chunk = b""
                    if first_chunk:
                        response = web.StreamResponse(
                            headers={
                                "Cache-Control": "no-store",
                                "Content-Type": manager.ffmpeg_stream_content_type,
                            }
                        )
                        await response.prepare(request)
                        try:
                            await response.write(first_chunk)
                            while chunk := await stream_reader.read(65536):
                                await response.write(chunk)
                        except (BrokenPipeError, ConnectionResetError):
                            pass
                        return response
                    _LOGGER.debug(
                        "Native stream for %s produced no MJPEG data; using stills",
                        entity_id,
                    )
                finally:
                    await stream.close()

        last_source: bytes | None = None
        last_frame: bytes | None = None

        async def next_frame() -> bytes | None:
            nonlocal last_frame, last_source
            try:
                camera_image = await async_get_image(
                    self.hass,
                    entity_id,
                    timeout=5,
                    width=width,
                    height=height,
                )
            except HomeAssistantError:
                return last_frame

            source = camera_image.content
            if source == last_source and last_frame is not None:
                return last_frame
            normalized = await self.hass.async_add_executor_job(
                _normalize_jpeg_frame, source, width, height
            )
            if normalized is None:
                _LOGGER.debug("Unable to normalize frame from %s", entity_id)
                return last_frame
            last_source = source
            last_frame = normalized
            return normalized

        # Still-image cameras are normalized server-side as well. Do not
        # commit a successful response until one complete JPEG exists.
        for _attempt in range(3):
            if await next_frame() is not None:
                break
            await asyncio.sleep(0.2)

        if last_frame is None:
            # Preserve compatibility with integrations that expose only a
            # custom MJPEG handler. This last-resort path cannot guarantee the
            # requested geometry, so it deliberately comes after both native
            # size normalization paths above.
            if (
                type(camera).handle_async_mjpeg_stream
                is not Camera.handle_async_mjpeg_stream
            ):
                response = await camera.handle_async_mjpeg_stream(request)
                if response is not None:
                    return response
            raise web.HTTPBadGateway

        first_frame = last_frame

        async def stream_frame() -> bytes | None:
            nonlocal first_frame
            if first_frame is not None:
                frame = first_frame
                first_frame = None
                return frame
            return await next_frame()

        return await async_get_still_stream(
            request,
            stream_frame,
            "image/jpeg",
            1.0 / fps,
        )
