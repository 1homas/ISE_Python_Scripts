--
-- system_summary
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- timestamp,
    -- ise_node,
    -- cpu_utilization,
    -- cpu_count,
    -- memory_utilization,
    -- diskspace_root,
    -- diskspace_boot,
    -- diskspace_opt,
    -- diskspace_storedconfig,
    -- diskspace_tmp,
    -- diskspace_runtime
FROM system_summary
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
ORDER BY timestamp ASC -- first/oldest records
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
