CREATE DATABASE IF NOT EXISTS reconnect;

USE reconnect;

CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(150) NOT NULL,
    lname VARCHAR(150),
    mname VARCHAR(150),
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20) UNIQUE,
    tags JSON,
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