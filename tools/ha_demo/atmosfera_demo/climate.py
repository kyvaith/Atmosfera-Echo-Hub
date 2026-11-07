"""Simulation-only climate platform."""

from .entities import demo_platform

async_setup_entry = demo_platform("climate")
