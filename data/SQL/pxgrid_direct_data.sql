--
-- pxgrid_direct_data
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- edda_id, -- The unique identifier as specified in the connector configuration
    -- connector_type, -- The connector type as specified in the connector configuration
    -- create_time, -- The time when record created
    -- bulk_id, -- The Bulk ID
    -- version, -- The connector version
    -- version_type, -- The connector version type
    -- name, -- The connector name
    -- data, -- The data parsed by the connector in JSON format
FROM pxgrid_direct_data
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
