# src/api_clients/booking_service.py
from requests import Response

from src.base.api_base import APIBase
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BookingService(APIBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.booking_endpoint = "/booking"

    # No need for a separate auth method here if APIBase handles it
    # def get_auth_token(self):
    #    return self.authenticate() # Calls APIBase.authenticate()

    def create_booking(self, booking_data: dict) -> Response:
        logger.info(f"Creating booking with data: {booking_data.get('firstname', 'N/A')}")
        # POST /booking does not require prior auth token for Restful-booker
        return self.post(self.booking_endpoint, json=booking_data, requires_auth=False)

    def get_booking_ids(self, filter_params: dict = None) -> Response:
        logger.info(f"Requesting all booking IDs with params: {filter_params}")
        return self.get(self.booking_endpoint, params=filter_params, requires_auth=False)

    def get_booking_details(self, booking_id: int) -> Response:
        logger.info(f"Requesting details for booking ID: {booking_id}")
        return self.get(f"{self.booking_endpoint}/{booking_id}", requires_auth=False)

    def update_booking(self, booking_id: int, booking_data: dict) -> Response:
        logger.info(f"Updating booking ID {booking_id}")
        if not self.auth_token:  # Ensure auth has happened
            self.authenticate()
        # PUT requires authentication (token)
        return self.put(f"{self.booking_endpoint}/{booking_id}", json=booking_data, requires_auth=True)

    def partial_update_booking(self, booking_id: int, booking_data: dict) -> Response:
        logger.info(f"Partially updating booking ID {booking_id}")
        if not self.auth_token:
            self.authenticate()
        # PATCH requires authentication (token)
        return self.patch(f"{self.booking_endpoint}/{booking_id}", json=booking_data, requires_auth=True)

    def delete_booking(self, booking_id: int) -> Response:
        logger.info(f"Deleting booking ID: {booking_id}")
        if not self.auth_token:
            self.authenticate()
        # DELETE requires authentication (token)
        return self.delete(f"{self.booking_endpoint}/{booking_id}", requires_auth=True)

    def health_check(self) -> Response:
        logger.info("Performing health check (ping)")
        return self.get("/ping", requires_auth=False)
