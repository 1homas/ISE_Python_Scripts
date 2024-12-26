--
-- adapter_status
-- Adapter Status Report.
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT 
  * -- all columns
  -- logged_at, --  shows the time when the syslog was processed and stored by the Monitoring node
  -- status, -- specifies the adapter status
  -- id, --  unique database ID
  -- adapter_name, specifies the adapter name
  -- connectivity, -- specifies the connectivity
FROM adapter_status
ORDER BY
  logged_at ASC
  -- adapter_name ASC
