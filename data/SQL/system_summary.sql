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
ORDER BY timestamp ASC -- first/oldest records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
