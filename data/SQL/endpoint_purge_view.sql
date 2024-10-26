SELECT id,
    endpoint_purge_id,
    run_time,
    timestamp,
    profiler_server,
    endpoint_purge_rule,
    endpoint_count
FROM endpoint_purge_view
ORDER BY endpoint_purge_id
-- FETCH FIRST 10 ROWS ONLY