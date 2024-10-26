SELECT posture_agent_version,
  endpoint_mac_address
FROM (
    SELECT DISTINCT posture_agent_version,
      endpoint_mac_address
    FROM posture_assessment_by_endpoint
  )
WHERE endpoint_mac_address IS NOT NULL
  and posture_agent_version IS NOT NULL
ORDER BY posture_agent_version