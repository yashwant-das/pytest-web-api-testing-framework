import random
import string

from faker import Faker  # Requires: pip install Faker

fake = Faker()


def generate_random_string(length: int = 10) -> str:
    """Generates a random string of fixed length."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def generate_random_email() -> str:  # Could be useful for some web forms
    """Generates a random email address."""
    return f"{generate_random_string(8)}@{generate_random_string(5)}.com"


# This is used by tests/api/test_booking_api.py
# Keep it, or make it more specific if needed.
# For Restful-booker, the test itself generates the booking payload using fake.
# So, this function as-is might not be directly used by the current booking tests,
# but `fake` instance is.

# Consider renaming or creating a specific one for booking if you want a helper
# def generate_booking_payload() -> dict:
#     return {
#         "firstname": fake.first_name(),
#         "lastname": fake.last_name(),
#         "totalprice": fake.random_int(min=50, max=1000),
#         "depositpaid": fake.boolean(),
#         "bookingdates": {
#             "checkin": fake.date_between(start_date="-1y", end_date="today").strftime('%Y-%m-%d'),
#             "checkout": fake.date_between(start_date="today", end_date="+1y").strftime('%Y-%m-%d')
#         },
#         "additionalneeds": random.choice(["Breakfast", "Parking", "No Smoking", fake.sentence(nb_words=3)])
#     }


# Removed: generate_random_user_data() as it was generic
# Removed: generate_product_data() as it was generic

if __name__ == "__main__":
    # print("Example Booking Payload:", generate_booking_payload())
    print("Random Email:", generate_random_email())
    print("Fake Name:", fake.name())  # Just to show fake is working
