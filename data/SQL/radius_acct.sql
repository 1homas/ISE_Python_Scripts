--
-- Show a practical view of the radius_accounting table.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    -- timestamp AS timestamp,
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    acct_session_id AS session_id, -- Unique numeric string identifying the server session
    acct_status_type AS status, -- Specifies whether accounting packet starts or stops a bridging, routing, or terminal server session.
    syslog_message_code AS code, -- 3000=Acct-Start, 3001=Acct-Stop, 3002=Interim-Update, 3003=Acct-On, 3004=Acct-Off
    acct_session_time AS duration, -- Length of time (in seconds) for which the session has been logged in
    acct_input_octets AS oct_in, -- Number of octets received during the session
    acct_output_octets AS oct_out, -- Number of octets sent during the session
    acct_input_packets AS pack_in, -- Number of packets received during the session
    acct_output_packets AS pack_out, -- Number of octets sent during the session
    acct_terminate_cause AS termination, -- Reason a connection was terminated
    calling_station_id AS MAC,
    username,
    device_name -- ISE network device name
    -- access_service, -- ISE Allowed Protocls
    -- acct_authentic,
    -- acct_delay_time AS delay, -- always 0? Length of time (in seconds) for which the NAS has been sending the same accounting packet
    -- acct_interim_interval, -- Number of seconds between each transmittal of an interim update for a specific session
    -- acct_multi_session_id,
    -- acct_tunnel_connection, -- ⚠ empty
    -- acct_tunnel_packet_lost, -- ⚠ empty
    -- ad_domain,
    -- audit_session_id,
    -- authorization_policy,
    -- cisco_h323_connect_time,
    -- cisco_h323_disconnect_time,
    -- cisco_h323_setup_time,
    -- device_groups,
    -- event_timestamp, -- The date and time that this event occurred on the NAS
    -- failure_reason,
    -- framed_ip_address,
    -- framed_ipv6_address,
    -- framed_protocol,
    -- id,
    -- identity_group,
    -- identity_store,
    -- idle_timeout,
    -- ise_node, -- ISE node name
    -- nas_identifier,
    -- nas_ip_address, -- The IP address of the NAS originating the request
    -- nas_ipv6_address,
    -- nas_port_id, -- If provided by NAS
    -- nas_port, -- Physical port number of the NAS (Network Access Server) originating the request
    -- response_time, -- in milliseconds
    -- security_group AS SGT, -- ⚠ empty
    -- service_selection_policy,
    -- service_type, -- RADIUS Service Type: Framed, Call-Check, etc.
    -- session_id, -- ⚠ very long string
    -- session_timeout
    -- started,
    -- stopped,
    -- termination_action,
    -- timestamp_timezone,
    -- user_type,
    -- vn,
FROM radius_accounting
-- WHERE acct_status_type = 'Start' -- 3000=Start, 3001=Stop, 3002=Interim-Update, 3003=Accounting-On, 3004=Accounting-Off
-- WHERE syslog_message_code = '3001' -- 3000=Start, 3001=Stop, 3002=Interim-Update, 3003=Accounting-On, 3004=Accounting-Off
-- WHERE acct_status_type = 'Stop'
-- WHERE stopped != 3001
-- WHERE username = 'thomas'
-- WHERE device_name = 'thomas-mr46-2nl6'
-- WHERE acct_session_time < (60*60) -- sessions < 1 hour
-- WHERE acct_session_time > 3700 -- > sessions 1 hour
-- WHERE acct_session_time > (60*60*24) -- sessions > 1 day
-- WHERE acct_session_time > (60*60*24*3) -- sessions > 3 days
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
-- WHERE TO_CHAR(timestamp, 'YYYY-MM-DD') = '2024-11-01' -- match a timestamp by day
-- WHERE TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') = '2024-11-01 00:08:27' -- match a timestamp (YYYY-MM-DD HH24:MI:SS.ffffff)
-- WHERE TRUNC(timestamp) = TRUNC(SYSDATE) -- today
-- WHERE TRUNC(timestamp) = '01-NOV-24' -- Specific day (trunc format)
-- WHERE TRUNC(timestamp, 'HH24') = TRUNC(SYSDATE, 'HH24') -- sessions this hour
-- WHERE TRUNC(timestamp, 'DD') = '20-OCT-24' -- Specific DoM Format: 'DD-MMM-YY HH.MM.SS.mmmmmmmmm AM|PM'
-- WHERE timestamp > '01-NOV-24 08.00.00.000 AM' -- Format: 'DD-MMM-YY HH.MM.SS.mmmmmmmmm AM|PM'
-- WHERE timestamp > TIMESTAMP '2024-11-01 19:39:00' -- after a timestamp
-- WHERE timestamp > TIMESTAMP '2024-11-01 19:00:00' AND timestamp < TIMESTAMP '2024-11-01 20:00:00' -- time window
-- WHERE timestamp BETWEEN Date '2024-11-01' and Date '2024-11-02' -- exclusive of end date
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
-- FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
