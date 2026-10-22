import logging
import os

import snowflake.connector

from read_bookings import (
    BOOKINGS_FILE,
    read_bookings,
    validate_booking,
    deduplicate_bookings,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def merge_bookings():
    """Validate bookings and upsert them into Snowflake."""

    # Step 1: Read bookings from CSV
    bookings = read_bookings(BOOKINGS_FILE)

    valid_bookings = []
    invalid_bookings = []

    # Step 2: Validate individual bookings
    for booking in bookings:
        errors = validate_booking(booking)

        if errors:
            invalid_bookings.append({
                "booking": booking,
                "errors": errors,
            })
        else:
            valid_bookings.append(booking)

    # Step 3: Remove exact duplicates and reject conflicts
    valid_bookings, duplicates_removed = deduplicate_bookings(
        valid_bookings
    )

    if duplicates_removed > 0:
        logger.warning(
            f"Removed {duplicates_removed} exact duplicate records"
        )

    logger.info(f"Valid bookings: {len(valid_bookings)}")
    logger.info(f"Invalid bookings: {len(invalid_bookings)}")

    # Log invalid bookings
    if invalid_bookings:
        for invalid in invalid_bookings:
            logger.warning(
                f"Booking {invalid['booking'].get('booking_id')}: "
                f"{invalid['errors']}"
            )

    # Stop if there are no valid records
    if not valid_bookings:
        raise ValueError("No valid bookings to merge")

    # Step 4: Connect to Snowflake
    connection = snowflake.connector.connect(
        account="ALXICVR-FX80316",
        user="RSAMUELS1",
        password=os.environ["DBT_SNOWFLAKE_PASSWORD"],
        role="DBT_ROLE",
        warehouse="ANALYTICS_ENGINEERING_WH",
        database="ANALYTICS_ENGINEERING_PORTFOLIO",
        schema="RAW",
        autocommit=False,
    )

    try:
        cursor = connection.cursor()

        try:
            # Step 5: Clear the previous incoming batch
            cursor.execute("DELETE FROM BOOKINGS_INCOMING")

            # Step 6: Prepare validated records
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

            # Step 7: Load the incoming batch
            cursor.executemany(
                """
                INSERT INTO BOOKINGS_INCOMING (
                    booking_id,
                    customer_id,
                    booking_date,
                    tour_name,
                    guests,
                    total_amount,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                records,
            )

            logger.info(f"Staged {len(records)} bookings")

            # Step 8: MERGE incoming records into destination
            cursor.execute(
                """
                MERGE INTO BOOKINGS_INGESTED AS target
                USING BOOKINGS_INCOMING AS source
                ON target.booking_id = source.booking_id

                WHEN MATCHED THEN UPDATE SET
                    target.customer_id = source.customer_id,
                    target.booking_date = source.booking_date,
                    target.tour_name = source.tour_name,
                    target.guests = source.guests,
                    target.total_amount = source.total_amount,
                    target.status = source.status

                WHEN NOT MATCHED THEN INSERT (
                    booking_id,
                    customer_id,
                    booking_date,
                    tour_name,
                    guests,
                    total_amount,
                    status
                )
                VALUES (
                    source.booking_id,
                    source.customer_id,
                    source.booking_date,
                    source.tour_name,
                    source.guests,
                    source.total_amount,
                    source.status
                )
                """
            )

            # Step 9: Commit the transaction
            connection.commit()
            logger.info("MERGE completed successfully")

        except Exception:
            connection.rollback()
            logger.exception("MERGE failed; transaction rolled back")
            raise

        finally:
            cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    merge_bookings()