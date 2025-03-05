--
-- Show All Cisco ISE RADIUS Accounting Session Start events.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    -- timestamp,
    -- TRUNC(timestamp, 'DD') as timestamp,
    -- TRUNC(timestamp, 'MI') as timestamp,
    -- TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- per second (YYYY-MM-DD HH24:MI:SS)
    -- TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:') || '00' AS timestamp, -- per minute ('YYYY-MM-DD HH24:MI:00)
    -- TO_CHAR(timestamp, 'YYYY-MM-DD HH24:') || '00:00' AS timestamp, -- per hour (YYYY-MM-DD HH24:00:00)
    TO_CHAR(timestamp, 'YYYY-MM-DD') AS timestamp, -- per day (2024-12-01)
    COUNT(CASE WHEN acct_status_type = 'Start' THEN 1 END) AS starts,
    COUNT(CASE WHEN acct_status_type = 'Stop' THEN 1 END) AS stops,
    CASE 
        WHEN COUNT(CASE WHEN acct_status_type = 'Start' THEN 1 END) = 0 THEN 0 
        ELSE ROUND(COUNT(CASE WHEN acct_status_type = 'Stop' THEN 1 END) / COUNT(CASE WHEN acct_status_type = 'Start' THEN 1 END), 2)
    END AS stop_to_start,
    COUNT(CASE WHEN acct_status_type = 'Interim-Update' THEN 1 END) AS interims,
    ROUND(COUNT(CASE WHEN acct_status_type = 'Interim-Update' THEN 1 END) / COUNT(*), 2) AS interim_to_total,
    COUNT(CASE WHEN syslog_message_code > '3002' THEN 1 END) AS others,
    COUNT(*) AS total -- total
    -- access_service, -- ISE Allowed Protocls
    -- acct_authentic,
    -- acct_delay_time AS delay, -- always 0? Length of time (in seconds) for which the NAS has been sending the same accounting packet
    -- acct_input_octets AS oct_in, -- Number of octets received during the session
    -- acct_input_packets AS pack_in, -- Number of packets received during the session
    -- acct_interim_interval, -- Number of seconds between each transmittal of an interim update for a specific session
    -- acct_multi_session_id,
    -- acct_output_octets AS oct_out, -- Number of octets sent during the session
    -- acct_output_packets AS pack_out, -- Number of octets sent during the session
    -- acct_session_id AS session_id, -- Unique numeric string identifying the server session
    -- acct_session_time AS duration, -- Length of time (in seconds) for which the session has been logged in
    -- acct_session_time AS session_time,
    -- acct_status_type AS status, -- Specifies whether accounting packet starts or stops a bridging, routing, or terminal server session.
    -- acct_terminate_cause AS termination, -- Reason a connection was terminated
    -- acct_tunnel_connection, -- ⚠ empty
    -- acct_tunnel_packet_lost, -- ⚠ empty
    -- ad_domain,
    -- audit_session_id,
    -- authorization_policy,
    -- calling_station_id,
    -- cisco_h323_connect_time,
    -- cisco_h323_disconnect_time,
    -- cisco_h323_setup_time,
    -- device_groups,
    -- device_name -- ISE network device name
    -- event_timestamp, -- The date and time that this event occurred on the NAS
    -- failure_reason,
    -- framed_ip_address, -- session IP address of endpoint
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
    -- started, -- ⚠ always 1
    -- stopped, -- ⚠ always 0
    -- syslog_message_code AS code, -- 3000=Acct-Start, 3001=Acct-Stop, 3002=Interim-Update, 3003=Acct-On, 3004=Acct-Off
    -- termination_action,
    -- timestamp_timezone AS timestamp_tz,
    -- user_type,
    -- username,
    -- vn,
FROM radius_accounting
-- WHERE TRUNC(timestamp) = TRUNC(SYSDATE) -- today
-- WHERE TRUNC(timestamp, 'HH24') = TRUNC(SYSDATE, 'HH24') -- sessions this hour
-- WHERE TRUNC(timestamp, 'MI') = TRUNC(SYSDATE, 'MI') -- sessions this minute
-- GROUP BY TRUNC(timestamp, 'DD')
GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD') -- per day
-- GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD HH24:') || '00:00' -- per hour
-- GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:') || '00' -- per minute
-- GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') -- per second
ORDER BY timestamp ASC -- first/oldest records
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets