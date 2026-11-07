"""Simulation-only camera platform."""

from .entities import demo_platform

async_setup_entry = demo_platform("camera")
