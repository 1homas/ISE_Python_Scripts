#!/usr/bin/env python3
"""
Test script to demonstrate the uses of `datetime` for basic date and time types.
"""
__author__ = "Thomas Howard"
__email__ = "1@1homas.org"
__license__ = "MIT - https://mit-license.org/"

import datetime  # from datetime import date, time, datetime, timedelta, timezone

# import time  # do not confuse this time with datetime.time!

from dateutil.tz import UTC, tzlocal, gettz, resolve_imaginary

# import time
import zoneinfo  # Concrete time zones representing the IANA time zone database (often called tz, tzdata or zoneinfo)

W = 10  # column width

# Now Varibles for Examples
dt_now = datetime.datetime.now()  # current datetime in local timezone, since the Unix Epoch
ts_now = datetime.datetime.now().timestamp()  # current timestamp, in seconds, since the Unix Epoch
d_now = datetime.datetime.now().date()
t_now = datetime.datetime.now().timestamp()


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

| Directive | Example                 | Description                                             |
|-----------|-------------------------|---------------------------------------------------------|
| `%a`      | {dt_now.strftime('%a'):10} | Locale’s abbreviated weekday name |
| `%A`      | {dt_now.strftime('%A'):10} | Locale’s full weekday name |
| `%b`      | {dt_now.strftime('%b'):10} | Locale’s abbreviated month name |
| `%B`      | {dt_now.strftime('%B'):10} | Locale’s full month name |
| `%c`      | {dt_now.strftime('%c'):10} | Locale’s appropriate date and time representation |
| `%d`      | {dt_now.strftime('%d'):10} | Day of the month as a decimal number [01,31] |
| `%H`      | {dt_now.strftime('%H'):10} | Hour (24-hour clock) as a decimal number [00,23] |
| `%I`      | {dt_now.strftime('%I'):10} | Hour (12-hour clock) as a decimal number [01,12] |
| `%j`      | {dt_now.strftime('%j'):10} | Day of the year as a decimal number [001,366] |
| `%m`      | {dt_now.strftime('%m'):10} | Month as a decimal number [01,12] |
| `%M`      | {dt_now.strftime('%M'):10} | Minute as a decimal number [00,59] |
| `%p`      | {dt_now.strftime('%p'):10} | Locale’s equivalent of either AM or PM |
| `%s`      | {dt_now.strftime('%s'):10} | Seconds since the Unix epoch as a decimal number |
| `%S`      | {dt_now.strftime('%S'):10} | Second as a decimal number [00,61] |
| `%U`      | {dt_now.strftime('%U'):10} | Week # of year as a decimal number (Sunday is first DoW) [00,53] |
|           | {'  ':10} | All days in a new year preceding the first Sunday are considered to be in week 0 |
| `%w`      | {dt_now.strftime('%w'):10} | Weekday as a decimal number [0(Sunday),6] |
| `%W`      | {dt_now.strftime('%W'):10} | Week # of year as a decimal number (Monday as first DOW) [00,53] |
|           | {'  ':10} | All days in a new year preceding the first Monday are considered to be in week 0 |
| `%x`      | {dt_now.strftime('%x'):10} | Locale’s appropriate date representation |
| `%X`      | {dt_now.strftime('%X'):10} | Locale’s appropriate time representation |
| `%y`      | {dt_now.strftime('%y'):10} | Year without century as a decimal number [00,99] |
| `%Y`      | {dt_now.strftime('%Y'):10} | Year with century as a decimal number |
| `%z`      | {dt_now.strftime('%z'):10} | Time zone offset as a +/- time difference from UTC/GMT of the form ±HHMM |
| `%Z`      | {dt_now.strftime('%Z'):10} | 🛑 Deprecated. Time zone name (no characters if no time zone exists) |
| `%%`      | {dt_now.strftime('%%'):10} | A literal `'%'` character |

For ISO8601 format details, see
- https://en.wikipedia.org/wiki/ISO_8601 : ISO8601
- https://ijmacd.github.io/rfc3339-iso8601/ : RFC 3339 vs ISO 8601
- https://www.rfc-editor.org/rfc/rfc3339.html : Date and Time on the Internet: Timestamps


