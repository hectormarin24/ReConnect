USE reconnect;

ALTER TABLE email_messages
    ADD COLUMN imap_uidvalidity BIGINT UNSIGNED NULL,
    ADD COLUMN imap_uid BIGINT UNSIGNED NULL,
    ADD UNIQUE KEY unique_imap_message (imap_uidvalidity, imap_uid);
