"""API router for saving historical grid measurements."""

import os
import sqlite3

from fastapi import APIRouter, HTTPException

from ddse.database import init_measurements_db, insert_historical_measurements
from ddse.schemas import HistoricalGridData

# Get database name from environment or use default
DB_NAME = os.environ.get("GRID_DB_NAME", "grid_data.db")

router = APIRouter()


@router.post("/historical")
def save_historical_data(data: HistoricalGridData):
    """Stores historical voltage, power and exogenous measurements in the database.

    This endpoint receives a list of meters with their historical measurements
    and inserts each (meter_id, timestamp, v_measured, p_measured, exogenous)
    record into the `measurements` table.

    Args:
        data (HistoricalGridData): The grid ID, units, and list of meter measurements.

    Returns:
        dict: A message confirming the successful insertion.

    Raises:
        HTTPException: If any error occurs during database interaction.
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            init_measurements_db(cursor)
            insert_historical_measurements(cursor, data)
            conn.commit()
        return {"message": "Historical grid data saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