| Constant        | Value                | Expression           | Description          |
|-----------------|----------------------|----------------------|----------------------|
| FS_YYYYMMDD     | {FS_YYYYMMDD:20} | {dt_now.strftime(FS_YYYYMMDD):20} |
| FS_YYYY_MM_DD   | {FS_YYYY_MM_DD:20} | {dt_now.strftime(FS_YYYY_MM_DD):20} |
|                 |                      |                      |                      |
| Times           |                      |                      |                      |
| FS_HHMM         | {FS_HHMM:20} | {dt_now.strftime(FS_HHMM):20} | [T]hhmm |
| FS_HH_MM        | {FS_HH_MM:20} | {dt_now.strftime(FS_HH_MM):20} | [T]hh:mm |
| FS_HHMMSS       | {FS_HHMMSS:20} | {dt_now.strftime(FS_HHMMSS):20} | [T]hhmmss |
| FS_HH_MM_SS     | {FS_HH_MM_SS:20} | {dt_now.strftime(FS_HH_MM_SS):20} | [T]hh:mm:ss |
| FS_HHMMSS_SSS   | {FS_HHMMSS_SSS:20} | {dt_now.strftime(FS_HHMMSS_SSS):20} | [T]hhmmss.sss |
| FS_HH_MM_SS_SSS | {FS_HH_MM_SS_SSS:20} | {dt_now.strftime(FS_HH_MM_SS_SSS):20} | [T]hh:mm:ss.sss |
|                 |                      |                      |                      |
| Time Zones      |                      |                      |                      |
| FS_TZ_UTC       | {"Z":20} | {dt_now.strftime("Z"):20} | implied UTC |
| FS_TZ_OFFSET    | {"%z":20} | {dt_now.strftime("%z"):20} | ±HHMM + or - time offset from UTC/GMT |
| FS_TZ_NAME      | {"%Z":20} | {dt_now.strftime("%Z"):20} | Deprecated in Python! |
|                 |                      |                      |                      |
| ISO8601         |                      |                      |                      |
| FS_ISO8601_DATE | {FS_ISO8601_DATE:20} | {dt_now.strftime(FS_ISO8601_DATE):20} | 2024-11-05 |
| FS_ISO8601_TIME | {FS_ISO8601_TIME:20} | {dt_now.strftime(FS_ISO8601_TIME):20} | 00:15:40 |
| FS_ISO8601_UTC  | {FS_ISO8601_UTC:20} | {dt_now.strftime(FS_ISO8601_UTC):20} | 2024-11-05T00:15:40Z (UTC) |
| FS_ISO8601_DT   | {FS_ISO8601_DT:20} | {dt_now.strftime(FS_ISO8601_DT):20} | 2024-11-05 00:15:40 |
|                 |                      |                      |                      |
| Other formats   |                      |                      |                      |
| FS_ATOM         | {FS_ATOM:26} | {dt_now.strftime(FS_ATOM):26} | Ex = 2005-08-15T15:52:01+00:00 |
| FS_COOKIE       | {FS_COOKIE:26} | {dt_now.strftime(FS_COOKIE):26} | Ex: Monday, 15-Aug-05 15:52:01 UTC |
| FS_RSS          | {FS_RSS:26} | {dt_now.strftime(FS_RSS):26} | Ex: Mon, 15 Aug 2005 15:52:01 ±0000 |
| FS_W3C          | {FS_W3C:26} | {dt_now.strftime(FS_W3C):26} | W3C Ex: 2005-08-15T15:52:01±00:00 |
| FS_RFC822       | {FS_RFC822:26} | {dt_now.strftime(FS_RFC822):26} | Ex: Mon, 15 Aug 05 15:52:01 ±0000 |
| FS_RFC850       | {FS_RFC850:26} | {dt_now.strftime(FS_RFC850):26} | Ex: Monday, 15-Aug-05 15:52:01 UTC |
| FS_RFC1036      | {FS_RFC1036:26} | {dt_now.strftime(FS_RFC1036):26} | Ex: Mon, 15 Aug 05 15:52:01 ±0000 |
| FS_RFC1123      | {FS_RFC1123:26} | {dt_now.strftime(FS_RFC1123):26} | Ex: Mon, 15 Aug 2005 15:52:01 ±0000 |
| FS_RFC2822      | {FS_RFC2822:26} | {dt_now.strftime(FS_RFC2822):26} | Ex: Mon, 15 Aug 2005 15:52:01 ±0000 |
| FS_RFC3339      | {FS_RFC3339:26} | {dt_now.strftime(FS_RFC3339):26} | Same as DATE_ATOM |
"""
)


#
# Constants
#
# datetime.MINYEAR # smallest year number allowed in a date or datetime object. MINYEAR is 1.
# datetime.MAXYEAR # largest year number allowed in a date or datetime object. MAXYEAR is 9999.
# datetime.UTC     # Alias for the UTC time zone singleton datetime.timezone.utc.

# Contants for Examples
YEAR = 2000
MONTH = 1
DAY = 1
WEEK = 1
ORDINAL_1 = 1
EPOCH_STR = "1970-01-01 00:00:00"  # FS_ISO8601_DT format

print(
    f"""
| dt_now | {str(datetime.datetime.now()):20} | current datetime in local timezone, since the Unix Epoch
| ts_now | {str(datetime.datetime.now().timestamp()):20} | current timestamp, in seconds, since the Unix Epoch
| d_now  | {str(datetime.datetime.now().date()):20} | 
| t_now  | {str(datetime.datetime.now().timestamp()):20} | 
"""
)

d = datetime.date.today()
d_epoch = datetime.date(1, 1, 1)

# t = time.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)
t = datetime.time.fromisoformat("01:02:03")  # Return a time from a valid ISO 8601 format
dt_epoch = datetime.datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
dt = datetime.datetime(YEAR, MONTH, DAY, hour=0, minute=0, second=0)

#
# Types (immutable)
#
# object subclasses:
# - datetime.date       # An idealized naive date, assuming the current Gregorian calendar always was, and always will be, in effect. Attributes: year, month, and day.
#   - datetime.datetime # A combination of a date and a time. Attributes: year, month, day, hour, minute, second, microsecond, and tzinfo.
# - datetime.time       # An idealized time, independent of any particular day, assuming that every day has exactly 24*60*60 seconds. (There is no notion of “leap seconds” here.) Attributes: hour, minute, second, microsecond, and tzinfo.
# - datetime.tzinfo     # An abstract base class for time zone information objects. These are used by the datetime and time classes to provide a customizable notion of time adjustment (for example, to account for time zone and/or daylight saving time).
#  - datetime.timezone  # A class that implements the tzinfo abstract base class as a fixed offset from the UTC.
# - datetime.timedelta  # A duration expressing the difference between two datetime or date instances to microsecond resolution.
#


# -----------------------------------------------------------------------------
# date
# A date object represents a date (year, month and day) in an idealized calendar, the current Gregorian calendar indefinitely extended in both directions.
# class datetime.date(year, month, day)
# -----------------------------------------------------------------------------

# constructor methods
d = datetime.date(YEAR, MONTH, DAY)  # All args required. Must be integers

print(
    f"""

