import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from datetime import date
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# File locations
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOKINGS_FILE = PROJECT_ROOT / "seeds" / "bookings.csv"


def read_bookings(file_path):
    """Read booking records from a CSV file."""

    with open(file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        bookings = list(reader)

    return bookings


def validate_booking(booking):
    """Validate required fields and data types."""

    errors = []

    # Validate booking ID
    if not booking.get("booking_id"):
        errors.append("Missing booking_id")

    # Validate guest count
    try:
        guests = int(booking["guests"])

        if guests <= 0:
            errors.append("Guest count must be greater than zero")

    except (ValueError, TypeError, KeyError):
        errors.append("Invalid guest count")

    # Validate booking amount
    try:
        amount = Decimal(booking["total_amount"])

        if not amount.is_finite():
            errors.append("Booking amount must be finite")
        elif amount < 0:
            errors.append("Booking amount cannot be negative")

    except (InvalidOperation, TypeError, KeyError):
        errors.append("Invalid booking amount")
    # Validate booking status
    valid_statuses = {"completed", "confirmed", "cancelled"}

    status = str(booking.get("status") or "").strip().lower()

    if status not in valid_statuses:
        errors.append(f"Invalid booking status: {status}")

    # Validate booking date
    try:
        booking_date = date.fromisoformat(booking["booking_date"])

    except (ValueError, TypeError, KeyError):
        errors.append("Invalid booking date")

    return errors

def deduplicate_bookings(bookings):
    """Remove exact duplicates and reject conflicting booking records."""

    unique_bookings = {}
    duplicates_removed = 0

    for booking in bookings:
        booking_id = booking["booking_id"]

        if booking_id not in unique_bookings:
            unique_bookings[booking_id] = booking

        elif unique_bookings[booking_id] == booking:
            duplicates_removed += 1

        else:
            raise ValueError(
                f"Conflicting records found for booking {booking_id}"
            )

    return list(unique_bookings.values()), duplicates_removed

if __name__ == "__main__":

    # Read the CSV
    bookings = read_bookings(BOOKINGS_FILE)

    logger.info(f"Loaded {len(bookings)} bookings")

    # Separate valid and invalid records
    valid_bookings = []
    invalid_bookings = []

    for booking in bookings:

        errors = validate_booking(booking)

        if errors:
            invalid_bookings.append({
                "booking": booking,
                "errors": errors
            })
        else:
            valid_bookings.append(booking)

    logger.info(f"Valid bookings: {len(valid_bookings)}")

    if len(invalid_bookings) == 0:
        logger.info("Validation successful: all bookings passed")

    elif len(valid_bookings) == 0:
        logger.error("Validation failed: no valid bookings found")

    else:
        logger.warning(
            f"Partial validation success: "
            f"{len(valid_bookings)} valid, "
            f"{len(invalid_bookings)} invalid"
        )

    # Print any validation errors
    for invalid in invalid_bookings:
        print(
            f"Booking {invalid['booking'].get('booking_id')}: "
            f"{invalid['errors']}"
        )