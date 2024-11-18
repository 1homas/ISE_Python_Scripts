--
-- RADIUS Authentications with Username 'INVALID'
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
  -- timestamp,
  TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
  -- failed,
  calling_station_id,
  username,
  failure_reason,
  device_name,
  nas_port_id,
  nas_port_type,
  response_time,
  policy_set_name, -- Default, Wired, etc.
  ise_node
  -- user_type,
  -- '1' for username='INVALID'
  -- access_service, -- Allowed Protocols
  -- audit_session_id,
  -- authentication_method,
  -- authentication_protocol,
  -- authorization_profiles, -- ⚠ blank for failed auths
  -- authorization_rule, -- ⚠ blank for failed auths
  -- checksum,
  -- credential_check -- Auth protocol?
  -- device_type, -- NDG
  -- framed_ip_address,
  -- framed_ipv6_address,
  -- ⓘ Endpoint
  -- id,
  -- identity_group,
  -- identity_store,
  -- location, -- NDG
  -- mdm_server_name, -- ⚠ blank for failed auths
  -- nas_ip_address,
  -- nas_ipv6_address,
  -- orig_calling_station_id,
  -- passed, -- 'Fail' for username='INVALID'
  -- posture_status, -- ⚠ blank for failed auths
  -- response_time
  -- security_group, -- ⚠ blank for failed auths
  -- service_type,
  -- syslog_message_code,
FROM radius_authentications
WHERE username = 'INVALID'
-- ORDER BY timestamp ASC -- first/oldest records
ORDER BY timestamp DESC -- most recent records
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