-------------------------------------------------------------------------------
Date
-------------------------------------------------------------------------------

| Date Constructors                              | Example              | Description |
|------------------------------------------------|----------------------|-------------|
| datetime.date.today()                          | {str(datetime.date.today()):20} | current local date. This is equivalent to date.fromtimestamp(time.time()).
| datetime.date.fromtimestamp(dt.timestamp())    | {str(datetime.date.fromtimestamp(dt.timestamp())):20} | local date of the POSIX timestamp
| datetime.date.fromordinal(ORDINAL_1)           | {str(datetime.date.fromordinal(ORDINAL_1)):20} | date in the proleptic Gregorian ordinal, where January 1 of year 1 has ordinal 1.
| datetime.date.fromisoformat("2000-01-01")      | {str(datetime.date.fromisoformat("2000-01-01")):20} | date in a valid ISO 8601 format; datetime.date(2000, 1, 1)
| datetime.date.fromisoformat("20191204")        | {str(datetime.date.fromisoformat("20191204")):20} | datetime.date(2019, 12, 4)
| datetime.date.fromisocalendar(YEAR, WEEK, DAY) | {str(datetime.date.fromisocalendar(YEAR, WEEK, DAY)):20} | date in ISO calendar; inverse of date.isocalendar().
| datetime.date.fromisoformat("2021-W01-1")      | {str(datetime.date.fromisoformat("2021-W01-1")):20} | datetime.date(2021, 1, 4)

| date Class Atributes              | Example              | Description |
|-----------------------------------|----------------------|-------------|
| datetime.date.min                 | {str(datetime.date.min):20} | The earliest representable date, date(MINYEAR, 1, 1).
| datetime.date.max                 | {str(datetime.date.max):20} | The latest representable date, date(MAXYEAR, 12, 31).
| datetime.date.resolution          | {str(datetime.date.resolution):20} | The smallest possible difference between non-equal date objects, timedelta(days=1).
| datetime.date.year                | {str(datetime.date.year):20} | Between MINYEAR and MAXYEAR inclusive.
| datetime.date.month               | {str(datetime.date.month):20} | Between 1 and 12 inclusive.
| datetime.date.day                 | {str(datetime.date.day):20} | Between 1 and the number of days in the given month of the given year.

| date Instance methods             | Example              | Description |
|-----------------------------------|----------------------|-------------|
| datetime.date(2000, 12, 26)       | {str(datetime.date(2000, 12, 26)):20} | 
| d.replace(year=y, month=m, day=d) | {str(d.replace(year=YEAR, month=MONTH, day=DAY)):20} | same date, except for parameters given new values by keyword args
| d.replace(day=31)                 | {str(d.replace(day=31)):20} | Return a date with the same value, except for those parameters given new values (year, month, or day)
| d.timetuple()                     | {str(d.timetuple()):20} | Return a time.struct_time. hours, minutes and seconds are 0, and the DST flag is -1.
| d.toordinal()                     | {str(d.toordinal()):20} | Return the proleptic Gregorian ordinal of the date, where January 1 of year 1 has ordinal 1. For any date object d, date.fromordinal(d.toordinal()) == d.
| d.weekday()                       | {str(d.weekday()):20} | Return the day of the week as an integer, where Monday is 0 and Sunday is 6. For example, date(2002, 12, 4).weekday() == 2, a Wednesday. See also isoweekday().
| d.isoweekday()                    | {str(d.isoweekday()):20} | Return the day of the week as an integer, where Monday is 1 and Sunday is 7. For example, date(2002, 12, 4).isoweekday() == 3, a Wednesday. See also weekday(), isocalendar().
| d.isocalendar()                   | {str(d.isocalendar()):20} | Return a named tuple object with three components: year, week and weekday.
| d.isoformat()                     | {str(d.isoformat()):20} | Return a string representing the date in ISO 8601 format, YYYY-MM-DD:
| d.ctime()                         | {str(d.ctime()):20} | Return a string representing the date:
| d.strftime(FS_ISO8601)            | {str(d.strftime(FS_ISO8601_DT)):20} | Return a string representing the date, controlled by an explicit format string

"""
)

# -----------------------------------------------------------------------------
# datetime
# A datetime object is a single object containing all the information from a date object and a time object.
# class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
# -----------------------------------------------------------------------------

dt_now = datetime.datetime.now()  # 2023-10-28 12:26:16.479646
d_today = datetime.date.today()
dt_from_ts = datetime.datetime.fromtimestamp(dt_now.timestamp(), tz=None)  # tz=None uses the local system's timezone

datetime.datetime.now(tz=datetime.timezone.utc)  # Built-in: UTC
pacific_tz = zoneinfo.ZoneInfo("America/Los_Angeles")
datetime_now_pt = dt_now.replace(tzinfo=pacific_tz)


#
# datetime TimeZone Naive vs Aware Methods
# - date type are always naive
# - time or datetime may be aware or naive
# - A datetime object d is aware if both of the following hold:
#   - d.tzinfo is not None
#   - d.tzinfo.utcoffset(d) does not return None
# - A time object t is aware if both of the following hold:
#   - t.tzinfo is not None
#   - t.tzinfo.utcoffset(None) does not return None.
# - aware and naive doesn’t apply to timedelta objects
#
def aware_utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def aware_utcfromtimestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)


def naive_utcnow():
    return aware_utcnow().replace(tzinfo=None)


def naive_utcfromtimestamp(timestamp):
    return aware_utcfromtimestamp(timestamp).replace(tzinfo=None)


print(aware_utcnow())
print(aware_utcfromtimestamp(0))
print(naive_utcnow())
print(naive_utcfromtimestamp(0))

print(
    f"""

