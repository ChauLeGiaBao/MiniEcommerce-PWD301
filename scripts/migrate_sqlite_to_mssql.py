
"""
Migrate legacy SQLite data to Docker SQL Server.

Source:
    /tmp/legacy.db (read-only SQLite backup)

Target:
    MiniEcommerceDB (SQL Server)

Safety:
    - Never changes the original SQLite database.
    - Refuses to run if any target table contains data.
    - Preserves original IDs and password hashes.
    - Rolls back all inserts if any step fails.
"""

import os
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, insert, select

from app import create_app
from app.extensions import db
from app.models import (
    DanhMuc,
    SanPham,
    User,
    DonHang,
    ChiTietDonHang,
)


SOURCE_PATH = Path(
    os.getenv("LEGACY_SQLITE_PATH", "/tmp/legacy.db")
)

TABLES = [
    ("DANHMUC", DanhMuc),
    ("NGUOIDUNG", User),
    ("SANPHAM", SanPham),
    ("DONHANG", DonHang),
    ("CHITIETDONHANG", ChiTietDonHang),
]


def read_sqlite_data():
    if not SOURCE_PATH.is_file():
        raise FileNotFoundError(
            f"SQLite backup not found: {SOURCE_PATH}"
        )

    # Open the backup in read-only mode.
    uri = f"file:{SOURCE_PATH.as_posix()}?mode=ro"

    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row

    try:
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        if integrity != "ok":
            raise RuntimeError(
                f"SQLite integrity check failed: {integrity}"
            )

        data = {}

        for table_name, _ in TABLES:
            cursor = connection.execute(
                f'SELECT * FROM "{table_name}"'
            )

            data[table_name] = [
                dict(row) for row in cursor.fetchall()
            ]

            print(
                f"SQLite {table_name}: "
                f"{len(data[table_name])} rows"
            )

        if not data["SANPHAM"]:
            raise RuntimeError(
                "Source SQLite database has no products."
            )

        return data

    finally:
        connection.close()


def convert_value(column, value):
    if value is None:
        return None

    # Convert SQLite date strings into Python dates.
    if isinstance(column.type, db.Date):
        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        return date.fromisoformat(
            str(value).split(" ")[0]
        )

    # Convert monetary fields to Decimal.
    if isinstance(column.type, db.Numeric):
        return Decimal(str(value))

    return value


def prepare_record(model, source_row):
    record = {}

    for column in model.__table__.columns:
        column_name = column.name

        if column_name in source_row:
            record[column_name] = convert_value(
                column,
                source_row[column_name]
            )

    return record


def validate_target_database():
    engine = db.engine

    if engine.dialect.name != "mssql":
        raise RuntimeError(
            "Target database must be SQL Server."
        )

    if engine.url.database != "MiniEcommerceDB":
        raise RuntimeError(
            "Refusing to write to an unexpected database."
        )


def migrate(data):
    validate_target_database()

    # All inserts use one transaction.
    # On error, SQLAlchemy rolls back the transaction.
    with db.engine.begin() as connection:

        # Do not overwrite or mix with existing data.
        for table_name, model in TABLES:
            existing_count = connection.scalar(
                select(func.count()).select_from(
                    model.__table__
                )
            )

            if existing_count != 0:
                raise RuntimeError(
                    f"Target table {table_name} "
                    f"already has {existing_count} rows. "
                    "Migration cancelled without changes."
                )

        # Insert in foreign-key dependency order.
        for table_name, model in TABLES:
            rows = data[table_name]

            for source_row in rows:
                record = prepare_record(
                    model,
                    source_row
                )

                # SQL Server dialect handles IDENTITY_INSERT
                # when explicit identity values are supplied.
                connection.execute(
                    insert(model.__table__).values(
                        **record
                    )
                )

            print(
                f"Imported {table_name}: {len(rows)}"
            )

        # Verify counts before committing.
        for table_name, model in TABLES:
            actual_count = connection.scalar(
                select(func.count()).select_from(
                    model.__table__
                )
            )

            expected_count = len(
                data[table_name]
            )

            if actual_count != expected_count:
                raise RuntimeError(
                    f"Count mismatch in {table_name}: "
                    f"expected {expected_count}, "
                    f"found {actual_count}"
                )

    print("")
    print("MIGRATION SUCCESSFUL")
    print("All records imported and verified.")
    print("Original SQLite backup was not changed.")


def main():
    print("SQLite to SQL Server migration")
    print("--------------------------------")

    data = read_sqlite_data()

    app = create_app()

    with app.app_context():
        migrate(data)


if __name__ == "__main__":
    main()
