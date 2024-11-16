--
-- user_password_changes
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- timestamp_timezone,
    -- timestamp,
    -- ise_node,
    -- message_code,
    -- admin_name,
    -- admin_ip_address,
    -- admin_ipv6_address,
    -- admin_interface,
    -- message_class,
    -- message_text,
    -- operator_name,
    -- user_admin_flag,
    -- account_name,
    -- device_ip,
    -- identity_store_name,
    -- change_password_method,
    -- audit_password_type
FROM user_password_changes
ORDER BY timestamp ASC -- first/oldest records
-- ORDER BY timestamp DESC -- most recent records
FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
