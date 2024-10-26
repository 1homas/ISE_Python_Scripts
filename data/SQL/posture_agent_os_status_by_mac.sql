SELECT posture.posture_agent_version,
  posture.endpoint_mac_address,
  posture.endpoint_operating_system,
  posture.posture_status
FROM posture_assessment_by_endpoint posture
  INNER JOIN (
    SELECT endpoint_mac_address,
      MAX(timestamp) as timestamp
    FROM posture_assessment_by_endpoint
    GROUP BY endpoint_mac_address
  ) latest_records ON posture.endpoint_mac_address = latest_records.endpoint_mac_address
  AND posture.timestamp = latest_records.timestamp
ORDER BY posture.posture_agent_version