-------------------------------------------------------------------------------
DateTime
-------------------------------------------------------------------------------

| What                                | Example                        | Description                    |
|-------------------------------------|--------------------------------|--------------------------------|
| Class Methods                       | {'':30} | {'':30} |
| datetime.datetime.now()             | {str(datetime.datetime.now()):20} | 2023-11-05 10:43:26.552238
| datetime.datetime.now()             | {str(datetime.datetime.now()):20} | ⚠ naive datetime is timezone unaware!
| datetime.datetime.now(tz=None)      | {str(datetime.datetime.now(tz=None)):20} | TZ-aware! tz=None uses the local system's timezone
| datetime.datetime.now(tz=datetime.timezone.utc) | {str(datetime.datetime.now(tz=datetime.timezone.utc)):20} |
| datetime.datetime.now(datetime.UTC) |  | tz=None uses the local system's timezone |
| datetime.datetime.now().timestamp() | {str(datetime.datetime.now().timestamp()):20} | 1699209810.552254
| datetime.datetime.today()           | {str(datetime.datetime.today()):20} | ⚠ Current local date or naive datetime

| What                                                | Example              | Description                    |
|-----------------------------------------------------|----------------------|--------------------------------|
| datetime.datetime.utcnow()                          | {str(datetime.datetime.utcnow()):20} | ⌫␡ Deprecated Naive datetime from current UTC time.
| datetime.datetime.utcfromtimestamp(dt.timestamp())  | {str(datetime.datetime.utcfromtimestamp(dt.timestamp())):20} |
| datetime.datetime.combine(d, t, tzinfo=None)        | {str(datetime.datetime.combine(d, t, tzinfo=None)):20} | tzinfo = None is naive
| datetime.datetime.strptime("20000101", FS_YYYYMMDD) | {str(datetime.datetime.strptime("20000101", FS_YYYYMMDD)):20} |

| What                                                                               | Example                        | Description                    |
|------------------------------------------------------------------------------------|--------------------------------|--------------------------------|
| Python 3.12+ safe constructors                                                     |                |            |
| Python 3.11 or newer, may replace datetime.timezone.utc with datetime.UTC          |                |            |
| datetime.datetime.now(datetime.UTC).replace(tzinfo=None)                           | {naive_utcnow()} |            |
| datetime.datetime.fromtimestamp(dt.timestamp(), datetime.UTC)                      | {aware_utcfromtimestamp(ts_now)} |            |
| datetime.datetime.fromtimestamp(dt.timestamp(), datetime.UTC).replace(tzinfo=None) | {naive_utcfromtimestamp(ts_now)} |            |


