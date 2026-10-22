import logging
import os

import snowflake.connector


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def create_bookings_table():
    """Create the destination table for Python-ingested bookings."""

    connection = snowflake.connector.connect(
        account="ALXICVR-FX80316",
        user="RSAMUELS1",
        password=os.environ["DBT_SNOWFLAKE_PASSWORD"],
        role="DBT_ROLE",
        warehouse="ANALYTICS_ENGINEERING_WH",
        database="ANALYTICS_ENGINEERING_PORTFOLIO",
        schema="RAW",
    )

    try:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS BOOKINGS_INGESTED (
                    booking_id VARCHAR,
                    customer_id VARCHAR,
                    booking_date DATE,
                    tour_name VARCHAR,
                    guests INTEGER,
                    total_amount NUMBER(12, 2),
                    status VARCHAR,
                    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS BOOKINGS_INCOMING (
                    booking_id VARCHAR,
                    customer_id VARCHAR,
                    booking_date DATE,
                    tour_name VARCHAR,
                    guests INTEGER,
                    total_amount NUMBER(12, 2),
                    status VARCHAR
                )
                """
            )

            logger.info("BOOKINGS_INCOMING table is ready")
            logger.info("BOOKINGS_INGESTED table is ready")

        finally:
            cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    create_bookings_table()