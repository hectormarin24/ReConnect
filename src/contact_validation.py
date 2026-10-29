
import re


def validate_contact(full_name, email, phone):
    """
    Validate contact information before saving.

    Returns:
        (True, "") if the information is valid.
        (False, error_message) otherwise.
    """

    full_name = full_name.strip()
    email = email.strip()
    phone = phone.strip()

    # A contact must have a name.
    if not full_name:
        return False, "Please enter the contact's full name."

    # Require at least one way to contact the person.
    if not email and not phone:
        return False, "Please enter an email address or phone number."

    # Validate email format when an email is provided.
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Please enter a valid email address."

    # Validate phone format when a phone number is provided.
    if phone:
        digits = re.sub(r"\D", "", phone)

        if len(digits) not in (10, 11):
            return False, "Please enter a valid phone number."

        if len(digits) == 11 and not digits.startswith("1"):
            return False, "Please enter a valid US phone number."

    return True, ""
