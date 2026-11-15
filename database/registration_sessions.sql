USE reconnect;

CREATE TABLE IF NOT EXISTS registration_sessions(
phone VARCHAR(16) PRIMARY KEY,
stage ENUM('awaiting_name', 'awaiting_email') NOT NULL,
name VARCHAR(150),
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP
);