SELECT *
    -- edda_id, -- The unique identifier as specified in the connector configuration
    -- connector_type, -- The connector type as specified in the connector configuration
    -- create_time, -- The time when record created
    -- bulk_id, -- The Bulk ID
    -- version, -- The connector version
    -- version_type, -- The connector version type
    -- name, -- The connector name
    -- data, -- The data parsed by the connector in JSON format
FROM pxgrid_direct_data
-- FETCH FIRST 10 ROWS ONLY
