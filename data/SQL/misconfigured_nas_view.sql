--
-- misconfigured_nas_view
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- timestamp, -- time when record added
    -- calling_station_id, -- calling station id
    -- nas_ip_address, -- ip address of nas
    -- nas_ipv6_address, -- nas ipv6 address
    -- timestamp_timezone, -- time with timezone when record added
    -- detail_info, -- displays the detailed info
    -- failed_attempts, -- failed attempts
    -- failed_times_hours, -- failed times in hours
    -- failed_times, -- failed times
    -- id, -- database unique id
    -- ise_node, -- displays the hostname of the ise server
    -- message_code, -- displays the message code
    -- message_text, -- displays the message text
    -- other_attributes, -- other attributes
FROM misconfigured_nas_view
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
