"""Pydantic models for grid and meter configuration."""

from typing import List

from pydantic import BaseModel


class Meter(BaseModel):
    """Represents an electric meter associated with a grid.

    Attributes:
        meter_id (str): Unique identifier of the meter.
        meter_type (int): Type of meter.
        phase (int): Phase number the meter is connected to.
        info (int): Additional information or metadata about the meter.
        active (bool): Indicates whether the meter is active.
    """

    meter_id: str
    meter_type: int
    phase: int
    info: int
    active: bool


class GridData(BaseModel):
    """Represents a grid's configuration and its associated meters.

    Attributes:
        grid_id (str): Unique identifier of the grid.
        p_units (str): Unit for power measurements (e.g., "kW").
        v_units (str): Unit for voltage measurements (e.g., "V").
        estimation_type (int): Type of state estimation method used.
        resolution (int): Time resolution of the measurements (e.g., in 15/30 minutes).
        meters (List[Meter]): List of meters associated with the grid.
    """

    grid_id: str
    p_units: str
    v_units: str
    estimation_type: int
    resolution: int
    meters: List[Meter]
