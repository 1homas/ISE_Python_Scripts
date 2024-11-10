SELECT
    -- id,
    timestamp,
    -- event_timestamp, -- The date and time that this event occurred on the NAS
    -- timestamp_timezone,
    -- audit_session_id,
    acct_session_id AS session_id, -- Unique numeric string identifying the server session
    acct_status_type AS status, -- Specifies whether accounting packet starts or stops a bridging, routing, or terminal server session.
    syslog_message_code AS code, -- 3000=Acct-Start, 3001=Acct-Stop, 3002=Interim-Update, 3003=Acct-On, 3004=Acct-Off
    acct_session_time AS duration, -- Length of time (in seconds) for which the session has been logged in
    acct_input_octets AS oct_in, -- Number of octets received during the session
    acct_output_octets AS oct_out, -- Number of octets sent during the session
    acct_input_packets AS pack_in, -- Number of packets received during the session
    acct_output_packets AS pack_out, -- Number of octets sent during the session
    -- access_service, -- ISE Allowed Protocls
    -- acct_multi_session_id,
    -- acct_interim_interval, -- Number of seconds between each transmittal of an interim update for a specific session
    acct_terminate_cause AS termination, -- Reason a connection was terminated
    -- session_id, -- ⚠ very long string
    -- started,
    -- stopped,
    calling_station_id AS MAC,
    -- framed_ipv6_address,
    -- framed_ip_address,
    username,
    device_name -- ISE network device name
    -- nas_ip_address, -- The IP address of the NAS originating the request
    -- nas_ipv6_address,
    -- nas_identifier,
    -- nas_port, -- Physical port number of the NAS (Network Access Server) originating the request
    -- nas_port_id, -- If provided by NAS
    -- device_groups,
    -- ise_node, -- ISE node name
    -- identity_store,
    -- ad_domain,
    -- framed_protocol,
    -- service_type, -- RADIUS Service Type: Framed, Call-Check, etc.
    -- response_time, -- in milliseconds
    -- failure_reason,
    -- security_group AS SGT, -- ⚠ empty
    -- idle_timeout,
    -- vn,
    -- cisco_h323_setup_time,
    -- cisco_h323_connect_time,
    -- cisco_h323_disconnect_time,
    -- acct_delay_time AS delay, -- always 0? Length of time (in seconds) for which the NAS has been sending the same accounting packet
    -- acct_tunnel_connection, -- ⚠ empty
    -- acct_tunnel_packet_lost, -- ⚠ empty
    -- service_selection_policy,
    -- acct_authentic,
    -- user_type,
    -- identity_group,
    -- authorization_policy,
    -- termination_action,
    -- session_timeout
FROM radius_accounting
-- WHERE username = 'thomas' AND acct_status_type = 'Stop'
ORDER BY timestamp
-- FETCH FIRST 100 ROWS ONLY
-- FETCH NEXT 50 ROWS ONLY
