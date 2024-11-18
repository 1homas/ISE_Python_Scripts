--
-- From the ISE Data Connect Guides' Profiling Examples
-- https://developer.cisco.com/docs/dataconnect/guides/#radius-authentication-summary
-- Profiling > Number of different endpoint profiles profiled per endpoint sources
--

SELECT
    * -- all columns
FROM (
    SELECT source,
      endpoint_profile
    FROM profiled_endpoints_summary
  ) pivot (
    COUNT(endpoint_profile) for endpoint_profile in (
      'Cisco-Device',
      'Macintosh-Workstation',
      'Microsoft-Workstation',
      'RedHat-Workstation',
      'VMWare-Device',
      'Windows10-Workstation',
      'Windows11-Workstation',
      'Xerox-Device'
    )
  )