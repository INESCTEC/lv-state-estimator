"""Pydantic models for historical grid measurement data."""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class Measurement(BaseModel):
    """Represents a single timestamped measurement.

    Attributes:
        timestamp (datetime): Timestamp of the measurement.
        v_measured (float): Measured voltage value.
        p_measured (float): Measured power value.
        exogenous (float): Exogenous variable or input relevant to the measurement.
    """

    timestamp: datetime
    v_measured: float
    p_measured: float
    exogenous: float


class HistoricalEntry(BaseModel):
    """Represents historical data for a specific meter.

    Attributes:
        meter_id (str): Identifier of the meter.
        info (int): Additional information or type code for the meter.
        measurements (List[Measurement]): List of timestamped measurements.
    """

    meter_id: str
    info: int
    measurements: List[Measurement]


class HistoricalGridData(BaseModel):
    """Represents historical measurement data for a grid.

    Attributes:
        grid_id (str): Identifier of the grid.
        p_units (str): Unit of power measurements (e.g., "kW").
        v_units (str): Unit of voltage measurements (e.g., "V").
        historical (List[HistoricalEntry]): List of historical data entries for meters in the grid.
    """

    grid_id: str
    p_units: str
    v_units: str
    historical: List[HistoricalEntry]
