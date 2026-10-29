def normalize_phone(phone):
    return "".join(char for char in phone if char.isdigit())


def check_duplicate_contact(email, phone, existing_contacts):
    email = email.strip().lower()
    phone = normalize_phone(phone.strip())

    for contact in existing_contacts:
        existing_email = (contact.get("email") or "").strip().lower()
        existing_phone = normalize_phone(
            (contact.get("phone") or "").strip()
        )

        if email and email == existing_email:
            return True, "A contact with this email already exists."

        if phone and phone == existing_phone:
            return True, "A contact with this phone number already exists."

    return False, ""