--
-- Compliant Endpoints per Day
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    -- * 
    TO_CHAR(timestamp, 'YYYY-MM-DD') AS day, -- date only
    COUNT(DISTINCT username) AS count -- 
    -- am_installed, -- anti-malware installed on the endpoint
    -- anti_spyware_installed, -- installed anti-spyware
    -- anti_virus_installed, -- installed anti-virus
    -- endpoint_mac_address, -- mac address of the endpoint
    -- endpoint_operating_system, -- operating system of the endpoint
    -- failure_reason, -- reason for failure
    -- feed_url, -- update feed url
    -- id 	number 	database unique id
    -- ip_address, -- ip address of the endpoint
    -- ise_node, -- hostname of ise node
    -- message_code, -- message code of the posture syslog
    -- message_text, -- message text
    -- nad_location, -- location of nad
    -- num_of_updates 	number 	number of updates
    -- posture_agent_version, -- version of the posture agent
    -- posture_policy_matched, -- posture policy matched
    -- posture_report 	clob 	posture report
    -- posture_status, -- posture status i.e. pending, compliant, non-compliant etc
    -- pra_action, -- periodic reassessment action configured
    -- pra_enforcement_flag 	number 	status of periodic reassessment enforcement
    -- pra_grace_time, -- periodic reassessment grace time configured
    -- pra_interval 	number 	periodic reassessment interval configured
    -- request_time, -- request time
    -- response_time, -- response time
    -- session_id, -- session id
    -- system_domain, -- domain name of the endpoint
    -- system_name, -- hostname of the endpoint
    -- system_user_domain, -- system user domain
    -- system_user, -- system user
    -- timestamp, -- stime when record added
    -- timestamp_timezone, -- stimestamp(6) with time zone 	time with timezone when record added
    -- user_agreement_status, -- status of the user agreement
    -- username, -- username
FROM posture_assessment_by_endpoint
-- WHERE posture_status = 'Compliant'
GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD')
ORDER BY day DESC