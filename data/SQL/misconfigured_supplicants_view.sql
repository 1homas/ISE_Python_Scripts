--
-- misconfigured_supplicants_view
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- timestamp_timezone, -- time with timezone when record added
    -- timestamp, -- time when record added
    -- access_service, -- access service
    -- audit_session_id, -- unique numeric string identifying the server session
    -- authentication_method, -- authentication method
    -- authentication_protocol, -- authentication protocol
    -- calling_station_id, -- calling station id
    -- credential_check, -- credential check
    -- device_type, -- device type
    -- endpoint_profile, -- endpoint matched profile
    -- execution_steps, -- execution steps
    -- failed, -- failed flag
    -- failure_reason, -- failure reason
    -- framed_ip_address, -- framed ip address
    -- framed_ipv6_address, -- framed ipv6 address
    -- id, -- database unique id
    -- identity_group, -- identity group
    -- identity_store, -- identity store
    -- ise_node, -- displays the hostname of the ise server
    -- location, -- location
    -- mdm_server_name, -- mdm server name
    -- message_code, -- displays the message code
    -- message_text, -- displays the message text
    -- nas_ip_address, -- ip address of nas
    -- nas_ipv6_address, -- nas ipv6 address
    -- nas_port_id, -- nas port id
    -- nas_port_type, -- nas port type
    -- network_device_name, -- network device name
    -- other_attributes, -- other attributes
    -- passed, -- passed flag
    -- posture_status, -- posture status
    -- response_time, -- response time
    -- response, -- displays the response
    -- security_group, -- security group
    -- selected_authorization_profiles, -- authorization profile used after authentication
    -- service_type, -- the type of service the user has requested
    -- user_type, -- user type
    -- username, -- user's claimed identity
FROM misconfigured_supplicants_view
-- ORDER BY timestamp ASC
ORDER BY timestamp DESC
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
