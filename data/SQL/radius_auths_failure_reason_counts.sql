--
-- RADIUS Authentications by Failure Reason
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
  COUNT(*) as total,
  calling_station_id AS mac,
  username AS username,
  -- MAX(device_name),
  -- MAX(nas_ip_address),
  -- MAX(ise_node),
  -- MAX(policy_set_name), -- Default, Wired, etc.
  -- audit_session_id,
  -- access_service, -- Allowed Protocols
  -- authentication_method AS auth_method,
  -- authentication_protocol AS auth_protocol,
  -- authorization_rule AS authz_rule, -- ⚠ Blank for failed auths!
  -- authorization_profiles AS authz_profiles, -- ⚠ Blank for failed auths!
  failure_reason
FROM radius_authentications
WHERE failure_reason IS NOT NULL
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
GROUP BY failure_reason, calling_station_id, username
ORDER BY total DESC
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
