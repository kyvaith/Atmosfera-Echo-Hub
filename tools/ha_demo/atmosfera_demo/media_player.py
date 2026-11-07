"""Simulation-only media_player platform."""

from .entities import demo_platform

async_setup_entry = demo_platform("media_player")