| What                           | Example                        | Description |
|--------------------------------|--------------------------------|--------------------------------|
| datetime Class Attributes      | {'':30} | {'':30} |
| datetime.datetime.max          | {str(datetime.datetime.max):30} | latest datetime: datetime(MAXYEAR, 12, 31, 23, 59, 59, 999999, tzinfo=None)
| datetime.datetime.resolution   | {str(datetime.datetime.resolution):30} | smallest difference between datetime objects, timedelta(microseconds=1)
|                                | {'':30} | {'':30} |
| datetime Instance Attributes (read-only) |                      | {'':30} |
| dt_now.year                    | {str(dt_now.year):30} | Between MINYEAR and MAXYEAR inclusive.
| dt_now.month                   | {str(dt_now.month):30} | Between 1 and 12 inclusive.
| dt_now.day                     | {str(dt_now.day):30} | Between 1 and the number of days in the given month of the given year.
| dt_now.hour                    | {str(dt_now.hour):30} | In range(24).
| dt_now.minute                  | {str(dt_now.minute):30} | In range(60).
| dt_now.second                  | {str(dt_now.second):30} | In range(60).
| dt_now.microsecond             | {str(dt_now.microsecond):30} | In range(1000000).
| dt_now.tzinfo                  | {str(dt_now.tzinfo):30} | object passed as tzinfo argument to constructor, or None
| dt_now.fold                    | {str(dt_now.fold):30} | In [0, 1]. Used to disambiguate wall times during a repeated interval.
|                                | {'':30} | {'':30} |
| datetime Instance Methods      | {'':30} | {'':30} |
| datetime.datetime.now()        | {str(datetime.datetime.now()):30} | now
| dt_now.today()                 | {str(dt_now.today()):30} | 2023-10-28 12:26:15.475201
| dt_now.timestamp()             | {str(dt_now.timestamp()):30} | 1698521416.47965
| dt_now.date()                  | {str(dt_now.date()):30} | Return `date` object with same year, month and day
| dt_now.time()                  | {str(dt_now.time()):30} | Return datetime's `time` component however tzinfo is None.
| dt_now.timetz()                | {str(dt_now.timetz()):30} | Return DateTime's `time` component with tzinfo
| dt_now.replace(year=2030)      | {str(dt_now.replace(year=2030)):30} | Replace year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, fold=0
|                                | {'':30} | {'':30} |
| timezone aware methods         | {'':30} | {'':30} |
| dt_now.astimezone(tz=None)     | {str(dt_now.astimezone(tz=None)):30} | Return a datetime with new tzinfo attribute tz's local time
| dt_now.utcoffset()             | {str(dt_now.utcoffset()):30} | Returns self.tzinfo.utcoffset(self), otherwise None
| dt_now.dst()                   | {str(dt_now.dst()):30} | If tzinfo is None, returns None, else returns self.tzinfo.dst(self)
| dt_now.tzname()                | {str(dt_now.tzname()):30} | If tzinfo is None, returns None, else returns self.tzinfo.tzname(self)
| dt_now.timetuple()             | {str(dt_now.timetuple()):30} | Return a time.struct_time such as returned by time.localtime().
| dt_now.utctimetuple()          | {str(dt_now.utctimetuple()):30} | 
| dt_now.toordinal()             | {str(dt_now.toordinal()):30} | Return the proleptic Gregorian ordinal of the date; same as dt.date().toordinal()
| dt_now.timestamp()             | {str(dt_now.timestamp()):30} | Return POSIX timestamp
| dt_now.replace(tzinfo=None)    | {str(dt_now.replace(tzinfo=None)):30} | attach/change a time zone (tz) object to datetime without adjustment
| dt_now.weekday()               | {str(dt_now.weekday()):30} | day of the week as an integer, where Monday is 0 and Sunday is 6
| dt_now.isoweekday()            | {str(dt_now.isoweekday()):30} | day of the week as an integer, where Monday is 1 and Sunday is 7
| dt_now.isocalendar()           | {str(dt_now.isocalendar()):30} | named tuple with 3 components: year, week, weekday; same as dt.date().isocalendar()
| dt_now.isoformat()             | {str(dt_now.isoformat()):30} | ISO 8601: YYYY-MM-DDTHH:MM:SS.ffffff, if microsecond is not 0
| dt_now.isoformat(sep="T")      | {str(dt_now.isoformat(sep="T")):30} | ISO 8601: YYYY-MM-DDTHH:MM:SS.ffffff, if microsecond is not 0
| dt_now.isoformat(sep="T", timespec="auto") | {str(dt_now.isoformat(sep="T", timespec="auto")):30} | ISO 8601: YYYY-MM-DDTHH:MM:SS.ffffff, if microsecond is not 0
| dt_now.ctime()                 | {str(dt_now.ctime()):30} | a string representing the date and time: 'Wed Dec  4 20:26:40 2002'
| dt_now.strftime("%s")          | {str(dt_now.strftime("%s")):30} | seconds!
| dt_now.strftime(FS_ISO8601_DT) | {str(dt_now.strftime(FS_ISO8601_DT)):30} | format the date and time using for format specifier string

"""
)


# -----------------------------------------------------------------------------
# time
# A time object represents a (local) time of day, independent of any particular day, and subject to adjustment via a tzinfo object.
# class datetime.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
# -----------------------------------------------------------------------------

print(
    f"""

-------------------------------------------------------------------------------
datetime.time 
t = time.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)
-------------------------------------------------------------------------------


