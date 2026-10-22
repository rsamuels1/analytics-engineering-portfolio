import os
import logging

import snowflake.connector


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def test_connection():
    """Connect to Snowflake and verify the current session."""

    password = os.environ.get("DBT_SNOWFLAKE_PASSWORD")

    if not password:
        raise ValueError(
            "DBT_SNOWFLAKE_PASSWORD environment variable is not set"
        )

    connection = snowflake.connector.connect(
        account="ALXICVR-FX80316",
        user="RSAMUELS1",
        password=password,
        role="DBT_ROLE",
        warehouse="ANALYTICS_ENGINEERING_WH",
        database="ANALYTICS_ENGINEERING_PORTFOLIO",
    )

    try:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    CURRENT_USER(),
                    CURRENT_ROLE(),
                    CURRENT_WAREHOUSE(),
                    CURRENT_DATABASE()
                """
            )

            result = cursor.fetchone()

            logger.info("Connected to Snowflake successfully")
            logger.info(f"User: {result[0]}")
            logger.info(f"Role: {result[1]}")
            logger.info(f"Warehouse: {result[2]}")
            logger.info(f"Database: {result[3]}")

        finally:
            cursor.close()

    finally:
        connection.close()
        logger.info("Snowflake connection closed")


if __name__ == "__main__":
    test_connection()