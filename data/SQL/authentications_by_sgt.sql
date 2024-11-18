--
-- RADIUS Authentications by SGT
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    security_group,
    MAX(calling_station_id) AS calling_station_id,
    MAX(framed_ip_address) AS ipv4,
    MAX(username),
    MAX(timestamp) AS timestamp,
    MAX(passed)
FROM radius_authentications
WHERE passed = 'Pass'
GROUP BY security_group,
    calling_station_id
    -- framed_ip_address,
    -- username,
    -- passed
ORDER BY security_group ASC,timestamp DESC
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
