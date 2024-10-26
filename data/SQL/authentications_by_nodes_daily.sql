SELECT TRUNC(timestamp) DAY,
  ise_node,
  -- device_name,
  -- passed, -- 'Fail' for username='INVALID'
  -- failed, -- '1' for username='INVALID'
  SUM(
    CASE
      WHEN failed = '0' THEN 1
    END
  ) AS passed,
  SUM(
    CASE
      WHEN failed = '1' THEN 1
    END
  ) AS failed,
  SUM(
    CASE
      WHEN failed = '0' THEN 1
    END
  ) + SUM(
    CASE
      WHEN failed = '1' THEN 1
    END
  ) AS total,
  ROUND(
    to_char(
      (
        (
          SUM(
            CASE
              WHEN failed = '1' THEN 1
            END
          ) / (
            SUM(
              CASE
                WHEN failed = '0' THEN 1
              END
            ) + SUM(failed)
          )
        ) * 100
      )
    ),
    0
  ) AS fail_pct,
  MAX(response_time) AS max_resp_time -- ⓘ Request
  -- audit_session_id,
  -- syslog_message_code,
  -- failure_reason,
  -- response_time,
  -- checksum
  -- ⓘ Endpoint
  -- calling_station_id,
  -- framed_ip_address,
  -- orig_calling_station_id,
  -- framed_ipv6_address,
  -- ⓘ User
  -- username,
  -- user_type, -- blank?
  -- id,
  -- service_type,
  -- access_service, -- Allowed Protocols
  -- ⓘ NAD
  -- device_name,
  -- device_type, -- NDG
  -- location, -- NDG
  -- nas_ip_address,
  -- nas_port_id,
  -- nas_port_type,
  -- nas_ipv6_address,
  -- ⓘ Auth
  -- identity_store,
  -- identity_group,
  -- authentication_method,
  -- authentication_protocol,
  -- credential_check -- Auth protocol?
  -- ⓘ Policy
  -- policy_set_name -- Default, Wired, etc.
  -- authorization_rule, -- 💡 Blank for failed auths!
  -- authorization_profiles, -- 💡 Blank for failed auths!
  -- security_group, -- 💡 Blank for failed auths!
  -- response_time
  -- 💡 Blank for failed auths!
  -- posture_status,
  -- mdm_server_name,
FROM radius_authentications
GROUP BY TRUNC(timestamp),
  ise_node
ORDER BY TRUNC(timestamp),
  ise_node ASC
-- FETCH FIRST 10 ROWS ONLY