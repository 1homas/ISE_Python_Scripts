--
-- key_performance_metrics
-- Shows details of ISE nodes' key performance metrics (KPM) like average TPS, average load etc.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- avg_latency_per_req, -- average latency per RADIUS request for PSN node
    -- avg_load, -- average load for node
    -- avg_tps, -- average transactions per second ???
    -- ise_node, -- ISE Node
    -- logged_time, -- logged timestamp
    -- logged_to_mnt_hr, -- requests logged to MNT database for PSN node
    -- max_load, -- maximum load for node
    -- noise_hr, -- difference between RADIUS requests and logged to MnT per hour ???
    -- radius_requests_hr, -- radius requests per hour for PSN node
    -- suppression_hr,
FROM key_performance_metrics
-- WHERE logged_time > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE logged_time > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE logged_time > sysdate - INTERVAL '1' HOUR -- last N hours
WHERE logged_time > sysdate - INTERVAL '1' DAY -- last N days
ORDER BY logged_time ASC -- first/oldest records
-- ORDER BY logged_time DESC -- most recent records
