-- From the ISE Data Connect Guides' Posture Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
-- Posture > Number of times a user becomes compliant and non-compliant
SELECT *
FROM (
        SELECT username,
            posture_status
        FROM posture_assessment_by_endpoint
    ) pivot (
        count(posture_status) for posture_status in ('Compliant', 'NonCompliant')
    );