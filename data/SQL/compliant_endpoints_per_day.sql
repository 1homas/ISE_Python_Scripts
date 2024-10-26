SELECT TRUNC(timestamp),
  COUNT(distinct username)
FROM posture_assessment_by_endpoint
WHERE posture_status = 'Compliant'
GROUP BY TRUNC(timestamp)
ORDER BY TRUNC(timestamp) DESC