from fastapi import APIRouter, HTTPException, Query

from ..schemas import ContactCreate, ContactUpdate
from ..services.contact_services import (
    create_contact,
    delete_contact,
    get_contact_by_id,
    list_contacts,
    update_contact,
)
from ..services.email_services import send_outbound_email, fetch_inbound_emails

router = APIRouter()


@router.get("/contacts")
def get_contacts(
    search: str | None = Query(default=None),
    tag: str | None = Query(default=None),
):
    return list_contacts(search=search, tag=tag)


@router.get("/contacts/{contact_id}")
def get_single_contact(contact_id: int):
    contact = get_contact_by_id(contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/contacts")
def add_contact(payload: ContactCreate):
    created = create_contact(payload)
    if created is None:
        raise HTTPException(status_code=400, detail="Unable to create contact")
    return created


@router.put("/contacts/{contact_id}")
def edit_contact(contact_id: int, payload: ContactUpdate):
    updated = update_contact(contact_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated


@router.delete("/contacts/{contact_id}")
def remove_contact(contact_id: int):
    deleted = delete_contact(contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"success": True, "message": "Contact deleted"}

@router.post("/contacts/{contact_id}/send-email")
def send_contact_email(contact_id: int):
    contact = get_contact_by_id(contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    if not contact.get("email"):
        raise HTTPException(status_code=400, detail="Contact has no email")

    sent = send_outbound_email(
        contact["email"],
        "ReConnect Message",
        "Hello from ReConnect",
        contact_id=contact_id,
    )

    if not sent:
        raise HTTPException(status_code=500, detail="Email send failed")

    return {"success": True, "message": "Email sent successfully"}


@router.get("/emails/inbox")
def get_inbox():
    return fetch_inbound_emails()