--
-- ISE Reports > Threat-Centric NAC > Adapter-status
--

SELECT
    * -- all columns
    -- logged_at, -- timeSTAMP(6) Shows the time when the syslog was processed and stored by the Monitoring node
    -- status, -- Specifies the adapter status
    -- id, -- Unique database ID
    -- adapter_name, -- Specifies the adapter name
    -- connectivity, -- Specifies the connectivity
FROM adapter_status
ORDER BY logged_at ASC -- first/oldest records
-- ORDER BY logged_at DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets