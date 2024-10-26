-- From the ISE Data Connect Guides' Posture Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
-- Posture > Non Complaint Users with Date
SELECT TRUNC(timestamp),
    username
FROM posture_assessment_by_endpoint
WHERE posture_status = 'NonCompliant';