| Constructors                                   | Example                        | Description                    |
|------------------------------------------------|--------------------------------|--------------------------------|
| Method                                         | {'':20} | {'':20} |
| datetime.time.fromisoformat("01:02:03")        | {str(datetime.time.fromisoformat("01:02:03")):20} | Return a time from a valid ISO 8601 format
| datetime.time.fromisoformat("04:23:01")        | {str(datetime.time.fromisoformat("04:23:01")):20} | datetime.time(4, 23, 1)
| datetime.time.fromisoformat("T04:23:01")       | {str(datetime.time.fromisoformat("T04:23:01")):20} | datetime.time(4, 23, 1)
| datetime.time.fromisoformat("T042301")         | {str(datetime.time.fromisoformat("T042301")):20} | datetime.time(4, 23, 1)
| datetime.time.fromisoformat("04:23:01.000384") | {str(datetime.time.fromisoformat("04:23:01.000384")):20} | datetime.time(4, 23, 1, 384)
| datetime.time.fromisoformat("04:23:01,000384") | {str(datetime.time.fromisoformat("04:23:01,000384")):20} | datetime.time(4, 23, 1, 384)
| datetime.time.fromisoformat("04:23:01+04:00")  | {str(datetime.time.fromisoformat("04:23:01+04:00")):20} | datetime.time(4, 23, 1, tzinfo=datetime.timezone(datetime.timedelta(seconds=14400)))
| datetime.time.fromisoformat("04:23:01Z")       | {str(datetime.time.fromisoformat("04:23:01Z")):20} | datetime.time(4, 23, 1, tzinfo=datetime.timezone.utc)
| datetime.time.fromisoformat("04:23:01+00:00")  | {str(datetime.time.fromisoformat("04:23:01+00:00")):20} | datetime.time(4, 23, 1, tzinfo=datetime.timezone.utc)
|                                                | {'':20} | {'':20} |
| Class attributes                               | {'':20} | {'':20} |
| datetime.time.min                              | {str(datetime.time.min):20} | The earliest representable time, time(0, 0, 0, 0).
| datetime.time.max                              | {str(datetime.time.max):20} | The latest representable time, time(23, 59, 59, 999999).
| datetime.time.resolution                       | {str(datetime.time.resolution):20} | The smallest possible difference between non-equal time objects, timedelta(microseconds=1), although note that arithmetic on time objects is not supported.
|                                                | {'':20} | {'':20} |
| Instance attributes (read-only)                | {'':20} | {'':20} |
| t.hour                                         | {str(t.hour):20} | In range(24)                   
| t.minute                                       | {str(t.minute):20} | In range(60)                   
| t.second                                       | {str(t.second):20} | In range(60)                   
| t.microsecond                                  | {str(t.microsecond):20} | In range(1000000)
| t.tzinfo                                       | {str(t.tzinfo):20} | The object passed as the tzinfo argument to the time constructor, or None if none was passed.
| t.fold                                         | {str(t.fold):20} | In [0, 1]. Used to disambiguate wall times during a repeated interval.
|                                                | {'':20} | {'':20} |
| Instance methods                               | {'':20} | {'':20} |
| t.replace(hour=0, ...)                         | {str(t.replace(hour=0)):20} | Same time, updated values (hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.UTC, fold=0). tzinfo=None is naive
| t.isoformat(timespec="auto")                   | {str(t.isoformat(timespec="auto")):20} | Return a string representing the time in ISO 8601 format, where:
| t.isoformat(timespec='auto')                   | {str(t.isoformat(timespec='auto')):20} | Same as 'seconds' if microsecond is 0, same as 'microseconds' otherwise.
| t.isoformat(timespec='hours')                  | {str(t.isoformat(timespec='hours')):20} | Include the hour in the two-digit HH format.
| t.isoformat(timespec='minutes')                | {str(t.isoformat(timespec='minutes')):20} | Include hour and minute in HH:MM format.
| t.isoformat(timespec='seconds')                | {str(t.isoformat(timespec='seconds')):20} | Include hour, minute, and second in HH:MM:SS format.
| t.isoformat(timespec='milliseconds')           | {str(t.isoformat(timespec='milliseconds')):20} | Include full time, but truncate fractional second part to milliseconds. HH:MM:SS.sss format.
| t.isoformat(timespec='microseconds')           | {str(t.isoformat(timespec='microseconds')):20} | Include full time in HH:MM:SS.ffffff format.
|                                                | {'':30} | {'':30} |
| t.__str__()                                    | {str(t.__str__()):20} | For a time t, str(t) is equivalent to t.isoformat().
| t.strftime(FS_HH_MM_SS)                        | {str(t.strftime(FS_HH_MM_SS)):20} | Return a string representing the time, with format string. See also strftime() and strptime()
| t.__format__(FS_HH_MM_SS)                      | {str(t.__format__(FS_HH_MM_SS)):20} | Same as time.strftime(). See also strftime() and strptime() Behavior and time.isoformat().
| t.utcoffset()                                  | {str(t.utcoffset()):20} | If tzinfo is None, returns None, else returns self.tzinfo.utcoffset(None), and raises an exception if the latter doesn’t return None or a timedelta object with magnitude less than one day.
| t.dst()                                        | {str(t.dst()):20} | If tzinfo is None, returns None, else returns self.tzinfo.dst(None), and raises an exception if the latter doesn’t return None, or a timedelta object with magnitude less than one day.
| t.tzname()                                     | {str(t.tzname()):20} | If tzinfo is None, returns None, else returns self.tzinfo.tzname(None), or raises an exception if the latter doesn’t return None or a string object.

"""
)


print(
    f"""
    
-------------------------------------------------------------------------------
tzinfo
datetime.tzinfo
An abstract base class, and should not be instantiated directly. Define a subclass to capture information about a time zone.
An instance of (a concrete subclass of) tzinfo can be passed to the constructors for datetime and time objects.
The latter objects view their attributes as being in local time, and the tzinfo object supports methods revealing offset of local time from UTC, the name of the time zone, and DST offset, all relative to a date or time object passed to them.
-------------------------------------------------------------------------------

tzi = datetime.datetime.now(tz=zoneinfo.ZoneInfo("UTC"))
tzi.utcoffset() | offset of local time from UTC as a timedelta object: positive east of UTC, negative west of UTC.
tzi.dst()       | the daylight saving time (DST) adjustment, as a timedelta object or None if DST information isn’t known.
tzi.tzname()    | time zone name of the datetime object. May be anything: "UTC", "-500", "-5:00", "EDT", "US/Eastern"... None if unknown.

"""
)


print(
    f"""
    
-------------------------------------------------------------------------------
timezone
The timezone class is a *subclass* of tzinfo - each instance represents a time zone defined by a fixed offset from UTC.
class datetime.timezone(offset, name=None) where offset is a timedelta object representing the difference between the local time and UTC
-------------------------------------------------------------------------------

tz = datetime.timezone(datetime.timedelta(hours=-8), name="HBC")
utc = datetime.timezone(datetime.timedelta(0), name="UTC")

# Class Attributes
datetime.timezone.utc  # The UTC time zone, timezone(timedelta(0)).

# Class methods
tz.utcoffset(None)  # Return the fixed value specified when the timezone instance is constructed.
tz.tzname(None)  # Return the fixed value specified when the timezone instance is constructed.
tz.dst(None)  # Always returns None.
# tz.fromutc( datetime.datetime.now(tz=None))  # Return dt + offset. The dt argument must be an *aware* datetime instance, with tzinfo set to self.

# Class attributes
# timezone.utc # The UTC time zone, timezone(timedelta(0)).

