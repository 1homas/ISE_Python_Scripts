-- ISE System Summary Daily

SELECT TRUNC(timestamp, 'DD') AS datetime,
  MAX(ise_node) AS node,
  AVG(cpu_utilization) AS cpu_avg,
  MAX(cpu_utilization) AS cpu_max,
  MAX(cpu_count) AS cpus,
  AVG(memory_utilization) AS mem_avg,
  MAX(memory_utilization) AS mem_max
  --   MAX(diskspace_root),
  --   MAX(diskspace_boot),
  --   MAX(diskspace_opt),
  --   MAX(diskspace_storedconfig),
  --   MAX(diskspace_tmp),
  --   MAX(diskspace_runtime)
FROM system_summary
GROUP BY TRUNC(timestamp, 'DD'),
  ise_node
ORDER BY TRUNC(timestamp, 'DD') ASC
-- FETCH FIRST 10 ROWS ONLY
