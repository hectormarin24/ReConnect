-- ReConnect: Login Credentials Database
-- Run once while connected to the existing postgres maintenance database.
-- Run outside a transaction. Do not run this if reconnect already exists.

CREATE DATABASE reconnect
    WITH ENCODING = 'UTF8'
    TEMPLATE = template0;
