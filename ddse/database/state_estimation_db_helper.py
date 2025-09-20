import sqlite3
from datetime import datetime
from typing import Dict, List

import numpy as np

import ddse.schemas.state_estimation as sc


def get_all_grid_meter_ids(conn, grid_id: str) -> set:
    """Fetches all meter IDs associated with a specific grid.

    Args:
        conn (sqlite3.Connection): Active database connection.
        grid_id (str): Identifier of the grid.

    Returns:
        set: A set of meter IDs belonging to the given grid.
    """
    cur = conn.cursor()
    cur.execute("SELECT meter_id FROM meters WHERE grid_id = ?", (grid_id,))
    return {row["meter_id"] for row in cur.fetchall()}


def get_all_voltage_measurements(conn, meter_ids: List[str]):
    """Retrieves voltage measurements for a list of meter IDs.

    Args:
        conn (sqlite3.Connection): Active database connection.
        meter_ids (List[str]): List of meter IDs to fetch measurements for.

    Returns:
        List[sqlite3.Row]: Rows containing meter_id, timestamp, and v_measured.
    """
    placeholders = ",".join(["?"] * len(meter_ids))
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT meter_id, timestamp, v_measured
        FROM measurements
        WHERE meter_id IN ({placeholders})
        """,
        meter_ids,
    )
    return cur.fetchall()


def organize_measurements_by_meter(
    rows: List[sqlite3.Row],
) -> tuple[Dict[str, Dict[str, float]], List[str]]:
    """Organizes raw measurement rows by meter ID and extracts all unique timestamps.

    Args:
        rows (List[sqlite3.Row]): List of measurement rows from the database.

    Returns:
        tuple:
            Dict[str, Dict[str, float]]: Mapping of meter_id to timestamp-value pairs.
            List[str]: Sorted list of all unique timestamps.
    """
    meter_data: Dict[str, Dict[str, float]] = {}
    timestamps_set = set()

    for row in rows:
        meter = row["meter_id"]
        ts = row["timestamp"]
        v = row["v_measured"]
        timestamps_set.add(ts)
        if meter not in meter_data:
            meter_data[meter] = {}
        meter_data[meter][ts] = v

    sorted_timestamps = sorted(timestamps_set)
    return meter_data, sorted_timestamps


def build_voltage_matrix(
    meter_ids: List[str], meter_data: Dict[str, Dict[str, float]], timestamps: List[str]
):
    """Builds a voltage matrix aligned by timestamps and meter IDs.

    Args:
        meter_ids (List[str]): List of meter IDs to include in the matrix.
        meter_data (Dict[str, Dict[str, float]]): Voltage data organized by meter and timestamp.
        timestamps (List[str]): Sorted list of timestamps.

    Returns:
        np.ndarray: A 2D NumPy array of shape (meters × timestamps) with voltage values or None.
    """
    import numpy as np

    matrix = []
    for meter in meter_ids:
        row = [meter_data.get(meter, {}).get(ts, None) for ts in timestamps]
        matrix.append(row)
    return np.asarray(matrix)


def extract_input_voltages(data: sc.StateEstimationData) -> list:
    """Extracts the actual voltage values provided in the input data.

    Assumes each meter has only one measurement, and all timestamps are the same.

    Args:
        data (StateEstimationData): Input state estimation data.

    Returns:
        list: A list of voltage values (`v_measured`) for the included meters.
    """
    return np.asarray([entry.measurements[0].v_measured for entry in data.historical])


def get_excluded_voltages_at_timestamps(
    conn, excluded_ids: List[str], timestamps: List[datetime]
) -> np.ndarray:
    """Fetches historical voltage values for excluded meters at specific timestamps.

    Args:
        conn (sqlite3.Connection): Active database connection.
        excluded_ids (List[str]): Meter IDs that are excluded from the input.
        timestamps (List[datetime]): List of datetime objects representing the lookup instants.

    Returns:
        np.ndarray: A 2D NumPy array with shape (len(timestamps), len(excluded_ids)),
                    containing voltage values or None where data is missing.
    """

    cur = conn.cursor()
    matrix = []

    for ts in timestamps:
        ts_iso = ts.isoformat()
        placeholders = ",".join(["?"] * len(excluded_ids))
        cur.execute(
            f"""
            SELECT meter_id, v_measured
            FROM measurements
            WHERE meter_id IN ({placeholders}) AND timestamp = ?
            """,
            excluded_ids + [ts_iso],
        )
        results = {row["meter_id"]: row["v_measured"] for row in cur.fetchall()}
        matrix.append([results.get(meter, None) for meter in excluded_ids])

    return np.asarray(matrix)
