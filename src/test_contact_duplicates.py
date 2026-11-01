
from contact_duplicates import check_duplicate_contact


def run_tests():
    existing_contacts = [
        {
            "email": "john@gmail.com",
            "phone": "(916) 555-1234"
        },
        {
            "email": "mary@gmail.com",
            "phone": "9165555678"
        }
    ]

    test_cases = [
        ("JOHN@gmail.com", "", True, "Duplicate email"),
        ("", "916-555-1234", True, "Duplicate phone"),
        ("new@gmail.com", "9165559999", False, "New contact"),
        ("", "", False, "Empty contact"),
        ("MARY@gmail.com", "", True, "Imported duplicate email"),
        ("", "(916) 555-5678", True, "Imported duplicate phone"),
    ]

    for email, phone, expected, description in test_cases:
        is_duplicate, message = check_duplicate_contact(
            email, phone, existing_contacts
        )

        assert is_duplicate == expected, (
            f"{description} failed: {message}"
        )

        print(f"PASS: {description}")


if __name__ == "__main__":
    run_tests()
