SELECT *
    -- id,
    -- timestamp_timezone,
    -- timestamp,
    -- ise_node,
    -- message_severity,
    -- message_code,
    -- message_text,
    -- category,
    -- diagnostic_info
FROM system_diagnostics_view
FETCH FIRST 10 ROWS ONLY