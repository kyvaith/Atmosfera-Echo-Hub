"""Constants for the Atmosfera Echo Hub integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "atmosfera_echo_hub"

CONF_CAMERAS = "cameras"
CONF_DEVICE_ID = "device_id"
CONF_STREAM_FPS = "stream_fps"
CONF_STREAM_HEIGHT = "stream_height"
CONF_STREAM_WIDTH = "stream_width"

DEFAULT_STREAM_FPS = 10
DEFAULT_STREAM_HEIGHT = 800
DEFAULT_STREAM_WIDTH = 800
MAX_STREAM_FPS = 15
MIN_STREAM_FPS = 1

API_ACTION_SELECT_SOURCE = "camera_select_source"
API_ACTION_SET_SOURCES = "camera_set_sources"

SERVICE_REPORT_CAMERA_SOURCE = "report_camera_source"
ATTR_NODE_NAME = "node_name"
ATTR_SOURCE = "source"

PLATFORMS = [Platform.SELECT]
TOKEN_REFRESH_INTERVAL = timedelta(minutes=4)
RETRY_INTERVAL_SECONDS = 15
