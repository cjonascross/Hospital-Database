
import subprocess
import sys
from pathlib import Path

import mysql.connector
from mysql.connector import Error as MySQLError

import gui

HERE = Path(__file__).resolve().parent


def tables_exist():
    """Return True if hospital_db already has all of its tables."""
    config = {k: v for k, v in gui.DB_CONFIG.items() if k != "database"}
    conn = mysql.connector.connect(**config)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s",
            (gui.DB_CONFIG["database"],),
        )
        count = cursor.fetchone()[0]
        cursor.close()
    finally:
        conn.close()
    return count >= 9


def run_script(name):
    """Run one of the setup scripts with the same Python interpreter."""
    print(f"Running {name}...")
    result = subprocess.run([sys.executable, str(HERE / name)], cwd=HERE)
    if result.returncode != 0:
        sys.exit(f"{name} failed (exit code {result.returncode}).")


def main():
    try:
        if tables_exist():
            print("Tables already exist, skipping Create_Tables.py.")
        else:
            run_script("Create_Tables.py")
    except MySQLError as exc:
        sys.exit(f"Could not connect to MySQL: {exc}\n"
                 "Make sure the MySQL server is running and the root password "
                 "matches DB_CONFIG in gui.py.")

    run_script("Insert_Data.py")

    print("Starting GUI...")
    gui.main()


if __name__ == "__main__":
    main()
