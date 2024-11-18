--
-- From the ISE Data Connect Guides' RADIUS Authentication Summary Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
--

SELECT access_service AS allowed_protocol,
  SUM(passed_count) AS passed,
  SUM(failed_count) AS failed,
  SUM(passed_count) + SUM(failed_count) AS total,
  ROUND( (SUM(failed_count) / (SUM(passed_count) + SUM(failed_count)) * 100), 2) AS failed_pct,
  ROUND(SUM(total_response_time) / (SUM(passed_count) + SUM(failed_count)), 2) AS total_response_time,
  MAX(max_response_time) AS max_response_time
FROM radius_authentication_summary
GROUP BY access_service