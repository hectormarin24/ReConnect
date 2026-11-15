CREATE DATABASE IF NOT EXISTS reconnect;

USE reconnect;

CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS email_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    direction ENUM('inbound', 'outbound') NOT NULL,
    contact_id INT NULL,
    from_email VARCHAR(255) NOT NULL,
    to_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    body TEXT,
    status ENUM('queued','sent','delivered','failed','received') DEFAULT 'sent',
    sent_at TIMESTAMP NULL,
    received_at TIMESTAMP NULL,
    imap_uidvalidity BIGINT UNSIGNED NULL,
    imap_uid BIGINT UNSIGNED NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_imap_message (imap_uidvalidity, imap_uid),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);
CREATE TABLE IF NOT EXISTS user_sessions (
    token_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
    user_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,

    INDEX idx_user_sessions_user_id (user_id),
    INDEX idx_user_sessions_expires_at (expires_at),

    CONSTRAINT fk_user_sessions_user
        FOREIGN KEY (user_id)
        REFERENCES admin_users(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS twilio_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    label VARCHAR(100) NOT NULL,

    account_sid CHAR(34)
        CHARACTER SET ascii COLLATE ascii_bin NOT NULL,

    auth_token_encrypted TEXT NOT NULL,

    sms_number VARCHAR(16) DEFAULT NULL,
    whatsapp_number VARCHAR(16) DEFAULT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_twilio_accounts_account_sid (account_sid),

    INDEX idx_twilio_accounts_user_id (user_id),

    CONSTRAINT fk_twilio_accounts_user
        FOREIGN KEY (user_id)
        REFERENCES admin_users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS twilio_messages (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    twilio_account_id INT NOT NULL,

    message_sid CHAR(34)
        CHARACTER SET ascii COLLATE ascii_bin NOT NULL,

    channel ENUM('sms', 'whatsapp') NOT NULL,
    direction ENUM('inbound', 'outbound') NOT NULL,

    from_address VARCHAR(64) NOT NULL,
    to_address VARCHAR(64) NOT NULL,
    body TEXT NOT NULL,

    status VARCHAR(32) NOT NULL,
    error_code INT DEFAULT NULL,

    is_read BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uq_twilio_messages_sid (message_sid),

    INDEX idx_twilio_messages_account_created (
        twilio_account_id,
        created_at,
        id
    ),

    INDEX idx_twilio_messages_account_unread (
        twilio_account_id,
        direction,
        is_read
    ),

    CONSTRAINT fk_twilio_messages_account
        FOREIGN KEY (twilio_account_id)
        REFERENCES twilio_accounts(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
