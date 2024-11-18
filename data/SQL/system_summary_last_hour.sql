--
-- system_summary for the past 1 hour
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
WHERE timestamp > sysdate - INTERVAL '1' HOUR
    -- AND ise_node = 'ise-ppan'
ORDER BY timestamp ASC
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
