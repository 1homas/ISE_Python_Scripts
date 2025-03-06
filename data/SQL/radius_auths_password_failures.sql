--
-- Count password-related failures which may indicate a credential stuffing attack.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--
SELECT
  COUNT(*) AS total,
  TO_CHAR(MAX(timestamp), 'YYYY-MM-DD HH24:MI:SS') AS last_failed, -- drop fractional seconds
  username,
  nas_port_type,
  -- calling_station_id,
  -- device_name,
  failure_reason
  -- policy_set_name, -- Default, Wired, etc.
  -- location, -- NDG
  -- passed, -- 'Fail' for username='INVALID'
  -- user_type,  -- ⚠ Blank?
  -- nas_ip_address,
  -- nas_port_id,
  -- ise_node,
  -- audit_session_id,
  -- access_service, -- Allowed Protocols
  -- authentication_method AS auth_method,
  -- authentication_protocol AS auth_protocol,
  -- authorization_rule AS authz_rule, -- ⚠ Blank for failed auths!
  -- authorization_profiles AS authz_profiles, -- ⚠ Blank for failed auths!
  -- checksum,
  -- credential_check -- Auth protocol?
  -- device_type, -- NDG
  -- failed,
  -- framed_ip_address,
  -- framed_ipv6_address,
  -- id,
  -- identity_group,
  -- identity_store,
  -- mdm_server_name,
  -- nas_ipv6_address,
  -- orig_calling_station_id,
  -- posture_status, 
  -- response_time -- ⚠ Blank for failed auths!
  -- security_group, -- ⚠ Blank for failed auths!
  -- service_type,
  -- syslog_message_code,
  -- response_time
FROM radius_authentications
WHERE failure_reason LIKE '%password%'
-- WHERE failure_reason ^= '22040 Wrong password or invalid shared secret'
-- WHERE nas_port_type = 'Virtual' -- VPN connections
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '7' DAY -- last N days
GROUP BY
  username,
  nas_port_type,
  -- calling_station_id,
  -- device_name,
  failure_reason
ORDER BY total DESC, username ASC