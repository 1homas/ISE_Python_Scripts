--
-- endpoint_purge_view
-- Show the history of endpoints purge activities.
--

SELECT
  * -- all columns
  -- id, -- database unique ID
  -- endpoint_purge_id, -- endpoint purge ID ??
  -- run_time, -- when
  -- TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- time when record added; drop fractional seconds
  -- profiler_server, -- profiler server
  -- endpoint_purge_rule, -- endpoint purge rule
  -- endpoint_count -- number of endpoints purged
FROM endpoint_purge_view
ORDER BY endpoint_purge_id