"""
)


from datetime import timedelta

# Convenient Constants
TD_60S = datetime.timedelta(seconds=60)
TD_01M = datetime.timedelta(minutes=1)
TD_05M = datetime.timedelta(minutes=5)
TD_60M = datetime.timedelta(minutes=60)
TD_01H = datetime.timedelta(hours=1)
TD_24H = datetime.timedelta(hours=24)
TD_01D = datetime.timedelta(days=1)
TD_07D = datetime.timedelta(days=7)
TD_30D = datetime.timedelta(days=30)
TD_90D = datetime.timedelta(days=90)

# FY24,2023-07-30,2024-07-27
dt_fy24_beg = datetime.date(2023, 7, 30)
dt_fy24_end = datetime.date(2024, 7, 27)
dt_qtr_beg = datetime.date(2023, 7, 30)

print(
    f"""

-------------------------------------------------------------------------------
timedelta
A timedelta object represents a duration, the difference between two datetime or date instances.
class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
-------------------------------------------------------------------------------

| What                                    | Example                        | Description                    |
|-----------------------------------------|--------------------------------|--------------------------------|
| Define Convenient Constants             | {'':30} | {'':30} |
| TD_60S = datetime.timedelta(seconds=60) | {str(TD_60S):30} | {'':30} |
| TD_01M = datetime.timedelta(minutes=1)  | {str(TD_01M):30} | {'':30} |
| TD_01M = datetime.timedelta(minutes=5)  | {str(TD_05M):30} | {'':30} |
| TD_60M = datetime.timedelta(minutes=60) | {str(TD_60M):30} | {'':30} |
| TD_01H = datetime.timedelta(hours=1)    | {str(TD_01H):30} | {'':30} |
| TD_24H = datetime.timedelta(hours=24)   | {str(TD_24H):30} | {'':30} |
| TD_01D = datetime.timedelta(days=1)     | {str(TD_01D):30} | {'':30} |
| TD_07D = datetime.timedelta(days=7)     | {str(TD_07D):30} | {'':30} |
| TD_30D = datetime.timedelta(days=30)    | {str(TD_30D):30} | {'':30} |
| TD_90D = datetime.timedelta(days=90)    | {str(TD_90D):30} | {'':30} |
|                                         | {'':30} | {'':30} |
| Relative datetime from delta            | {'':30} | {'':30} |
| dt_qtr_beg = datetime.date(2023, 7, 30)               | {str(datetime.date(2023, 7, 30)):30} | 
| dt_qtr_end = dt_qtr_beg + datetime.timedelta(days=90) | {str(dt_qtr_beg + datetime.timedelta(days=90)):30} | 
| dt_2y_before_fy24_end = dt_fy24_end - datetime.timedelta(days=730) | {str(dt_fy24_end - datetime.timedelta(days=730)):30} | 
|                                         | {'':30} | {'':30} |
| TimeDelta Constructors                  | {'':30} | {'':30} |
| datetime.timedelta(days=0)              | {str(datetime.timedelta(days=0)):30} | {'':30} |
| datetime.timedelta(weeks=2)             | {str(datetime.timedelta(weeks=2)):30} | {'':30} |
| datetime.timedelta(days=1)              | {str(datetime.timedelta(days=1)):30} | {'':30} |
| datetime.timedelta(hours=24)            | {str(datetime.timedelta(hours=24)):30} | {'':30} |
| datetime.timedelta(days=365)            | {str(datetime.timedelta(days=365)):30} | {'':30} |
| 10 * td_year                            | {str(10*datetime.timedelta(days=365)):30} | {'':30} |
|                                         | {'':30} | {'':30} |
| TimeDelta Attributes                    | {'':30} | {'':30} |
| TD_07D                                  | {str(TD_07D):30} | timedelta |
| TD_07D.days                             | {str(TD_07D.days):30} | Between -999,999,999 and 999,999,999 inclusive. |
| TD_07D.seconds                          | {str(TD_07D.seconds):30} | 0 and 86,399 inclusive |
| TD_07D.microseconds                     | {str(TD_07D.microseconds):30} | Between 0 and 999,999 inclusive |
| TD_07D.total_seconds()                  | {str(TD_07D.total_seconds()):30} | Return the total number of seconds contained in the duration |

"""
)

assert timedelta(days=1).seconds == timedelta(hours=24).seconds, "1 day == 24 hours"

print(
    f"""

-------------------------------------------------------------------------------
Timestamps (seconds from the Unix epoch)
-------------------------------------------------------------------------------

t_now = datetime.time()  # time
now_str = t.strftime("HH:MM:SS")
print(f"now isinstance int: {isinstance(dt_now, int)}")      # now timestamp as int
print(f"now_str isinstance str: {isinstance(dt_now, str)}")  # verify timestamp is string
"""
)

# Convert any timestamp to UTC using the 'second' and 'utc' args:
# Local (int) = {'%s' | strftime(second=0) | int}
# UTC   (int) = {'%s' | strftime(second=0, utc=true) | int}
# Offset = {'%s' | strftime(second=0, utc=true) | int}


print(
    f"""

-------------------------------------------------------------------------------
strftime(): Timestamp Formatting of date, datetime, time classes
-------------------------------------------------------------------------------

