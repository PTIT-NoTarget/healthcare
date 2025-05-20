-- The main database healthcare_users is already created via environment variables
-- No additional databases needed for MySQL as it's only used for the default/auth database
-- Grant all privileges to the healthcare user
GRANT ALL PRIVILEGES ON healthcare_users.* TO 'healthcare'@'%';
FLUSH PRIVILEGES; 