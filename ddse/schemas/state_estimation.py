"""Pydantic models for state estimation input and prediction output."""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class StateEstimationMeasurement(BaseModel):
    """Represents a single measurement used in state estimation.

    Attributes:
        timestamp (datetime): Timestamp of the measurement.
        v_measured (float): Measured voltage value.
        p_measured (float): Measured power value.
        exogenous (float): Exogenous input or influencing variable.
    """

    timestamp: datetime
    v_measured: float
    p_measured: float
    exogenous: float


class StateEstimationEntry(BaseModel):
    """Represents the state estimation data for a specific meter.

    Attributes:
        meter_id (str): Identifier of the meter.
        info (int): Additional information or type code.
        measurements (List[StateEstimationMeasurement]): List of measurements for this meter.
    """

    meter_id: str
    info: int
    measurements: List[StateEstimationMeasurement]


class StateEstimationData(BaseModel):
    """Represents a full set of state estimation data for a grid.

    Attributes:
        grid_id (str): Identifier of the grid.
        p_units (str): Unit for power values (e.g., "kW").
        v_units (str): Unit for voltage values (e.g., "V").
        historical (List[StateEstimationEntry]): State estimation entries for each meter.
    """

    grid_id: str
    p_units: str
    v_units: str
    historical: List[StateEstimationEntry]


class PredictedVoltage(BaseModel):
    """Represents a predicted voltage value for a meter.

    Attributes:
        meter_id (str): Identifier of the meter.
        v_predicted (float): Predicted voltage value.
    """

    meter_id: str
    v_predicted: float


class PredictionResponse(BaseModel):
    """Represents the response containing all predicted voltages.

    Attributes:
        predictions (List[PredictedVoltage]): List of voltage predictions per meter.
    """

    predictions: List[PredictedVoltage]
