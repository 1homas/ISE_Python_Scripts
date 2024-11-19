--
-- Show the last RADIUS authentication per endpoint.
-- Includes random MAC detection (2nd digit is 26AE).
-- Optionally filter for >N days or more.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    calling_station_id AS mac, --  
    MAX(CASE WHEN REGEXP_LIKE(calling_station_id, '^.[26AE].*', 'i') THEN '✔' END) AS random, -- Indicator: ✔
    -- MAX(CASE WHEN REGEXP_LIKE(calling_station_id, '^.[26AE].*', 'i') THEN '✔' ELSE '✖' END) AS random, -- Indicator: ✔|✖
    -- MAX(CASE WHEN REGEXP_LIKE(calling_station_id, '^.[26AE].*', 'i') THEN SUBSTR(calling_station_id, 2, 1) END) AS random, -- Indicator: 2|6|A|E
    TO_CHAR(MAX(timestamp), 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    MAX(location) AS location, --  
    MAX(username) AS username, --  
    MAX(endpoint_profile) AS endpoint_profile, --  
    MAX(security_group) AS SGT, -- ⚠ Blank for failed auths!
    MAX(device_name) AS device_name, --  
    MAX(framed_ip_address) AS ipv4, --  
    MAX(passed) AS passed -- 'Fail' for username='INVALID'
    -- MAX(failure_reason) AS failure_reason --  
    -- MAX(access_service) AS access_service, -- Allowed Protocols
    -- MAX(audit_session_id) AS audit_session_id, --  
    -- MAX(authentication_method) AS auth_method, --  
    -- MAX(authentication_protocol) AS auth_protocol, --  
    -- MAX(authorization_profiles) AS authz_profiles, -- ⚠ Blank for failed auths!
    -- MAX(authorization_rule) AS authz_rule, -- ⚠ Blank for failed auths!
    -- MAX(checksum) AS checksum, --  
    -- MAX(credential_check) AS credential_check, --  
    -- MAX(device_type) AS device_type, --  
    -- MAX(failed) AS failed, --  
    -- MAX(framed_ipv6_address) AS ipv6, --  
    -- MAX(id) AS id, --  
    -- MAX(identity_group) AS identity_group, --  
    -- MAX(identity_store) AS identity_store, --  
    -- MAX(ise_node) AS ise_node, --  
    -- MAX(mdm_server_name) AS mdm_server_name, --  
    -- MAX(nas_ip_address) AS nas_ip_address, --  
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
FROM radius_authentications
GROUP BY calling_station_id
-- HAVING MAX(timestamp) < (sysdate - INTERVAL '30' DAY) -- Last seen >30 days ago
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
