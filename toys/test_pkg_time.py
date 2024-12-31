#!/usr/bin/env python3
"""
Test script to demonstrate the uses of the Python `time` module for various time-related functions.
"""
__author__ = "Thomas Howard"
__email__ = "1@1homas.org"
__license__ = "MIT - https://mit-license.org/"

import time  # do not confuse this time with datetime.time!

EPOCH = time.gmtime(0)

t_now = time.time()  # float
gmtime_now = time.gmtime()
localtime_now = time.localtime()


print(
    f"""

-------------------------------------------------------------------------------
Terminology
-------------------------------------------------------------------------------

The epoch is the point where the time starts, the return value of time.gmtime(0).
It is January 1, 1970, 00:00:00 (UTC) on all platforms.
The cut-off point in the future is determined by the C library; for 32-bit systems, it is typically in 2038.

EPOCH = time.gmtime(0) | { time.gmtime(0) }


UTC
UTC is Coordinated Universal Time (formerly known as Greenwich Mean Time, or GMT).
The acronym UTC is not a mistake but a compromise between English and French.

time.gmtime()    | { time.gmtime() } # GMT == UTC
time.localtime() | { time.localtime() } current local time
time.time()      | { time.time() } # current local time


DST
DST is Daylight Saving Time, an adjustment of the timezone by (usually) one hour during part of the year.
DST rules are magic (determined by local law) and can change from year to year.
The C library has a table containing the local rules (often it is read from a system file for flexibility) and is the only source of True Wisdom in this respect.


-------------------------------------------------------------------------------
Time Constants
-------------------------------------------------------------------------------

time.altzone  | { time.altzone  } | The offset of the local DST timezone, in seconds west of UTC, if one is defined. This is negative if the local DST timezone is east of UTC (as in Western Europe, including the UK). Only use this if daylight is nonzero.
time.daylight | { time.daylight } | Nonzero if a DST timezone is defined.
time.timezone | { time.timezone } | The offset of the local (non-DST) timezone, in seconds west of UTC (negative in most of Western Europe, positive in the US, zero in the UK).
time.tzname   | { time.tzname   } | A tuple of two strings: the first is the name of the local non-DST timezone, the second is the name of the local DST timezone. If no DST timezone is defined, the second string should not be used.

"""
)

print(
    f"""

-------------------------------------------------------------------------------
Functions
-------------------------------------------------------------------------------

Return the time in seconds since the epoch as a floating-point number. 
Use localtime() or gmtime() for a more common time format (i.e. year, month, day, hour, etc…) in UTC

| time.time() | { time.time() }

| time.asctime([t]) | Convert a tuple or struct_time representing a time as returned by gmtime() or localtime() to a string of the following form: 'Sun Jun 20 23:21:05 1993'.
| time.asctime()    | { time.asctime() } # uses localtime by default
| time.asctime([t]) | { time.asctime(localtime_now) } # Tuple or struct_time argument required

| time.ctime([secs]) | Convert a time expressed in seconds since the epoch to a string of a form: 'Sun Jun 20 23:21:05 1993' representing local time.
| time.ctime()       | { time.ctime() }
| time.ctime(1)      | { time.ctime(1) }

| time.gmtime([secs]) | Convert a time expressed in seconds since the epoch to a struct_time in UTC in which the dst flag is always zero. 
| time.gmtime()       | { time.gmtime() }
| time.gmtime(1)      | { time.gmtime(1) }

| time.localtime([secs]) | Like gmtime() but converts to local time. If secs is not provided or None, the current time as returned by time() is used. The dst flag is set to 1 when DST applies to the given time.
| time.localtime() | { time.localtime() }
| time.localtime(1) | { time.localtime(1) }

| time.mktime(t) | Inverse function of localtime(). Its argument is the struct_time or full 9-tuple (since the dst flag is needed; use -1 as the dst flag if it is unknown) which expresses the time in local time, not UTC. It returns a floating-point number, for compatibility with time(). 
| time.mktime(localtime_now) | { time.mktime(localtime_now) } # Tuple or struct_time argument required

| time.sleep(secs) | Suspend execution of the calling thread for the given number of seconds. The argument may be a floating-point number to indicate a more precise sleep time.
| time.sleep(1) | { time.sleep(1) } 

"""
)


