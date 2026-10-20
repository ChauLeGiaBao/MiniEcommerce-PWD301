
import os
import sys
import time

import pyodbc

from app import create_app
from app.extensions import db


DATABASE_NAME = "MiniEcommerceDB"


def connect_to_master():
    password = os.environ["MSSQL_SA_PASSWORD"]

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=db,1433;"
        "DATABASE=master;"
        "UID=sa;"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=5;"
    )

    for attempt in range(1, 61):
        try:
            connection = pyodbc.connect(
                connection_string,
                autocommit=True,
                timeout=5,
            )
            print("Connected to SQL Server.")
            return connection

        except pyodbc.Error as exc:
            print(
                f"Waiting for SQL Server "
                f"({attempt}/60): {exc.__class__.__name__}",
                flush=True,
            )
            time.sleep(2)

    raise RuntimeError(
        "Could not connect to SQL Server after 60 attempts."
    )


def create_database():
    connection = connect_to_master()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT DB_ID(?)",
            DATABASE_NAME,
        )

        existing = cursor.fetchone()[0]

        if existing is None:
            cursor.execute(
                f"CREATE DATABASE [{DATABASE_NAME}]"
            )
            print(f"Created database: {DATABASE_NAME}")
        else:
            print(f"Database already exists: {DATABASE_NAME}")

        cursor.close()
    finally:
        connection.close()


def create_tables():
    app = create_app()

    with app.app_context():
        if db.engine.dialect.name != "mssql":
            raise RuntimeError(
                "Bootstrap requires a SQL Server DATABASE_URL."
            )

        db.create_all()
        print("Database tables initialized successfully.")


if __name__ == "__main__":
    try:
        create_database()
        create_tables()
        print("Database bootstrap completed.")
    except Exception as error:
        print(f"Bootstrap failed: {error}", file=sys.stderr)
        sys.exit(1)
