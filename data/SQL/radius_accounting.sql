SELECT timestamp,
    -- event_timestamp,
    -- id,
    -- audit_session_id,
    acct_session_id,
    acct_input_octets AS octets_in,
    acct_output_octets AS octets_out,
    acct_input_packets AS packets_in,
    acct_output_packets AS packets_out,
    access_service,
    -- acct_multi_session_id,
    -- acct_interim_interval,
    acct_status_type AS status,
    acct_session_time AS session_time,
    acct_terminate_cause AS termination,
    -- SESSION_ID,
    -- started,
    -- stopped,
    -- **Endpoint**               ,
    calling_station_id,
    -- framed_ipv6_address,
    framed_ip_address,
    -- **User**                   ,
    username,
    -- **NAS**                    ,
    device_name,
    -- device_groups,
    nas_ip_address,
    -- nas_ipv6_address,
    nas_identifier,
    nas_port,
    nas_port_id,
    -- **Policy**                 ,
    ise_node,
    -- identity_store,
    -- ad_domain,
    -- framed_protocol,
    service_type,
    response_time,
    failure_reason,
    syslog_message_code,
    -- **Security**               ,
    security_group AS SGT -- idle_timeout,
    -- vn,
    -- cisco_h323_setup_time,
    -- cisco_h323_connect_time,
    -- cisco_h323_disconnect_time,
    --
    -- **🐞 Always empty?**       ,
    --
    -- acct_delay_time AS delay, -- always 0?
    -- acct_tunnel_connection, -- empty
    -- acct_tunnel_packet_lost, -- empty
    -- service_selection_policy,
    -- acct_authentic,
    -- user_type,
    -- identity_group,
    -- authorization_policy,
    -- termination_action,
    -- session_timeout
FROM radius_accounting
ORDER BY timestamp
FETCH FIRST 10 ROWS ONLY
-- FETCH NEXT 50 ROWS ONLY