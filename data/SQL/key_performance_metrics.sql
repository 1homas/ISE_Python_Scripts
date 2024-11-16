--
-- _____
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- avg_latency_per_req,
    -- avg_load,
    -- avg_tps,
    -- ise_node,
    -- logged_time,
    -- logged_to_mnt_hr,
    -- max_load,
    -- noise_hr,
    -- radius_requests_hr,
    -- suppression_hr,
FROM key_performance_metrics
-- ORDER BY logged_time ASC -- first/oldest records
ORDER BY logged_time DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
