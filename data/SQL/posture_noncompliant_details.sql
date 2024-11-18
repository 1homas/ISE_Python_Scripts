--
-- From the ISE Data Connect Guides' Posture Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
-- Posture > Details of non-compliant posture
--

SELECT
    * -- all columns
FROM posture_assessment_by_condition
WHERE enforcement_type = 'Mandatory'
    AND posture_status = 'NonCompliant'
    AND policy_status = 'Failed';