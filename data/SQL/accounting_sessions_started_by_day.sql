SELECT
    TRUNC(timestamp) AS datetime,
    COUNT(*)
FROM radius_accounting
WHERE started = 1 and stopped = 0
GROUP BY TRUNC(timestamp)
ORDER BY TRUNC(timestamp) ASC