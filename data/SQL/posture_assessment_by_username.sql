--
-- Posture Assessment by Username
--

SELECT
  username,
  COUNT(*)
  -- system_domain, -- Displays the domain name of the endpoint
  -- system_user, -- Displays the system user
  -- system_user_domain, -- Displays the system user domain
  -- ip_address, -- IP address of the endpoint
  -- pra_grace_time, -- Periodic reassessment grace time configured
  -- nad_location, -- Location of NAD
  -- am_installed, -- Displays the anti-malware installed on the endpoint
  -- message_text, -- Displays the message text
  -- id, -- database unique ID
  -- timestamp_timezone, -- timeSTAMP(6) WITH TIME ZONE Time with timezone when record added
  -- timestamp, -- timestamp(6) Time when record added
  -- ise_node, -- Hostname of ISE node
  -- message_code, -- Displays the message code of the posture syslog
  -- request_time, -- Displays the request time
  -- response_time, -- Displays the response time
  -- endpoint_mac_address, -- MAC address of the endpoint
  -- endpoint_operating_systeM, -- Operating system of the endpoint
  -- posture_agent_version, -- Displays the version of the posture agent
  -- posture_status, -- Posture status i.e. pending, compliant, non-compliant etc
  -- posture_policy_matched, -- Displays the posture policy matched
  -- posture_report, -- Displays the posture report
  -- anti_virus_installed, -- Displays the installed anti-virus
  -- anti_spyware_installed, -- Displays the installed anti-spyware
  -- failure_reason, -- Specifies the reason for failure
  -- pra_enforcement_flag, -- Displays the status of periodic reassessment enforcement
  -- pra_interval, -- Periodic reassessment interval configured
  -- pra_action, -- Periodic reassessment action configured
  -- username, -- Displays the username
  -- session_id, -- Shows the session ID
  -- feed_url, -- Shows the update feed URL
  -- num_of_updates, -- Number of updates
  -- user_agreement_status, -- Displays the status of the user agreement
  -- system_name, -- Hostname of the endpoint

FROM posture_assessment_by_endpoint
-- WHERE timestamp > '24-May-22 04.00.00 PM'
GROUP BY username
ORDER BY username ASC