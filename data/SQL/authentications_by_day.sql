SELECT TRUNC(timestamp) DAY,
  SUM(passed_count) AS Passed,
  SUM(failed_count) AS Failed,
  SUM(passed_count) + SUM(failed_count) as Total
FROM radius_authentication_summary
GROUP BY TRUNC(timestamp)
ORDER BY DAY DESC