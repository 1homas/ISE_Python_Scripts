-- ISE Reports > Threat-Centric NAC > Adapter-status
SELECT *
    -- logged_at, -- timeSTAMP(6) Shows the time when the syslog was processed and stored by the Monitoring node
    -- status, -- Specifies the adapter status
    -- id, -- Unique database ID
    -- adapter_name, -- Specifies the adapter name
    -- connectivity, -- Specifies the connectivity
FROM adapter_status
-- FETCH FIRST 10 ROWS ONLY