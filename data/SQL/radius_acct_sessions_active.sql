--
-- List All Cisco ISE Sessions by ID that are Active.
-- 💡 Un/Comment columns to quickly customize queries. Remember the last SELECT column must not end with a `,`.
-- Session states are in the `ℹ` column: □ stopped, ! ghosted, ⧖ interim, ▷ started
--
-- All Active RADIUS Accounting sessions consume a license until a RADIUS Accounting Stop is received or the session is cleared in ISE.
-- A RADIUS session is Active/Started if:
--   - there is a RADIUS Accounting Start record (syslog_message_code = 3000 OR acct_status_type = 'Start') with an acct_session_id
--   - the acct_session_id does not have a corresponding Stop record (syslog_message_code = 3001 OR acct_status_type = 'Stop')
--   - the last update is < 5 days old
--   ⓘ there may 0 or more Interim-Updates (syslog_message_code = 3002 or acct_status_type = Interim-Update) to maintain a session
-- ⚠ If a device is [unintentionally] powered off or accounting is mis/unconfigured, it's sessions' may become stale in ISE.
-- ⓘ RADIUS Accounting sessions without updates every 24 hours are generally considered as 'ghosted' 👻
-- ⓘ ISE clears any session after five days of inactivity (no further RADIUS Accounting updates for that acct_session_id).
-- ⓘ RADIUS Accounting Interim-Updates may contain IPv4/v6 address changes for the given sessions
-- ⓘ Cisco WLC uses an Accounting-Stop with a 'nas-update=true' attribute to identify a session in a roaming state.
--    When ISE sees this attribute, the session is not deleted in ISE to avoid reauthentication.
--    If roaming fails, ISE clears the session after five days of inactivity.
--

SELECT
    acct_session_id,
    TO_CHAR(MIN(timestamp), 'YYYY-MM-DD HH24:MI:SS') AS started, -- drop fractional seconds
    TO_CHAR(MAX(timestamp), 'YYYY-MM-DD HH24:MI:SS') AS stopped, -- drop fractional seconds
    MAX(syslog_message_code) AS code, -- 3000=Acct-Start, 3001=Acct-Stop, 3002=Interim-Update, 3003=Acct-On, 3004=Acct-Off
    COUNT(timestamp) AS num, -- total accounting updates 
    CASE WHEN MAX(syslog_message_code) = 3001 THEN '□' WHEN (MAX(timestamp) < (SYSDATE - 1)) THEN '!' WHEN MAX(syslog_message_code) = '3002' THEN '⧖'  ELSE '▷' END AS ℹ, -- [□ stopped, ! ghosted, ⧖ interim, ▷ started] alternatives: ▷ | □ ⏹ ⚠ ! ◌ ⍉ ⬚ ◯ ▶ ◻ □ ○ ◌
    NVL(MAX(acct_session_time), 0) AS time, -- time (seconds) for which the session has been Started
    MAX(calling_station_id) AS mac, -- endpoint MAC address (00:00:00:00:00:00)
    MAX(username) AS username, -- username or MAC (00-00-00-00-00-00)
    MAX(acct_terminate_cause) AS termination, -- Reason a connection was terminated
    MAX(device_name) AS device_name, -- ISE device name
    MAX(response_time) as resp_ms
    -- MIN(event_timestamp) AS nas_timestamp, -- seconds since epoch that this event occurred on the NAS
    -- MIN(syslog_message_code) AS min_code, -- 3000=Acct-Start, 3001=Acct-Stop, 3002=Interim-Update, 3003=Acct-On, 3004=Acct-Off
    -- MAX(syslog_message_code) INTO last_msg,
    -- NVL(MAX(acct_session_time), ((CAST(SYSTIMESTAMP AS DATE) - (CAST(MIN(timestamp) AS DATE))) * 86400)) AS duration, -- calculate time (seconds) since the session Started
    -- MAX(session_id), -- very long string (8a37ff0600001811672d50d2:ise-span/519859596/4561)
    -- MAX(user_type) AS user_type, -- ⚠ empty
    -- MIN(acct_status_type) AS status_min, -- [Interim-Update, Start, Stop]
    -- MAX(acct_status_type) AS status_max, -- [Interim-Update, Start, Stop]
FROM radius_accounting
WHERE syslog_message_code != 3003 AND syslog_message_code != 3004 -- ignore Accounting-On/Off messages
GROUP BY acct_session_id
HAVING MAX(syslog_message_code) != 3001
-- ORDER BY MIN(timestamp) ASC
ORDER BY MIN(timestamp) DESC
-- ORDER BY NVL(MAX(acct_session_time), 0) DESC, MIN(timestamp) ASC -- longest sessions
FETCH FIRST 50 ROWS ONLY -- limit default number of rows returned for large datasets
