-- From the ISE Data Connect Guides' RADIUS Authentication Summary Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
SELECT failure_reason,
  SUM(passed_count) AS passed,
  SUM(failed_count) AS failed,
  SUM(passed_count) + SUM(failed_count) AS total
FROM radius_authentication_summary
WHERE failure_reason IS NOT NULL
GROUP BY failure_reason
ORDER BY total DESC