USE reconnect;

CREATE TABLE IF NOT EXISTS registration_locks (
    phone VARCHAR(16) PRIMARY KEY
) ENGINE=InnoDB;

SET @ddl = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'twilio_messages'
       AND COLUMN_NAME = 'registration_reply') = 0,
    'ALTER TABLE twilio_messages ADD COLUMN registration_reply TEXT NULL',
    'SELECT 1'
);

PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ddl = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'twilio_messages'
       AND COLUMN_NAME = 'registration_processed_at') = 0,
    'ALTER TABLE twilio_messages ADD COLUMN registration_processed_at TIMESTAMP NULL DEFAULT NULL',
    'SELECT 1'
);

PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;