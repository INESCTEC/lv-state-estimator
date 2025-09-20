"""API router for creating grid database."""

import os
import sqlite3

from fastapi import APIRouter, HTTPException

from ddse.database import init_grid_db
from ddse.database.grid_database import init_grid_db, insert_grid_data
from ddse.schemas import GridData

# Get the database name from the environment variable, or use default
DB_NAME = os.environ.get("GRID_DB_NAME", "grid_data.db")

router = APIRouter()


@router.post("/grid")
def save_grid_data(data: GridData):
    """Saves grid configuration and associated meters to the database.

    This endpoint creates or updates a grid entry in the `grids` table,
    deletes any existing meters linked to that grid, and inserts the new list
    of meters into the `meters` table.

    Args:
        data (GridData): The grid configuration and list of meters to be stored.

    Returns:
        dict: A message confirming successful storage of the data.

    Raises:
        HTTPException: If an error occurs during database interaction.
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            init_grid_db(cursor)
            insert_grid_data(cursor, data)
            conn.commit()
        return {"message": "Grid data saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
