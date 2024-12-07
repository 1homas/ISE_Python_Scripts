--
-- Show All Cisco ISE RADIUS Accounting Sessions by ID with start, stop and session time.
-- Session states are in the `ℹ` column: □ stopped, ! ghosted, ⧖ interim, ▷ started
-- An active session is generally considered 'ghosted' after >24 hours without a Stop or Interim Update.
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--


SELECT
    acct_session_id,
    CASE WHEN MAX(syslog_message_code) = 3001 THEN '□' WHEN (MAX(timestamp) < (SYSDATE - 1)) THEN '!' WHEN MAX(syslog_message_code) = '3002' THEN '⧖'  ELSE '▷' END AS ℹ, -- [□ stopped, ! ghosted, ⧖ interim, ▷ started] alternatives: ▷ | □ ⏹ ⚠ ! ◌ ⍉ ⬚ ◯ ▶ ◻ □ ○ ◌
    TO_CHAR(MIN(timestamp), 'YYYY-MM-DD HH24:MI:SS') AS started, -- drop fractional seconds
    TO_CHAR(MAX(timestamp), 'YYYY-MM-DD HH24:MI:SS') AS stopped, -- drop fractional seconds
    MAX(syslog_message_code) AS code, -- 3000=Acct-Start, 3001=Acct-Stop, 3002=Interim-Update, 3003=Acct-On, 3004=Acct-Off
    COUNT(timestamp) AS num, -- total accounting updates
    NVL(MAX(acct_session_time), 0) AS time, -- time (seconds) for which the session has been Started
    MAX(calling_station_id) AS mac, -- endpoint MAC address (00:00:00:00:00:00)
    MAX(username) AS username, -- username or MAC (00-00-00-00-00-00)
    MAX(acct_terminate_cause) AS termination, -- Reason a connection was terminated
    MAX(device_name) AS device_name, -- ISE device name
    MAX(response_time) as resp_ms
    -- MIN(event_timestamp) AS nas_timestamp, -- seconds since epoch that this event occurred on the NAS
    -- MIN(syslog_message_code) AS min_code, -- 3000=Acct-Start, 3001=Acct-Stop, 3002=Interim-Update, 3003=Acct-On, 3004=Acct-Off
    -- NVL(MAX(acct_session_time), ((CAST(SYSTIMESTAMP AS DATE) - (CAST(MIN(timestamp) AS DATE))) * 86400)) AS length, -- calculate time (seconds) since the session Started
    -- MAX(session_id), -- very long string (8a37ff0600001811672d50d2:ise-span/519859596/4561)
    -- MAX(user_type) AS user_type, -- ⚠ empty
    -- MIN(acct_status_type) AS status_min, -- [Interim-Update, Start, Stop]
    -- MAX(acct_status_type) AS status_max, -- [Interim-Update, Start, Stop]
    -- MAX(service_type) AS service_type, -- RADIUS Service-Type: [Framed, Call Check, ...]
    -- MAX(acct_input_octets) AS acct_input_octets, -- Number of octets received during the session
    -- MAX(acct_output_octets) AS acct_output_octets, -- Number of octets sent during the session
    -- MAX(acct_input_packets) AS acct_input_packets, -- Number of packets received during the session
    -- MAX(acct_output_packets) AS acct_output_packets, -- Number of octets sent during the session
    -- MAX(nas_port) AS nas_port, -- Physical port number of the NAS (Network Access Server) originating the request
    -- MAX(nas_ip_address) AS nas_ip_address, -- The IP address of the NAS originating the request
    -- MAX(framed_protocol) AS framed_protocol, -- ⚠ empty
    -- MAX(framed_ip_address) AS framed_ip_address,
    -- MAX(access_service) AS access_service,
    -- MAX(audit_session_id) AS audit_session_id, -- (75ec21060000000366c76fb5)
    -- MAX(acct_multi_session_id) AS acct_multi_session_id,
    -- MAX(acct_authentic) AS acct_authentic, -- RADIUS
    -- MAX(session_timeout) AS session_timeout, -- ⚠ empty
    -- MAX(idle_timeout) AS idle_timeout, -- ⚠ empty
    -- MAX(acct_interim_interval) AS interim, -- ⚠ empty. Number of seconds between each transmittal of an interim update for a specific session
    -- MAX(acct_delay_time), -- time (seconds) for which the NAS has been sending the same accounting packet
    -- MAX(acct_tunnel_connection), -- ⚠ empty
    -- MAX(acct_tunnel_packet_lost), -- ⚠ empty
    -- MAX(device_groups) AS device_groups,
    -- MAX(nas_identifier),
    -- MAX(nas_port_id) AS port_id, -- ⚠ empty
    -- MAX(service_selection_policy) AS service_selection_policy,-- ⚠ empty
    -- MAX(identity_store) AS identity_store,-- ⚠ empty
    -- MAX(ad_domain) AS ad_domain,
    -- MAX(identity_group) AS identity_group, -- ⚠ empty
    -- MAX(authorization_policy) AS authz, -- ⚠ empty
    -- MAX(failure_reason), -- ⚠ empty - no session if authentication failed
    -- MAX(security_group) AS SGT, -- ⚠ empty
    -- cisco_h323_setup_time,
    -- cisco_h323_connect_time,
    -- cisco_h323_disconnect_time,
FROM radius_accounting
WHERE syslog_message_code != 3003 AND syslog_message_code != 3004 -- ignore Accounting-On/Off messages
    -- AND calling_station_id = 'DC:A6:32:6D:A3:BA'
    -- AND username = 'thomas'
    -- AND device_name = 'thomas-mr46-2nl6'
    -- AND acct_session_time < (60*60) -- sessions < 1 hour
    -- AND acct_session_time > 3700 -- > sessions 1 hour
    -- AND acct_session_time > (60*60*24) -- sessions > 1 day
    -- AND acct_session_time > (60*60*24*3) -- sessions > 3 days
    -- AND TRUNC(timestamp) = TRUNC(SYSDATE) -- today
    -- AND TRUNC(timestamp, 'HH24') = TRUNC(SYSDATE, 'HH24') -- sessions this hour
    -- AND TRUNC(timestamp) = '01-NOV-24' -- Specific day (trunc default)
    -- AND TRUNC(timestamp, 'DD') = '20-OCT-24' -- Specific DoM Format: 'DD-MMM-YY HH.MM.SS.mmmmmmmmm AM|PM'
    -- AND timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
    -- AND timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
    -- AND timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
    -- AND timestamp > sysdate - INTERVAL '1' DAY -- last N days
    -- AND timestamp > TIMESTAMP '2024-11-01 19:39:00' -- after a timestamp
    -- AND timestamp > TIMESTAMP '2024-11-01 19:00:00' AND timestamp < TIMESTAMP '2024-11-01 20:00:00' -- time window
    -- AND timestamp BETWEEN Date '2024-11-01' and Date '2024-11-02' -- exclusive of end date
GROUP BY acct_session_id
ORDER BY MIN(timestamp) ASC -- first/oldest records
-- ORDER BY NVL(MAX(acct_session_time), 0) DESC, MIN(timestamp) ASC -- longest sessions
-- FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
