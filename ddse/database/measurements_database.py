"""Service logic for historical grid measurement databases."""

from ddse.schemas import HistoricalGridData


def init_measurements_db(cursor):
    """Initializes the database schema for storing measurement data.

    This function creates the `measurements` table if it does not already exist.
    Each record stores a timestamped voltage, power, and exogenous value
    associated with a meter.

    The table uses a composite primary key of `(meter_id, timestamp)` and enforces
    a foreign key constraint linking `meter_id` to the `meters` table.

    Args:
        cursor (sqlite3.Cursor): A SQLite cursor object used to execute SQL commands.
    """

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS measurements (
        meter_id TEXT,
        timestamp TEXT,
        v_measured REAL,
        p_measured REAL,
        exogenous REAL,
        PRIMARY KEY (meter_id, timestamp)
        FOREIGN KEY(meter_id) REFERENCES meters(meter_id)
    )
    """
    )


def insert_historical_measurements(cursor, data: HistoricalGridData):
    """Inserts historical measurements into the database.

    For each meter in the input, inserts all associated timestamped
    measurements into the `measurements` table.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        data (HistoricalGridData): Historical grid data containing multiple meters and measurements.
    """
    for entry in data.historical:
        for m in entry.measurements:
            cursor.execute(
                """
                INSERT INTO measurements (meter_id, timestamp, v_measured, p_measured, exogenous)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    entry.meter_id,
                    m.timestamp.isoformat(),
                    m.v_measured,
                    m.p_measured,
                    m.exogenous,
                ),
            )
