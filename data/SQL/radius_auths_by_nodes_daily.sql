--
-- Show RADIUS Authentications per ISE Node Daily
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
  TO_CHAR(MIN(timestamp), 'YYYY-MM-DD') AS timestamp, -- drop fractional seconds
  -- TRUNC(timestamp) DAY,
  ise_node,
  -- device_name,
  -- passed, -- 'Fail' for username='INVALID'
  -- failed, -- '1' for username='INVALID'
  SUM( CASE WHEN failed = '0' THEN 1 END ) AS passed,
  SUM( CASE WHEN failed = '1' THEN 1 END ) AS failed,
  SUM( CASE WHEN failed = '0' THEN 1 END ) + SUM( CASE WHEN failed = '1' THEN 1 END ) AS total,
  ROUND( TO_CHAR( ( ( SUM( CASE WHEN failed = '1' THEN 1 END ) / ( SUM( CASE WHEN failed = '0' THEN 1 END ) + SUM(failed) ) ) * 100 ) ), 0) AS fail_pct,
  MAX(response_time) AS max_resp_time -- ⓘ Request
  -- access_service, -- Allowed Protocols
  -- audit_session_id,
  -- authentication_method,
  -- authentication_protocol,
  -- authorization_profiles, -- 💡 Blank for failed auths!
  -- authorization_rule, -- 💡 Blank for failed auths!
  -- calling_station_id,
  -- checksum
  -- credential_check -- Auth protocol?
  -- device_name,
  -- device_type, -- NDG
  -- failure_reason,
  -- framed_ip_address,
  -- framed_ipv6_address,
  -- id,
  -- identity_group,
  -- identity_store,
  -- location, -- NDG
  -- mdm_server_name,
  -- nas_ip_address,
  -- nas_ipv6_address,
  -- nas_port_id,
  -- nas_port_type,
  -- orig_calling_station_id,
  -- policy_set_name -- Default, Wired, etc.
  -- posture_status,
  -- response_time
  -- response_time,
  -- security_group, -- 💡 Blank for failed auths!
  -- service_type,
  -- syslog_message_code,
  -- user_type, -- blank?
  -- username,
FROM radius_authentications
GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD'), ise_node
-- ORDER BY TRUNC(timestamp) ASC, ise_node ASC
ORDER BY timestamp DESC, ise_node ASC
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
