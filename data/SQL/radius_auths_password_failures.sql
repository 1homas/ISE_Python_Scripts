--
-- Query to determine if there is a credential stuffing attack occurring via VPN
--

SELECT
  username,
  nas_port_type,
  failure_reason,
  COUNT( CASE WHEN failed = '1' THEN 1 END ) AS failed,
  COUNT(*) AS total

    -- TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    -- passed, -- 'Fail' for username='INVALID'
    -- calling_station_id,
    -- username,
    -- user_type,  -- ⚠ Blank?
    -- device_name,
    -- nas_ip_address,
    -- nas_port_id,
    -- nas_port_type,
    -- ise_node,
    -- policy_set_name, -- Default, Wired, etc.
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
    -- failure_reason,
    -- framed_ip_address,
    -- framed_ipv6_address,
    -- id,
    -- identity_group,
    -- identity_store,
    -- location, -- NDG
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
-- WHERE nas_port_type = 'Virtual'
-- WHERE failure_reason ^= '22040 Wrong password or invalid shared secret'
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
WHERE timestamp > sysdate - INTERVAL '7' DAY -- last N days
  AND failure_reason LIKE '%password%'

GROUP BY
  username,
  nas_port_type,
  failure_reason
ORDER BY failed DESC