print(
    f"""

-------------------------------------------------------------------------------
strftime() vs strptime()
-------------------------------------------------------------------------------

time.strftime(format[, t])      | Convert a tuple or struct_time representing a time as returned by gmtime() or localtime() to a string as specified by the format argument. If t is not provided, the current time as returned by localtime() is used.
time.strptime(string[, format]) | Parse a string representing a time according to a format. The return value is a struct_time as returned by gmtime() or localtime(). The format parameter uses the same directives as those used by strftime(); it defaults to "%a %b %d %H:%M:%S %Y" which matches the formatting returned by ctime().
"""
)

# Date Format Strings
FS_YYYYMMDD = "%Y%m%d"  # YYYYMMDD
FS_YYYY_MM_DD = "%Y-%m-%d"  # YYYY-MM-DD

FS_DATE = "%a %b %d %H:%M:%S %Z %Y"  # Fri Aug 03 11:57:19 PDT 2029 from `date` utility
FS_DATETIME = "%Y-%m-%d %H:%M:%S"  # 2024-11-05 00:15:40
FS_DATETIMEZ = "%Y-%m-%dT%H:%M:%SZ"  # 2024-11-05T00:15:40Z (UTC)

# Times
FS_HHMM = "%H%M"  # [T]hhmm
FS_HH_MM = "%H:%M"  # [T]hh:mm
FS_HHMMSS = "%H%M%S"  # [T]hhmmss
FS_HH_MM_SS = "%H:%M:%S"  # [T]hh:mm:ss
FS_HHMMSS_SSS = "%H%M%S.%f"  #  [T]hhmmss.sss
FS_HH_MM_SS_SSS = "%H:%M:%S.%f"  # [T]hh:mm:ss.sss

# Time Zones
FS_TZ_UTC = "Z"  # implied UTC
FS_TZ_OFFSET = "%z"  # ±HHMM
FS_TZ_NAME = "%Z"  # Deprecated in Python!

# ISO8601
FS_ISO8601_DATE = "%Y-%m-%d"  # 2024-11-05
FS_ISO8601_TIME = "%H:%M:%S"  # 00:15:40
FS_ISO8601_DT = "%Y-%m-%d %H:%M:%S"  # 2024-11-05 00:15:40
FS_ISO8601_UTC = "%Y-%m-%dT%H:%M:%SZ"  # 2024-11-05T00:15:40Z (UTC)

# Other Date & Time formats
FS_ATOM = "%Y-%m-%dT%H:%M:%S%z"  # Ex = 2005-08-15T15:52:01+00:00
FS_COOKIE = "%A, %d-%b-%y %H:%M:%S %Z"  # Ex: Monday, 15-Aug-05 15:52:01 UTC
FS_RSS = "%a, %d %b %Y %H:%M:%S %z"  # Ex: Mon, 15 Aug 2005 15:52:01 ±0000
FS_W3C = "%Y-%m-%dT%H:%M:%S%z"  # W3C Ex: 2005-08-15T15:52:01±00:00
FS_RFC822 = "%a, %d %b %y %H:%M:%S %z"  # Ex: Mon, 15 Aug 05 15:52:01 ±0000
FS_RFC850 = "%A, %d-%b-%y %H:%M:%S %Z"  # Ex: Monday, 15-Aug-05 15:52:01 UTC
FS_RFC1036 = "%a, %d %b %y %H:%M:%S %z"  # Ex: Mon, 15 Aug 05 15:52:01 ±0000
FS_RFC1123 = "%a, %d %b %Y %H:%M:%S %z"  # Ex: Mon, 15 Aug 2005 15:52:01 ±0000
FS_RFC2822 = "%a, %d %b %Y %H:%M:%S %z"  # Ex: Mon, 15 Aug 2005 15:52:01 ±0000
FS_RFC3339 = FS_ATOM  # Same as DATE_ATOM


