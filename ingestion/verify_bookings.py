import os

import snowflake.connector


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
        cursor.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(DISTINCT booking_id) AS unique_bookings,
                SUM(total_amount) AS total_booking_value
            FROM BOOKINGS_INGESTED
        """)

        result = cursor.fetchone()

        print(f"Total rows: {result[0]}")
        print(f"Unique bookings: {result[1]}")
        print(f"Total booking value: ${result[2]}")

    finally:
        cursor.close()

finally:
    connection.close()