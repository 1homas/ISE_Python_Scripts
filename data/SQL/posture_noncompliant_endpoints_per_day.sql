-- From the ISE Data Connect Guides' Posture Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
-- Posture > Number of Non-Compliant Devices per day
SELECT TRUNC(timestamp),
    count(distinct username)
FROM posture_assessment_by_endpoint
WHERE posture_status = 'NonCompliant'
GROUP BY TRUNC(timestamp)
ORDER BY TRUNC(timestamp) desc;