print(
    f"""

-------------------------------------------------------------------------------
Standard Date Format Strings
-------------------------------------------------------------------------------

| Directive | Value                   | Description                                             |
|-----------|-------------------------|---------------------------------------------------------|
| `%a`      | { time.strftime('%a') } | Locale’s abbreviated weekday name
| `%A`      | { time.strftime('%A') } | Locale’s full weekday name
| `%b`      | { time.strftime('%b') } | Locale’s abbreviated month name
| `%B`      | { time.strftime('%B') } | Locale’s full month name
| `%c`      | { time.strftime('%c') } | Locale’s appropriate date and time representation
| `%d`      | { time.strftime('%d') } | Day of the month as a decimal number [01,31]
| `%H`      | { time.strftime('%H') } | Hour (24-hour clock) as a decimal number [00,23]
| `%I`      | { time.strftime('%I') } | Hour (12-hour clock) as a decimal number [01,12]
| `%j`      | { time.strftime('%j') } | Day of the year as a decimal number [001,366]
| `%m`      | { time.strftime('%m') } | Month as a decimal number [01,12]
| `%M`      | { time.strftime('%M') } | Minute as a decimal number [00,59]
| `%p`      | { time.strftime('%p') } | Locale’s equivalent of either AM or PM
| `%s`      | { time.strftime('%s') } | Seconds since the Unix epoch as a decimal number
| `%S`      | { time.strftime('%S') } | Second as a decimal number [00,61]
| `%U`      | { time.strftime('%U') } | Week # of year as a decimal number (Sunday is first DoW) [00,53]
|           | { '  '                } | All days in a new year preceding the first Sunday are considered to be in week 0
| `%w`      | { time.strftime('%w') } | Weekday as a decimal number [0(Sunday),6]
| `%W`      | { time.strftime('%W') } | Week # of year as a decimal number (Monday as first DOW) [00,53]
|           | { '  '                } | All days in a new year preceding the first Monday are considered to be in week 0
| `%x`      | { time.strftime('%x') } | Locale’s appropriate date representation
| `%X`      | { time.strftime('%X') } | Locale’s appropriate time representation
| `%y`      | { time.strftime('%y') } | Year without century as a decimal number [00,99]
| `%Y`      | { time.strftime('%Y') } | Year with century as a decimal number
| `%z`      | { time.strftime('%z') } | Time zone offset as a +/- time difference from UTC/GMT of the form ±HHMM
| `%Z`      | { time.strftime('%Z') } | 🛑 Deprecated. Time zone name (no characters if no time zone exists)
| `%%`      | { time.strftime('%%') } | A literal `'%'` character

For ISO8601 format details, see
- https://en.wikipedia.org/wiki/ISO_8601 : ISO8601
- https://ijmacd.github.io/rfc3339-iso8601/ : RFC 3339 vs ISO 8601
- https://www.rfc-editor.org/rfc/rfc3339.html : Date and Time on the Internet: Timestamps


time uses the current time by default

| Constant        | Value               | Expression                         | Description        |
|-----------------|---------------------|------------------------------------|--------------------|
| FS_YYYYMMDD     | { FS_YYYYMMDD     } | { time.strftime(FS_YYYYMMDD    ) } |
| FS_YYYY_MM_DD   | { FS_YYYY_MM_DD   } | { time.strftime(FS_YYYY_MM_DD  ) } |
|                 |                     |                                    | 
| Times           |                     |                                    | 
| FS_HHMM         | { FS_HHMM         } | { time.strftime(FS_HHMM        ) } | [T]hhmm
| FS_HH_MM        | { FS_HH_MM        } | { time.strftime(FS_HH_MM       ) } | [T]hh:mm
| FS_HHMMSS       | { FS_HHMMSS       } | { time.strftime(FS_HHMMSS      ) } | [T]hhmmss
| FS_HH_MM_SS     | { FS_HH_MM_SS     } | { time.strftime(FS_HH_MM_SS    ) } | [T]hh:mm:ss
| FS_HHMMSS_SSS   | { FS_HHMMSS_SSS   } | { time.strftime(FS_HHMMSS_SSS  ) } | [T]hhmmss.sss
| FS_HH_MM_SS_SSS | { FS_HH_MM_SS_SSS } | { time.strftime(FS_HH_MM_SS_SSS) } | [T]hh:mm:ss.sss
|                 |                     |                                    | 
| Time Zones      |                     |                                    | 
| FS_TZ_UTC       | "Z"                 | { time.strftime("Z"            ) } | implied UTC
| FS_TZ_OFFSET    | "%z"                | { time.strftime("%z"           ) } | ±HHMM + or - time offset from UTC/GMT
| FS_TZ_NAME      | "%Z"                | { time.strftime("%Z"           ) } | Deprecated in Python!
|                 |                     |                                    | 
| ISO8601         |                     |                                    | 
| FS_ISO8601_DATE | { FS_ISO8601_DATE } | { time.strftime(FS_ISO8601_DATE) } | 2024-11-05
| FS_ISO8601_TIME | { FS_ISO8601_TIME } | { time.strftime(FS_ISO8601_TIME) } | 00:15:40
| FS_ISO8601_UTC  | { FS_ISO8601_UTC  } | { time.strftime(FS_ISO8601_UTC ) } | 2024-11-05T00:15:40Z (UTC)
| FS_ISO8601_DT   | { FS_ISO8601_DT   } | { time.strftime(FS_ISO8601_DT  ) } | 2024-11-05 00:15:40
|                 |                     |                                    | 
| Other formats   |                     |                                    | 
| FS_ATOM         | { FS_ATOM         } | { time.strftime(FS_ATOM        ) } | Ex = 2005-08-15T15:52:01+00:00
| FS_COOKIE       | { FS_COOKIE       } | { time.strftime(FS_COOKIE      ) } | Ex: Monday, 15-Aug-05 15:52:01 UTC
| FS_RSS          | { FS_RSS          } | { time.strftime(FS_RSS         ) } | Ex: Mon, 15 Aug 2005 15:52:01 ±0000
| FS_W3C          | { FS_W3C          } | { time.strftime(FS_W3C         ) } | W3C Ex: 2005-08-15T15:52:01±00:00
| FS_RFC822       | { FS_RFC822       } | { time.strftime(FS_RFC822      ) } | Ex: Mon, 15 Aug 05 15:52:01 ±0000
| FS_RFC850       | { FS_RFC850       } | { time.strftime(FS_RFC850      ) } | Ex: Monday, 15-Aug-05 15:52:01 UTC
| FS_RFC1036      | { FS_RFC1036      } | { time.strftime(FS_RFC1036     ) } | Ex: Mon, 15 Aug 05 15:52:01 ±0000
| FS_RFC1123      | { FS_RFC1123      } | { time.strftime(FS_RFC1123     ) } | Ex: Mon, 15 Aug 2005 15:52:01 ±0000
| FS_RFC2822      | { FS_RFC2822      } | { time.strftime(FS_RFC2822     ) } | Ex: Mon, 15 Aug 2005 15:52:01 ±0000
| FS_RFC3339      | { FS_RFC3339      } | { time.strftime(FS_RFC3339     ) } | Same as DATE_ATOM
"""
)

print(
    f"""


-------------------------------------------------------------------------------
strftime(): Timestamp Formatting of date, datetime, time classes
-------------------------------------------------------------------------------

| time.strftime('%Y-%m-%d')      | { time.strftime('%Y-%m-%d')      } | now as year-month-day
| time.strftime('%H:%M:%S')      | { time.strftime('%H:%M:%S')      } | now as hour:min:sec
| time.strftime(FS_ISO8601_DATE) | { time.strftime(FS_ISO8601_DATE) } | now as date only
| time.strftime(FS_ISO8601_TIME) | { time.strftime(FS_ISO8601_TIME) } | now as time only
| time.strftime(FS_ISO8601_UTC)  | { time.strftime(FS_ISO8601_UTC)  } | now as UTC
| time.strftime(FS_ISO8601_UTC)  | { time.strftime(FS_ISO8601_DT)   } | now as Date Time


-----

Time is TimeZone naive by definition
⚠ Do not use any `%z` timezone offsets with `time` - they will always be local!

{ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())    } | local time
{ time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime()) } | local time with offset
{ time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())       } | GMT/UTC
{ time.strftime("%Y-%m-%d %H:%M:%S %z", time.gmtime())    } | GMT/UTC with offset

"""
)
