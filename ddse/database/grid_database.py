from ddse.schemas import GridData


def init_grid_db(cursor):
    """Initializes the database schema for grid and meter configuration.

    This function creates the `grids` and `meters` tables if they do not already exist.
    - The `grids` table stores metadata for each electrical grid.
    - The `meters` table stores metadata for each meter and is linked to a grid via `grid_id`.

    Args:
        cursor (sqlite3.Cursor): A SQLite cursor object used to execute SQL commands.
    """

    # Create grid table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS grids (
            grid_id TEXT PRIMARY KEY,
            p_units TEXT,
            v_units TEXT,
            estimation_type INTEGER,
            resolution INTEGER
        )
    """
    )

    # Create meters table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meters (
            meter_id TEXT,
            meter_type INTEGER,
            phase INTEGER,
            info INTEGER,
            active BOOLEAN,
            grid_id TEXT,
            FOREIGN KEY(grid_id) REFERENCES grids(grid_id)
            PRIMARY KEY (meter_id, grid_id)
        )
    """
    )


def insert_grid_data(cursor, data: GridData):
    """Inserts grid and meter data into the database.

    Args:
        cursor (sqlite3.Cursor): Cursor connected to the database.
        data (GridData): Parsed grid data with meters.
    """
    # Inserir ou actualizar a grelha
    cursor.execute(
        """
        INSERT OR REPLACE INTO grids (grid_id, p_units, v_units, estimation_type, resolution)
        VALUES (?, ?, ?, ?, ?)
        """,
        (data.grid_id, data.p_units, data.v_units, data.estimation_type, data.resolution),
    )

    # Apagar meters antigos da mesma grelha (opcional)
    cursor.execute("DELETE FROM meters WHERE grid_id = ?", (data.grid_id,))

    # Inserir novos meters
    for meter in data.meters:
        cursor.execute(
            """
            INSERT INTO meters (meter_id, meter_type, phase, info, active, grid_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                meter.meter_id,
                meter.meter_type,
                meter.phase,
                meter.info,
                int(meter.active),  # SQLite usa INTEGER para booleanos
                data.grid_id,
            ),
        )
