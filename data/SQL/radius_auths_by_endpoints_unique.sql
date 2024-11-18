--
--  RADIUS Authentication Summary by Endpoints
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT DISTINCT calling_station_id,
  MAX(username) as username,
  SUM(passed_count) AS passed,
  SUM(failed_count) AS failed,
  SUM(passed_count) + SUM(failed_count) AS total,
  ROUND( (SUM(failed_count) / (SUM(passed_count) + SUM(failed_count)) * 100), 2) AS failed_pct,
  ROUND(SUM(total_response_time) / (SUM(passed_count) + SUM(failed_count)), 2) AS total_response_time,
  MAX(max_response_time) AS max_response_time
  -- timestamp, -- timestamp(6)  Time when record added
  -- ise_node, -- Name of the ISE server used for authentication
  -- username, -- User name
  -- calling_station_id, -- Mac address of the device the user is using
  -- identity_store, -- The Identity Store to which the user authenticated belongs to. Example - Internal Endpoints
  -- identity_group, -- The Identity Group to which the user belongs to. Example - Windows11-Workstation
  -- device_name, -- The name of the network device used by the user to access network. Example - 9800CLWLC, Access-Switch-3K, 9800VWLC etc.
  -- device_type, -- The type of the network device used by the user to access network. Example - Wireless - IEEE 802.11
  -- location, -- The location hierarchy of the the network device. Example - All Locations#My-Territory#US#Sanjose#BLDG5
  -- access_service, -- The protocol used for authentication. Example - NDAC_SGT_Service, Default Network Access
  -- nas_port_id, -- ID of the NAD Port used. Example - GigabitEthernet1/0/14
  -- authorization_profiles, -- The authorization profile applied. Example - PermitAccess, Machine-Access
  -- failure_reason, -- Reason for the failure, in case authentication was not successful
  -- security_group, -- The security group classification of the device i.e the source SGT. Example - TrustedDevices, Quarantined_Systems
  -- total_response_time, -- The total response time required for authentication
  -- max_response_time, -- The maximum response time required for authentication
  -- passed_count, -- The number of passed authentication
  -- failed_count, -- Number of failed authentication
FROM radius_authentication_summary
GROUP BY calling_station_id
ORDER BY calling_station_id ASC
