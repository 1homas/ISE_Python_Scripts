--
-- ISE System (Nodes) Summary for the Last 1 hour
--
-- Author: Thomas Howard, thomas@cisco.com
-- License: MIT - https://mit-license.org
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    -- * -- all columns
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    ise_node AS ise_node, -- 
    cpu_count AS cpus, -- 
    TO_CHAR(cpu_utilization, 'fm999D00') || '%' AS cpu_util, -- 
    TO_CHAR(memory_utilization, '999D00') || '%' AS memory_disk , -- 
    TO_CHAR(diskspace_root, 'fm999') || '%' AS root_disk , -- 
    TO_CHAR(diskspace_boot, 'fm999') || '%' AS boot_disk , -- 
    TO_CHAR(diskspace_opt, 'fm999') || '%' AS opt_disk , -- 
    TO_CHAR(diskspace_storedconfig, 'fm999') || '%' AS config_disk , -- 
    TO_CHAR(diskspace_tmp, 'fm999') || '%' AS tmp_disk  -- 
    -- TO_CHAR(diskspace_runtime, 'fm990D99') || '%' AS runtime_disk ,
FROM system_summary
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
-- WHERE timestamp > sysdate - INTERVAL '1' DAY -- last N days
    -- AND ise_node = 'ise-ppan'
ORDER BY timestamp ASC
-- FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
