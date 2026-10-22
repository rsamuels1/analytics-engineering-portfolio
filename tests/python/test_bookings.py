import pytest

from ingestion.read_bookings import (
    deduplicate_bookings,
    validate_booking,
)


def test_exact_duplicates_are_removed():
    """Identical bookings should be deduplicated."""

    bookings = [
        {"booking_id": "B001", "status": "completed"},
        {"booking_id": "B001", "status": "completed"},
        {"booking_id": "B002", "status": "confirmed"},
    ]

    unique_bookings, duplicates_removed = deduplicate_bookings(bookings)

    assert len(unique_bookings) == 2
    assert duplicates_removed == 1


def test_conflicting_duplicates_are_rejected():
    """Conflicting bookings should raise an error."""

    bookings = [
        {"booking_id": "B001", "status": "confirmed"},
        {"booking_id": "B001", "status": "completed"},
    ]

    with pytest.raises(ValueError):
        deduplicate_bookings(bookings)

def test_negative_booking_amount_is_rejected():
    """Bookings with negative amounts should fail validation."""

    booking = {
        "booking_id": "B999",
        "customer_id": "C999",
        "booking_date": "2026-09-10",
        "tour_name": "Portland Bike Tour",
        "guests": "2",
        "total_amount": "-50.00",
        "status": "completed",
    }

    errors = validate_booking(booking)

    assert "Booking amount cannot be negative" in errors

def test_zero_guests_are_rejected():
    """Bookings must have at least one guest."""

    booking = {
        "booking_id": "B999",
        "customer_id": "C999",
        "booking_date": "2026-09-10",
        "tour_name": "Portland Bike Tour",
        "guests": "0",
        "total_amount": "180.00",
        "status": "completed",
    }

    errors = validate_booking(booking)

    print("Validation errors:", errors)

    assert any("guest" in error.lower() for error in errors)

def test_one_guest_is_accepted():
    """A booking with exactly one guest should be valid."""

    booking = {
        "booking_id": "B999",
        "customer_id": "C999",
        "booking_date": "2026-09-10",
        "tour_name": "Portland Bike Tour",
        "guests": "1",
        "total_amount": "90.00",
        "status": "completed",
    }

    errors = validate_booking(booking)

    assert errors == []

def test_zero_dollar_booking_is_accepted():
    """Complimentary bookings should pass validation."""

    booking = {
        "booking_id": "B999",
        "customer_id": "C999",
        "booking_date": "2026-09-10",
        "tour_name": "Complimentary Portland Bike Tour",
        "guests": "2",
        "total_amount": "0.00",
        "status": "completed",
    }

    errors = validate_booking(booking)

    assert errors == []

def test_negative_guests_are_rejected():
    """Bookings cannot have a negative guest count."""

    booking = {
        "booking_id": "B999",
        "customer_id": "C999",
        "booking_date": "2026-09-10",
        "tour_name": "Portland Bike Tour",
        "guests": "-2",
        "total_amount": "180.00",
        "status": "completed",
    }

    errors = validate_booking(booking)

    assert any("guest" in error.lower() for error in errors)

def test_fractional_guests_are_rejected():
    """Guest counts must be whole numbers."""

    booking = {
        "booking_id": "B999",
        "customer_id": "C999",
        "booking_date": "2026-09-10",
        "tour_name": "Portland Bike Tour",
        "guests": "2.5",
        "total_amount": "180.00",
        "status": "completed",
    }

    errors = validate_booking(booking)

    assert any("guest" in error.lower() for error in errors)