| What                                      | Example                        | Description |
|-------------------------------------------|--------------------------------|-------------|
| dt_now.strftime('%Y-%m-%d')               | {str(dt_now.strftime('%Y-%m-%d')):20} | Display now as year-month-day |
| dt_now.strftime('%H:%M:%S')               | {str(dt_now.strftime('%H:%M:%S')):20} | Display now as hour:min:sec |
| dt_now.strftime(FS_ISO8601_DATE)          | {str(dt_now.strftime(FS_ISO8601_DATE)):20} | Display now as date only |
| dt_now.strftime(FS_ISO8601_TIME)          | {str(dt_now.strftime(FS_ISO8601_TIME)):20} | Display now as time only |
| dt_now.strftime(FS_ISO8601_UTC)           | {str(dt_now.strftime(FS_ISO8601_UTC)):20} | Display now as UTC |
| datetime.date(1,1,1).strftime('%Y-%m-%d') | {str(datetime.date(1,1,1).strftime('%Y-%m-%d')):20} # First year |
| datetime.datetime.fromtimestamp(0).replace(tzinfo=None).strftime(FS_ISO8601_DT) {str(datetime.datetime.fromtimestamp(0).replace(tzinfo=None).strftime(FS_ISO8601_DT)):20} | Start of the Unix epoch (local time) |
| datetime.datetime.fromtimestamp(0).strftime(FS_ISO8601_UTC) | {str(datetime.datetime.fromtimestamp(0).strftime(FS_ISO8601_UTC)):20} | Start of the Unix epoch (local time in UTC) |

# Use the `datetime` object's instance methods after conversion:

| What                           | Example                        | Description                    |
|--------------------------------|--------------------------------|--------------------------------|
| dt_now.date()                  | {str(dt_now.date()):30} | {'':30} |
| dt_now.time()                  | {str(dt_now.time()):30} | {'':30} |
| dt_now.timetz()                | {str(dt_now.timetz()):30} | {'':30} |
| dt_now.timestamp()             | {str(dt_now.timestamp()):30} | {"(float)":30} |
|                                | {'':30} | {'':30} |
| dt_now.astimezone(tz=None)     | {str(dt_now.astimezone(tz=None)):30} | {'':30} |
| dt_now.utcoffset()             | {str(dt_now.utcoffset()):30} | {'':30} |
| dt_now.dst()                   | {str(dt_now.dst()):30} | If tzinfo is None, returns None | 
| dt_now.tzname()                | {str(dt_now.tzname()):30} | If tzinfo is None, returns None | 
| dt_now.timetuple()             | {str(dt_now.timetuple()):30} | {'':30} |
| dt_now.utctimetuple()          | {str(dt_now.utctimetuple()):30} | {'':30} |
| dt_now.toordinal()             | {str(dt_now.toordinal()):30} | {'':30} |
| dt_now.timestamp()             | {str(dt_now.timestamp()):30} | {'':30} |
| dt_now.weekday()               | {str(dt_now.weekday()):30} | {'':30} |
| dt_now.isoweekday()            | {str(dt_now.isoweekday()):30} | {'':30} |
| dt_now.isocalendar()           | {str(dt_now.isocalendar()):30} | {'':30} |
| dt_now.isoformat()             | {str(dt_now.isoformat()):30} | {'':30} |
| dt_now.ctime()                 | {str(dt_now.ctime()):30} | {'':30} |

"""
)


date1_str = "2020-01-01T00:00:00Z"
date2_str = "2021-01-01T00:00:00Z"

print(
    f"""

-------------------------------------------------------------------------------
datetime Differences
-------------------------------------------------------------------------------

date1_str: {str(date1_str):20}
date2_str: {str(date2_str):20}
date1_dt:  {str(datetime.datetime.strptime(date1_str, FS_ISO8601_UTC)):20}
date2_dt:  {str(datetime.datetime.strptime(date2_str, FS_ISO8601_UTC)):20}
date_diff: {str((datetime.datetime.strptime(date2_str, FS_ISO8601_UTC) - datetime.datetime.strptime(date1_str, FS_ISO8601_UTC)).total_seconds()):20} (seconds)
"""
)

# -----------------------------------------------------------------------------
# datetime.strptime(): Parse date strings to datetime object
# datetime.strptime(date_string, format)
# -----------------------------------------------------------------------------
datetime.datetime.strptime("2020-02-02 02:02:02", FS_ISO8601_DT)  # datetime requires format '%Y-%m-%d %H:%M:%S'
d = datetime.datetime.strptime("2020-02-02 02:02:02", FS_ISO8601_DT).date()
t = datetime.datetime.strptime("2020-02-02 02:02:02", FS_ISO8601_DT).time()
# isoformat = {(FS_DATETIME | strftime(now) | to_datetime).isoformat()}
# utcoffset = {(FS_DATETIME | strftime(now) | to_datetime).utcoffset()}
# timetz = {(FS_DATETIME | strftime(now) | to_datetime).timetz()} # None if no tzinfo
# dst = {(FS_DATETIME | strftime(now) | to_datetime).dst()}  # None if no tzinfo
# tzname = {(FS_DATETIME | strftime(now) | to_datetime).tzname()}
# weekday = {(FS_DATETIME | strftime(now) | to_datetime).weekday()} # Monday is 0 and Sunday is 6
# isoweekday = {(FS_DATETIME | strftime(now) | to_datetime).isoweekday()} # Monday is 1 and Sunday is 7
# toordinal = {(FS_DATETIME | strftime(now) | to_datetime).toordinal()} # Days since Christ

print(
    f"""

Widths

| What          | Example              | Description                    |
|---------------|----------------------|--------------------------------|
| 5             | {5} | {'':30} |
| 5             | {5:5} | {'':30} |
| 5             | {5:20} | {'':30} |
| 5             | {5:20.2f} | {'':30} |
| 5.0           | {float(5):20.2f} | {'':30} |
| dt_now.date() | {str(dt_now.date()):^20} | {'center':30} |
| dt_now.date() | {str(dt_now.date()):>20} | {'right ':30} |
| dt_now.date() | {str(dt_now.date()):<20} | {'left  ':30} |
| dt_now.date() | {str(dt_now.date()):20} | {'':30} |

"""
)
