--
-- radius_errors_view
-- Check for RADIUS Requests Dropped, EAP connection time outs and unknown NADs
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
  * -- all columns
  -- timestamp,
  -- passed, -- ⚠ always 'Fail'
  -- failed, -- ⚠ always 1
  -- authentication_policy, -- ⚠ always null
  -- authorization_policy, -- ⚠ always null
  -- response_time, -- milliseconds
  -- credential_check, -- ⚠ always null
  -- endpoint_profile, -- ⚠ always null
  -- authentication_method, -- Example: MSCHAPV2
  -- authentication_protocol, -- Example: PEAP (EAP-MSCHAPv2), EAP-TLS
  -- network_device_name,
  -- message_code, -- Example: 5411
  -- response -- always empty?
  -- timestamp_timezone, -- OK for thin client
  -- id,
  -- ise_node,
  -- mdm_server_name,
  -- username, -- user's claimed identity
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
  -- selected_authorization_profiles, -- authorization profile used after authentication
  -- posture_status,
  -- security_group,
  -- failure_reason,
  -- execution_steps,
  -- other_attributes,
  -- message_text, -- Example: Supplicant stopped responding to ISE
  -- other_attributes_string, -- long list of RADIUS attributes 
FROM radius_errors_view
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
FETCH FIRST 1 ROWS ONLY -- limit default number of rows returned for large datasets
