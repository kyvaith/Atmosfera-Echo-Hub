"""Simulation-only number platform."""

from .entities import demo_platform

async_setup_entry = demo_platform("number")
