--
-- RADIUS Authentications by Policy
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    policy_set_name AS policy_set, -- 
    -- access_service AS allowed_protocols, -- 
    authentication_method AS authn_method, -- 
    authentication_protocol AS authn_protocol, -- 
    NVL(authorization_rule, '-') AS authz_rule, -- 
    NVL(authorization_profiles, 'ACCESS-REJECT') AS authz_profile, -- 
    MAX(security_group) AS security_group, -- 
    TO_CHAR(AVG(response_time), '9999999') || 'ms' AS rt_avg, -- avg response time
    TO_CHAR(MAX(response_time), '9999999') || 'ms' AS rt_max, -- max response time
    COUNT(CASE WHEN passed = 'Pass' THEN 1 END) AS passed,
    COUNT(CASE WHEN passed = 'Fail' THEN 1 END) AS failed,
    COUNT(timestamp) AS total,
    TO_CHAR(ROUND( (COUNT(CASE WHEN passed = 'Fail' THEN 1 END) / (COUNT(CASE WHEN passed = 'Pass' THEN 1 END) + COUNT(CASE WHEN passed = 'Fail' THEN 1 END)) * 100), 0), 'FM999') || '%' AS fail_pct
    -- COUNT(DISTINCT device_name) AS devices,
    -- MAX(audit_session_id) AS audit_session_id, -- 
    -- MAX(calling_station_id) AS mac, -- 
    -- MAX(checksum) AS checksum, -- 
    -- MAX(credential_check) AS credential_check, -- 
    -- MAX(device_type) AS device_type, -- 
    -- MAX(endpoint_profile) AS endpoint_profile, -- 
    -- MAX(failed) AS failed, -- 
    -- MAX(failure_reason) AS failure_reason, -- 
    -- MAX(framed_ip_address) AS framed_ip_address, -- 
    -- MAX(framed_ipv6_address) AS framed_ipv6_address, -- 
    -- MAX(id) AS id, -- 
    -- MAX(identity_group) AS identity_group, -- 
    -- MAX(identity_store) AS identity_store, -- 
    -- MAX(ise_node) AS ise_node, -- 
    -- MAX(location) AS location, -- 
    -- MAX(mdm_server_name) AS mdm_server_name, -- 
    -- MAX(nas_ip_address) AS nas_ip_address, -- 
    -- MAX(nas_ipv6_address) AS nas_ipv6_address, -- 
    -- MAX(nas_port_id) AS nas_port_id, --  -- Physical port number of the NAS (Network Access Server) originating the request
    -- MAX(nas_port_type) AS nas_port_type, -- 
    -- MAX(orig_calling_station_id) AS orig_calling_station_id, -- 
    -- MAX(passed) AS passed, -- 
    -- MAX(posture_status) AS posture_status, -- 
    -- MAX(response_time) AS response_time, -- 
    -- MAX(service_type) AS service_type, -- 
    -- MAX(syslog_message_code) AS syslog_message_code, -- 
    -- MAX(timestamp) AS timestamp, -- 
    -- MAX(timestamp_timezone) AS timestamp_timezone, -- 
    -- MAX(user_type) AS user_type, -- 
    -- MAX(username) AS username, -- 
FROM radius_authentications
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
WHERE timestamp > sysdate - INTERVAL '30' DAY -- last N days
GROUP BY policy_set_name, access_service, authentication_method, authentication_protocol, authorization_rule, authorization_profiles
-- GROUP BY policy_set_name
ORDER BY policy_set_name ASC, total DESC 
-- ORDER BY calling_station_id ASC
-- ORDER BY username ASC
-- FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
