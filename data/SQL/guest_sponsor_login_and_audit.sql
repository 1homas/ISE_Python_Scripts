--
-- ISE Reports > Audit > Sponsor Login and Audit
--

SELECT
    * -- all columns
    -- id, -- database unique ID
    -- timestamp_timezone, -- TIMESTAMP(6) WITH TIME ZONE  Time with timezone when record added
    -- timestamp, -- timeSTAMP(6)  Time when record added
    -- sponser_user_namE, -- User name of sponsor
    -- ip_address, -- IP address
    -- mac_address, -- MAC address
    -- portal_name, -- Portal name
    -- result, -- Result
    -- identity_store, -- Identity store
    -- operation, -- Operation
    -- guest_username, -- User name of guest
    -- guest_status, -- Status of guest
    -- failure_reason, -- Reason of failure
    -- optional_data, -- Optional data
    -- psn_hostname, -- Hostname of PSN
    -- user_details, -- Details of user
    -- guest_details, -- Details of guest
    -- guest_users, -- Guest users
FROM sponsor_login_and_audit
ORDER BY timestamp ASC
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
