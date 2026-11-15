USE reconnect;

ALTER TABLE twilio_messages
    ADD COLUMN registration_reply TEXT NULL,
    ADD COLUMN registration_processed_at TIMESTAMP NULL DEFAULT NULL;