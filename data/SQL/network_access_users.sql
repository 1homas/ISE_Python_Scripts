--
-- network_access_users
--
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
--

SELECT
    * -- all columns
    -- username,
    -- status,
    -- account_name_alias,
    -- alarm_emailable
    -- allow_password_change_after_login,
    -- current_successful_login_time,
    -- description,
    -- email_address,
    -- expiry_date_enabled,
    -- expiry_date,
    -- failed_login_ipaddress,
    -- first_name,
    -- id,
    -- identity_group,
    -- is_admin,
    -- last_name,
    -- last_successful_login_time,
    -- last_unsuccessful_login_time,
    -- password_last_updated_on,
    -- password_never_expires,
    -- success_login_ipaddress,
FROM network_access_users
-- FETCH FIRST 10 ROWS ONLY -- limit default number of rows returned for large datasets
