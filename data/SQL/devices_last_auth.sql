--
-- Show the last RADIUS authentication per network device.
-- Optionally filter for >N days or more.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    CAST(MAX(timestamp) AS DATE) AS last_auth, -- drop fractional seconds
    ROUND(CAST(SYSTIMESTAMP AS DATE) - CAST(MAX(timestamp) AS DATE), 2) AS inactive_days,
    nas_ip_address AS nas_ip_address, --  
    device_name AS device_name, --  
    -- MAX(nas_ip_address) AS nas_ip_address, --  
    -- MAX(location) AS location, --  
    MAX(calling_station_id) AS mac, --  
    MAX(username) AS username, --  
    MAX(endpoint_profile) AS endpoint_profile, --  
    MAX(security_group) AS SGT, -- ⚠ Blank for failed auths!
    -- MAX(access_service) AS access_service, -- Allowed Protocols
    -- MAX(audit_session_id) AS audit_session_id, --  
    MAX(authentication_method) AS auth_method, --  
    -- MAX(authentication_protocol) AS auth_protocol, --  
    -- MAX(authorization_profiles) AS authz_profiles, -- ⚠ Blank for failed auths!
    -- MAX(authorization_rule) AS authz_rule, -- ⚠ Blank for failed auths!
    -- MAX(checksum) AS checksum, --  
    -- MAX(credential_check) AS credential_check, --  
    -- MAX(device_type) AS device_type, --  
    -- MAX(framed_ip_address) AS ipv4, --  
    -- MAX(failure_reason) AS failure_reason --  
    -- MAX(failed) AS failed, --  
    -- MAX(framed_ipv6_address) AS ipv6, --  
    -- MAX(id) AS id, --  
    -- MAX(identity_group) AS identity_group, --  
    -- MAX(identity_store) AS identity_store, --  
    -- MAX(ise_node) AS ise_node, --  
    -- MAX(mdm_server_name) AS mdm_server_name, --  
    -- MAX(nas_ipv6_address) AS nas_ipv6_address, --  
    -- MAX(nas_port_id) AS nas_port_id, -- Physical port number of the NAS (Network Access Server) originating the request
    -- MAX(nas_port_type) AS nas_port_type, --  
    -- MAX(orig_calling_station_id) AS orig_calling_station_id, --  
    -- MAX(policy_set_name) AS policy_set_name, -- Default, Wired, etc.
    -- MAX(posture_status) AS posture_status, --  
    -- MAX(response_time) AS response_time, -- ⚠ Blank for failed auths!
    -- MAX(service_type) AS service_type, --  
    -- MAX(syslog_message_code) AS syslog_message_code, --  
    -- MAX(timestamp_timezone) AS timestamp_tz, --  
    -- MAX(user_type) AS user_type, --  
    MAX(passed) AS passed -- 'Fail' for username='INVALID'
FROM radius_authentications
GROUP BY nas_ip_address, device_name
-- HAVING MAX(timestamp) < (sysdate - INTERVAL '30' DAY) -- Last seen >30 days ago
ORDER BY last_auth ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
