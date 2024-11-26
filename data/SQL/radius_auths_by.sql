--
-- RADIUS Authentications by ...
-- There are many ways to perform a GROUP BY on the radius_authentications table!
-- Rather than create a separate SQL file for each one, un/comment lines to quickly customize queries.
-- Remember the last SELECT column must not end with a `,`.
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--

SELECT
    -- 💡 Group by one or more of these attributes

    TO_CHAR(timestamp, 'YYYY-MM-DD') AS timestamp, -- by day
    -- TO_CHAR(timestamp, 'YYYY-MM-DD HH24') AS timestamp, -- by hour
    -- TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI') AS timestamp, -- by minute

    -- access_service AS allowed_protocol,
    -- calling_station_id AS mac,
    -- device_name,
    -- device_name, location,
    -- device_type,
    -- failure_reason,
    -- identity_group,
    -- identity_store,
    -- nas_port_type,
    -- username,
    -- ise_node,

    -- 💡 Metrics for the group
    COUNT(CASE WHEN passed = 'Pass' THEN 1 END) AS passed,
    COUNT(CASE WHEN passed = 'Fail' THEN 1 END) AS failed,
    COUNT(timestamp) AS total,
    TO_CHAR(ROUND( (COUNT(CASE WHEN passed = 'Fail' THEN 1 END) / (COUNT(CASE WHEN passed = 'Pass' THEN 1 END) + COUNT(CASE WHEN passed = 'Fail' THEN 1 END)) * 100), 0), 'FM999') || '%' AS fail_pct,
    -- ROUND(AVG(response_time), 0) AS avg_resp_ms, -- milliseconds
    ROUND(MEDIAN(response_time), 0) AS median_resp_ms, -- milliseconds
    MAX(response_time) AS max_resp_ms -- milliseconds
FROM radius_authentications
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days

GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD') -- by day
-- GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD HH24') -- by hour
-- GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI') -- by minute
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records

-- GROUP BY failure_reason
-- ORDER BY failure_reason ASC

-- GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD'), ise_node
-- ORDER BY
--     TO_CHAR(timestamp, 'YYYY-MM-DD') ASC,
--     ise_node ASC

-- GROUP BY username,calling_station_id
-- ORDER BY username ASC,calling_station_id ASC

-- GROUP BY device_name
-- ORDER BY device_name ASC

-- GROUP BY device_name, location
-- ORDER BY device_name ASC, location ASC
