--
-- radius_authentication_summary
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- timestamp, -- timestamp(6)  Time when record added
    -- ise_node, -- Name of the ISE server used for authentication
    -- username, -- User name
    -- calling_station_id, -- Mac address of the device the user is using
    -- identity_store, -- The Identity Store to which the user authenticated belongs to. Example - Internal Endpoints
    -- identity_group, -- The Identity Group to which the user belongs to. Example - Windows11-Workstation
    -- device_name, -- The name of the network device used by the user to access network. Example - 9800CLWLC, Access-Switch-3K, 9800VWLC etc.
    -- device_type, -- The type of the network device used by the user to access network. Example - Wireless - IEEE 802.11
    -- location, -- The location hierarchy of the the network device. Example - All Locations#My-Territory#US#Sanjose#BLDG5
    -- access_service, -- The protocol used for authentication. Example - NDAC_SGT_Service, Default Network Access
    -- nas_port_id, -- ID of the NAD Port used. Example - GigabitEthernet1/0/14
    -- authorization_profiles, -- The authorization profile applied. Example - PermitAccess, Machine-Access
    -- failure_reason, -- Reason for the failure, in case authentication was not successful
    -- security_group, -- The security group classification of the device i.e the source SGT. Example - TrustedDevices, Quarantined_Systems
    -- total_response_time, -- The total response time required for authentication
    -- max_response_time, -- The maximum response time required for authentication
    -- passed_count, -- The number of passed authentication
    -- failed_count, -- Number of failed authentication
FROM radius_authentication_summary
-- ORDER BY timestamp ASC -- first/oldest records
ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets