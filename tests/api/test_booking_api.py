# tests/api/test_booking_api.py
import pytest
from jsonschema import ValidationError, validate

from src.utils.data_generator import fake  # Assuming you have Faker
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Schema for a booking object (adjust based on Restful-booker's actual response)
BOOKING_SCHEMA = {
    "type": "object",
    "properties": {
        "firstname": {"type": "string"},
        "lastname": {"type": "string"},
        "totalprice": {"type": "integer"},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "properties": {
                "checkin": {"type": "string", "format": "date"},
                "checkout": {"type": "string", "format": "date"},
            },
            "required": ["checkin", "checkout"],
        },
        "additionalneeds": {"type": "string", "nullable": True},  # Allow null or string
    },
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
}

# Schema for the POST response which includes bookingid
CREATED_BOOKING_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"bookingid": {"type": "integer"}, "booking": BOOKING_SCHEMA},
    "required": ["bookingid", "booking"],
}

# Store created booking ID for cleanup or dependent tests
created_booking_ids = []


@pytest.fixture(scope="module", autouse=True)
def api_auth(booking_service_client):
    """Ensure authentication happens once per module for this test class if needed by multiple tests."""
    if not booking_service_client.auth_token:
        logger.info("Authenticating API client for Booking API tests module...")
        if not booking_service_client.authenticate():
            pytest.skip("API Authentication failed. Skipping tests that require auth.")


@pytest.mark.api
@pytest.mark.regression
class TestBookingAPI:

    def test_health_check(self, booking_service_client):
        logger.info("Starting test_health_check (ping)")
        response = booking_service_client.health_check()
        assert response.status_code == 201, f"Health check failed. Expected 201, got {response.status_code}"
        assert (
            response.text == "Created"
        ), "Health check response text mismatch"  # Ping returns "Created" with 201
        logger.info("test_health_check successful.")

    @pytest.mark.smoke
    def test_create_booking(self, booking_service_client):
        logger.info("Starting test_create_booking")
        booking_payload = {
            "firstname": fake.first_name(),
            "lastname": fake.last_name(),
            "totalprice": fake.random_int(min=50, max=1000),
            "depositpaid": fake.boolean(),
            "bookingdates": {
                "checkin": fake.date_between(start_date="-1y", end_date="today").strftime("%Y-%m-%d"),
                "checkout": fake.date_between(start_date="today", end_date="+1y").strftime("%Y-%m-%d"),
            },
            "additionalneeds": "Breakfast",
        }
        response = booking_service_client.create_booking(booking_payload)
        assert (
            response.status_code == 200
        ), f"Expected 200 for create booking, got {response.status_code}. Response: {response.text}"

        created_booking_data = response.json()
        try:
            validate(instance=created_booking_data, schema=CREATED_BOOKING_RESPONSE_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"Create booking response schema validation failed: {e.message}")

        assert created_booking_data["booking"]["firstname"] == booking_payload["firstname"]
        booking_id = created_booking_data.get("bookingid")
        assert booking_id is not None
        created_booking_ids.append(booking_id)  # Store for potential cleanup
        logger.info(f"test_create_booking successful. Booking ID: {booking_id}")
        return booking_id  # Return for dependent tests

    def test_get_booking_details(self, booking_service_client):
        logger.info("Starting test_get_booking_details")
        if not created_booking_ids:
            pytest.skip(
                "No booking created in this session to fetch details for. Run create_booking first or use a known ID."
            )

        booking_id_to_fetch = created_booking_ids[-1]  # Get the last created one

        response = booking_service_client.get_booking_details(booking_id_to_fetch)
        assert (
            response.status_code == 200
        ), f"Expected 200 for get booking, got {response.status_code}. Response: {response.text}"

        booking_details = response.json()
        # GET /booking/{id} returns the booking object directly, not nested under "booking"
        try:
            validate(instance=booking_details, schema=BOOKING_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"Get booking details response schema validation failed: {e.message}")

        assert "firstname" in booking_details  # Basic check
        logger.info(f"test_get_booking_details for ID {booking_id_to_fetch} successful.")

    def test_update_booking(self, booking_service_client):
        logger.info("Starting test_update_booking")
        if not created_booking_ids:
            pytest.skip("No booking created to update. Run create_booking first.")

        booking_id_to_update = created_booking_ids[-1]

        update_payload = {
            "firstname": "UpdatedName",
            "lastname": fake.last_name(),
            "totalprice": fake.random_int(min=100, max=200),
            "depositpaid": True,
            "bookingdates": {  # Restful-booker needs the full bookingdates object for PUT
                "checkin": fake.date_between(start_date="-1y", end_date="today").strftime("%Y-%m-%d"),
                "checkout": fake.date_between(start_date="today", end_date="+1y").strftime("%Y-%m-%d"),
            },
            "additionalneeds": "Late checkout",
        }
        response = booking_service_client.update_booking(booking_id_to_update, update_payload)
        assert (
            response.status_code == 200
        ), f"Expected 200 for update, got {response.status_code}. Response: {response.text}"
        updated_data = response.json()
        assert updated_data["firstname"] == "UpdatedName"
        assert updated_data["additionalneeds"] == "Late checkout"
        logger.info(f"test_update_booking for ID {booking_id_to_update} successful.")

    # Add test_delete_booking, test_get_booking_ids, test_partial_update_booking
    # Remember DELETE needs auth too.

    # Example of how you might structure a delete test (ideally runs last or uses unique data)
    @pytest.mark.run(order=-1)  # Pytest-order marker, run last
    def test_delete_created_booking(self, booking_service_client):
        logger.info("Starting test_delete_created_booking")
        if not created_booking_ids:
            pytest.skip("No booking ID stored from creation to delete.")

        booking_id_to_delete = created_booking_ids.pop()  # Get and remove from list

        response = booking_service_client.delete_booking(booking_id_to_delete)
        # Restful-booker DELETE returns 201 Created (odd, but it's their spec)
        assert (
            response.status_code == 201
        ), f"Expected 201 for delete, got {response.status_code}. Response: {response.text}"

        # Verify deletion by trying to GET it (should be 404)
        get_response = booking_service_client.get_booking_details(booking_id_to_delete)
        assert get_response.status_code == 404, "Booking should be 404 Not Found after deletion."
        logger.info(f"test_delete_created_booking for ID {booking_id_to_delete} successful.")


# If you want to clean up all created bookings at the end of the session:
# def pytest_sessionfinish(session):
#    if created_booking_ids:
#        logger.info(f"Cleaning up {len(created_booking_ids)} created bookings...")
#        # Need a booking_service_client instance here.
#        # This is tricky as fixtures aren't directly available in sessionfinish.
#        # One way is to instantiate it directly if config is accessible globally or re-parsed.
#        # Or, rely on test-specific cleanup.
#        # For a demo, showing one delete test is often sufficient.
