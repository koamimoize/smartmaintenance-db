import sqlite3
from pathlib import Path

DB_PATH = Path("data/smartmaintenance.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS machines (
            machine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_name TEXT NOT NULL UNIQUE,
            machine_type TEXT NOT NULL,
            location TEXT,
            installation_date TEXT,
            status TEXT NOT NULL DEFAULT 'Operational'
        );

        CREATE TABLE IF NOT EXISTS failures (
            failure_id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id INTEGER NOT NULL,
            failure_date TEXT NOT NULL,
            failure_type TEXT NOT NULL,
            description TEXT,
            downtime_hours REAL NOT NULL DEFAULT 0,
            severity TEXT,
            FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
        );

        CREATE TABLE IF NOT EXISTS interventions (
            intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
            failure_id INTEGER NOT NULL,
            intervention_type TEXT NOT NULL,
            repair_duration_hours REAL,
            technician TEXT,
            labor_cost_eur REAL,
            status TEXT NOT NULL DEFAULT 'Completed',
            FOREIGN KEY (failure_id) REFERENCES failures(failure_id)
        );
        """)

def seed_demo_data():
    """Insert the illustrative dataset only when the machines table is empty."""
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        if count:
            return

        machines = [
            ("CNC-001", "CNC Machine", "Workshop A", "2022-05-10", "Operational"),
            ("PUMP-001", "Industrial Pump", "Workshop B", "2021-08-15", "Operational"),
            ("COMP-001", "Air Compressor", "Workshop A", "2023-01-20", "Operational"),
        ]
        conn.executemany("""
            INSERT INTO machines
            (machine_name, machine_type, location, installation_date, status)
            VALUES (?, ?, ?, ?, ?)
        """, machines)

        failures = [
            (1, "2026-10-01", "Mechanical", "Bearing wear", 4.5, "High"),
            (1, "2026-10-12", "Electrical", "Motor overheating", 2.0, "Medium"),
            (3, "2026-10-05", "Mechanical", "Air leakage", 1.5, "Low"),
            (3, "2026-10-18", "Mechanical", "Compressor vibration", 3.0, "Medium"),
            (2, "2026-10-08", "Hydraulic", "Seal leakage", 5.0, "High"),
            (2, "2026-10-22", "Mechanical", "Pump overheating", 2.5, "Medium"),
        ]
        conn.executemany("""
            INSERT INTO failures
            (machine_id, failure_date, failure_type, description, downtime_hours, severity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, failures)
