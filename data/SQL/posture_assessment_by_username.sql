SELECT username,
  COUNT(*)
FROM posture_assessment_by_endpoint
-- WHERE timestamp > '24-May-22 04.00.00.000000000 PM'
GROUP BY username