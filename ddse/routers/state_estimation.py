"""Endpoint for voltage prediction using state estimation data."""

import os
import sqlite3
from datetime import timedelta

from fastapi import APIRouter, HTTPException

import ddse.algorithm.beta_computation as bt
import ddse.schemas.state_estimation as sc
from ddse.database.state_estimation_db_helper import *

DB_NAME = os.environ.get("GRID_DB_NAME", "grid_data.db")

router = APIRouter()


def get_connection():
    """Establishes a connection to the SQLite database.

    Returns:
        sqlite3.Connection: SQLite connection object with row factory set.
    """

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@router.post("/voltages")
def get_voltage_measurements(data: sc.StateEstimationData):
    """Computes predicted voltages for meters not included in the input using historical state estimation.

    This endpoint performs the following:
    - Identifies included and excluded meters for the specified grid.
    - Retrieves all relevant voltage measurements from the database.
    - Constructs voltage matrices for included and excluded meters.
    - Computes beta coefficients using historical correlations.
    - Gathers previous-day, two-day, and one-week old voltages for excluded meters.
    - Applies the prediction model to estimate current voltages for excluded meters.
    - Returns a list of predicted voltage values per excluded meter.

    Args:
        data (StateEstimationData): State estimation input data, including grid ID and historical meter values.

    Returns:
        PredictionResponse: A list of predicted voltage values for excluded meters.

    Raises:
        HTTPException: If a database or processing error occurs.
    """

    try:
        input_meter_ids = {entry.meter_id for entry in data.historical}
        if not input_meter_ids:
            return sc.PredictionResponse(predictions=[])

        with get_connection() as conn:
            all_grid_meter_ids = get_all_grid_meter_ids(conn, data.grid_id)

        included_ids = sorted(input_meter_ids & all_grid_meter_ids)
        excluded_ids = sorted(all_grid_meter_ids - input_meter_ids)
        all_ids = included_ids + excluded_ids

        if not all_ids:
            return sc.PredictionResponse(predictions=[])

        with get_connection() as conn:
            raw_measurements = get_all_voltage_measurements(conn, all_ids)

        meter_data, sorted_timestamps = organize_measurements_by_meter(raw_measurements)

        included_voltages = build_voltage_matrix(included_ids, meter_data, sorted_timestamps)
        excluded_voltages = build_voltage_matrix(excluded_ids, meter_data, sorted_timestamps)

        daily_measurements = bt.number_daily_meas(bt.check_intervals(sorted_timestamps))
        beta_matr = bt.beta_pred(included_voltages, excluded_voltages, daily_measurements)

        ref_timestamp = data.historical[0].measurements[0].timestamp
        lookup_dates = [
            ref_timestamp - timedelta(days=1),
            ref_timestamp - timedelta(days=2),
            ref_timestamp - timedelta(days=7),
        ]

        with get_connection() as conn:
            excluded_previous_voltages = get_excluded_voltages_at_timestamps(
                conn, excluded_ids, lookup_dates
            )

        included_actual_voltages = extract_input_voltages(data)

        v_pred = bt.v_pred(excluded_previous_voltages, included_actual_voltages, beta_matr)

        result = [
            sc.PredictedVoltage(meter_id=m_id, v_predicted=pred)
            for m_id, pred in zip(excluded_ids, v_pred)
        ]

        return sc.PredictionResponse(predictions=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
