--
-- RADIUS Errors Summary
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    COUNT(*) AS total, --
    message_code as error, -- Example: 5411
    MAX(message_text) AS message_text -- Example: Supplicant stopped responding to ISE
    -- MAX(TRUNC(timestamp)) AS timestamp --
    -- MAX(timestamp) AS timestamp --
    -- passed, -- always 'Fail'?
    -- failed, -- always 1?
    -- authentication_policy,
    -- authorization_policy,
    -- response_time, -- milliseconds
    -- credential_check, -- always empty?
    -- endpoint_profile, -- always empty?
    -- authentication_method, -- Example: MSCHAPV2
    -- authentication_protocol, -- Example: PEAP (EAP-MSCHAPv2), EAP-TLS
    -- network_device_name,
    -- response -- always empty?
    -- timestamp_timezone, -- OK for thin client
    -- id,
    -- ise_node,
    -- mdm_server_name,
    -- username,
    -- user_type,
    -- calling_station_id,
    -- access_service,
    -- framed_ip_address,
    -- framed_ipv6_address,
    -- identity_store,
    -- identity_group,
    -- audit_session_id,
    -- service_type,
    -- device_type, -- 'All Device Types' network device group (NDG)
    -- location, -- 'All Locations' network device group (NDG)
    -- nas_ip_address,
    -- nas_ipv6_address,
    -- nas_port_id,
    -- nas_port_type,
    -- selected_authorization_profiles,
    -- posture_status,
    -- security_group,
    -- failure_reason,
    -- execution_steps,
    -- other_attributes
    -- other_attributes_string, -- long list of RADIUS attributes 
FROM radius_errors_view
-- WHERE message_code = 5411
-- WHERE TRUNC(timestamp) = TRUNC(SYSDATE) -- today
-- WHERE TRUNC(timestamp, 'HH24') = TRUNC(SYSDATE, 'HH24') -- sessions this hour
-- WHERE TRUNC(timestamp, 'MI') = TRUNC(SYSDATE, 'MI') -- sessions this minute
GROUP BY message_code
-- ORDER BY total ASC -- increasing
ORDER BY total DESC -- decreasing
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
