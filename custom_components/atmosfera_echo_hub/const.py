"""Constants for the Atmosfera Echo Hub integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "atmosfera_echo_hub"
EVENT_TILE_PRESS = f"{DOMAIN}_event"

CONF_CAMERAS = "cameras"
CONF_DEVICE_ID = "device_id"
CONF_STREAM_FPS = "stream_fps"
CONF_STREAM_HEIGHT = "stream_height"
CONF_STREAM_WIDTH = "stream_width"
CONF_TILES = "tiles"
CONF_LAYOUT = "home_layout"
CONF_ACCENT_COLOR = "accent_color"
DEFAULT_ACCENT_COLOR = "36BCF0"

DEFAULT_STREAM_FPS = 20
DEFAULT_STREAM_HEIGHT = 800
DEFAULT_STREAM_WIDTH = 800
MAX_STREAM_FPS = 24
MIN_STREAM_FPS = 1

API_ACTION_SELECT_SOURCE = "camera_select_source"
API_ACTION_SET_SOURCES = "camera_set_sources"
API_ACTION_SET_KEYED_SOURCES = "camera_set_sources_v2"
API_ACTION_DOORBELL_PREVIEW = "camera_doorbell_preview_v1"
SERVICE_DOORBELL_PREVIEW = "doorbell_preview"
API_ACTION_SET_TILES = "home_tiles_set_config"
API_ACTION_GET_TILE_STATUS = "home_tiles_get_status"
API_ACTION_GET_LIGHT_STATUS = "light_control_get_status"
API_ACTION_BIND_LIGHT = "light_control_bind"
API_ACTION_UPDATE_LIGHT = "light_control_update"
API_ACTION_GET_ENTITY_STATUS = "entity_control_get_status"
API_ACTION_GET_ENTITY_FEATURES = "entity_control_get_features"
API_ACTION_BIND_ENTITY_FEATURES = "entity_control_bind_features"
API_ACTION_GET_COVER_FEATURES = "entity_cover_get_features"
API_ACTION_BIND_COVER_FEATURES = "entity_cover_bind_features"
API_ACTION_BIND_ENTITY = "entity_control_bind"
API_ACTION_UPDATE_ENTITY = "entity_control_update"
API_ACTION_SHOW_NOTIFICATION = "notification_show"
API_ACTION_DISMISS_NOTIFICATION = "notification_dismiss"

SERVICE_REPORT_CAMERA_SOURCE = "report_camera_source"
SERVICE_REPORT_TILE_PRESS = "report_tile_press"
SERVICE_REPORT_TILE_CONTEXT_PRESS = "report_tile_context_press"
SERVICE_REPORT_LIGHT_CONTROL = "report_light_control"
SERVICE_REPORT_ENTITY_CONTROL = "report_entity_control"
ATTR_PAYLOAD = "payload"
ATTR_NODE_NAME = "node_name"
ATTR_SOURCE = "source"
ATTR_SLOT = "slot"
ATTR_CARD_ID = "card_id"
ATTR_REVISION = "revision"

PANEL_URL_PATH = "atmosfera-echo-hub"
PANEL_WEBCOMPONENT = "atmosfera-tile-editor"

PLATFORMS = [Platform.SELECT, Platform.NOTIFY, Platform.EVENT]
TOKEN_REFRESH_INTERVAL = timedelta(minutes=4)
RETRY_INTERVAL_SECONDS = 15

API_ACTION_GET_CHOICE_FEATURES = "entity_choice_get_features"
API_ACTION_BIND_CHOICE_FEATURES = "entity_choice_bind_features"

API_ACTION_GET_PANEL_FEATURES = "entity_panel_get_features"
API_ACTION_BIND_PANEL_FEATURES = "entity_panel_bind_features"
API_ACTION_GET_DETAIL_FEATURES = "entity_detail_get_features"
API_ACTION_BIND_DETAIL_FEATURES = "entity_detail_bind_features"
