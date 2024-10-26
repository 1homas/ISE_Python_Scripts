SELECT *
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
ORDER BY timestamp ASC
-- FETCH FIRST 10 ROWS ONLY