-- From the ISE Data Connect Guides' Profiling Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
-- Profiling > Number of Profiled Endpoints filtered by Endpoint Profile
SELECT endpoint_profile,
  COUNT(endpoint_profile)
FROM profiled_endpoints_summary
GROUP BY endpoint_profile