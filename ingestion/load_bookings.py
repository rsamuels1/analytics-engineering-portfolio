import logging
import os

import snowflake.connector

from read_bookings import (
    BOOKINGS_FILE,
    read_bookings,
    validate_booking,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def load_bookings():
    """Validate bookings and load them into Snowflake."""

    bookings = read_bookings(BOOKINGS_FILE)

    valid_bookings = []
    invalid_bookings = []

    for booking in bookings:
        errors = validate_booking(booking)

        if errors:
            invalid_bookings.append({
                "booking": booking,
                "errors": errors,
            })
        else:
            valid_bookings.append(booking)

    logger.info(f"Valid bookings: {len(valid_bookings)}")
    logger.info(f"Invalid bookings: {len(invalid_bookings)}")

    if invalid_bookings:
        for invalid in invalid_bookings:
            logger.warning(
                f"Booking {invalid['booking'].get('booking_id')}: "
                f"{invalid['errors']}"
            )

    if not valid_bookings:
        logger.error("No valid bookings to load")
        return

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
            insert_sql = """
                INSERT INTO BOOKINGS_INGESTED (
                    booking_id,
                    customer_id,
                    booking_date,
                    tour_name,
                    guests,
                    total_amount,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            records = [
                (
                    booking["booking_id"],
                    booking["customer_id"],
                    booking["booking_date"],
                    booking["tour_name"],
                    int(booking["guests"]),
                    booking["total_amount"],
                    booking["status"],
                )
                for booking in valid_bookings
            ]

            cursor.executemany(insert_sql, records)

            logger.info(
                f"Successfully inserted {len(records)} bookings"
            )

        finally:
            cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    load_bookings()