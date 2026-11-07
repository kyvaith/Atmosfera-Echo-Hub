"""Simulation-only binary_sensor platform."""

from .entities import demo_platform

async_setup_entry = demo_platform("binary_sensor")
