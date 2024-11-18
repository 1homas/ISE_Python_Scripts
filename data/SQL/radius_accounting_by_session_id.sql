--
-- List All Cisco ISE RADIUS Accounting Sessions by ID with start, stop and session time.
-- Session states are in the `ℹ` column: □ stopped, ! ghosted, ⧖ interim, ▷ started
-- An active session is generally considered 'ghosted' after >24 hours without a Stop or Interim Update.
-- 💡 Un/Comment columns to quickly customize queries to suite your needs.
--

SELECT
    acct_session_id,
    timestamp,
    -- event_timestamp AS nas_timestamp, -- seconds since epoch that this event occurred on the NAS
    CASE WHEN syslog_message_code = 3001 THEN '□' WHEN syslog_message_code = '3002' THEN '⧖' WHEN syslog_message_code = '3000' THEN '▷' WHEN (timestamp < (SYSDATE - 1)) THEN '!'  ELSE '▷' END AS ℹ, -- [□ stopped, ! ghosted, ⧖ interim, ▷ started] alternatives: ▷|⏹ ⚠ ! ◌ ⍉ ⬚ ◯ ▶ ◻ □ ○ ◌
    syslog_message_code as msg_code, -- 3000=Acct-Start, 3001=Acct-Stop, 3002=Interim-Update, 3003=Acct-On, 3004=Acct-Off
    acct_status_type AS status_type, -- [Interim-Update, Start, Stop]
    acct_session_time AS session_time, -- time (seconds) for which the session has been Started
    acct_terminate_cause AS termination, -- Reason a connection was terminated
    NVL(acct_session_time, 0) AS duration, -- calculate time (seconds) since the session Started
    calling_station_id AS mac, -- endpoint MAC address (00:00:00:00:00:00)
    username AS username, -- username or MAC (00-00-00-00-00-00)
    device_name, -- ISE device name
    response_time as resp_ms
    -- session_id, -- very long string (8a37ff0600001811672d50d2:ise-span/519859596/4561)
    -- user_type AS user_type, -- ⚠ empty
    -- service_type AS service_type, -- RADIUS Service-Type: [Framed, Call Check, ...]
    -- acct_input_octets AS acct_input_octets, -- Number of octets received during the session
    -- acct_output_octets AS acct_output_octets, -- Number of octets sent during the session
    -- acct_input_packets AS acct_input_packets, -- Number of packets received during the session
    -- acct_output_packets AS acct_output_packets, -- Number of octets sent during the session
    -- nas_port AS nas_port, -- Physical port number of the NAS (Network Access Server) originating the request
    -- nas_ip_address AS nas_ip_address, -- The IP address of the NAS originating the request
    -- framed_protocol AS framed_protocol, -- ⚠ empty
    -- framed_ip_address AS framed_ip_address,
    -- access_service AS access_service,
    -- audit_session_id AS audit_session_id, -- (75ec21060000000366c76fb5)
    -- acct_multi_session_id AS acct_multi_session_id,
    -- acct_authentic AS acct_authentic, -- RADIUS
    -- session_timeout AS session_timeout, -- ⚠ empty
    -- idle_timeout AS idle_timeout, -- ⚠ empty
    -- acct_interim_interval AS interim, -- ⚠ empty. Number of seconds between each transmittal of an interim update for a specific session
    -- acct_delay_time, -- time (seconds) for which the NAS has been sending the same accounting packet
    -- acct_tunnel_connection, -- ⚠ empty
    -- acct_tunnel_packet_lost, -- ⚠ empty
    -- device_groups AS device_groups,
    -- nas_identifier,
    -- nas_port_id AS port_id, -- ⚠ empty
    -- service_selection_policy AS service_selection_policy,-- ⚠ empty
    -- identity_store AS identity_store,-- ⚠ empty
    -- ad_domain AS ad_domain,
    -- identity_group AS identity_group, -- ⚠ empty
    -- authorization_policy AS authz, -- ⚠ empty
    -- failure_reason, -- ⚠ empty - no session if authentication failed
    -- security_group AS SGT, -- ⚠ empty
    -- cisco_h323_setup_time,
    -- cisco_h323_connect_time,
    -- cisco_h323_disconnect_time,
FROM radius_accounting
WHERE acct_session_id = '9F41F68A7FBE8B9E'
ORDER BY acct_session_id ASC, timestamp ASC
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
