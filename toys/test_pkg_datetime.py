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

#
# Constants
#
# datetime.MINYEAR # smallest year number allowed in a date or datetime object. MINYEAR is 1.
# datetime.MAXYEAR # largest year number allowed in a date or datetime object. MAXYEAR is 9999.
# datetime.UTC     # Alias for the UTC time zone singleton datetime.timezone.utc.

#
# DateTime formats are created folllowing the Python strftime
# See https://docs.python.org/3/library/time.html#time.strftime
#
# | Directive | Meaning                                                                           |
# |-----------|-----------------------------------------------------------------------------------|
# | `%a`      | Locale’s abbreviated weekday name.                                                |
# | `%A`      | Locale’s full weekday name.                                                       |
# | `%b`      | Locale’s abbreviated month name.                                                  |
# | `%B`      | Locale’s full month name.                                                         |
# | `%c`      | Locale’s appropriate date and time representation.                                |
# | `%d`      | Day of the month as a decimal number \[01,31\].                                   |
# | `%H`      | Hour (24-hour clock) as a decimal number \[00,23\].                               |
# | `%I`      | Hour (12-hour clock) as a decimal number \[01,12\].                               |
# | `%j`      | Day of the year as a decimal number \[001,366\].                                  |
# | `%m`      | Month as a decimal number \[01,12\].                                              |
# | `%M`      | Minute as a decimal number \[00,59\].                                             |
# | `%p`      | Locale’s equivalent of either AM or PM.                                           |
# | `%s`      | Seconds since the Unix epoch as a decimal number.                                 |
# | `%S`      | Second as a decimal number \[00,61\].                                             |
# | `%U`      | Week # of year as a decimal number (Sunday is first DoW) \[00,53\]                |
# |           | All days in a new year preceding the first Sunday are considered to be in week 0. |
# | `%w`      | Weekday as a decimal number \[0(Sunday),6\].                                      |
# | `%W`      | Week # of year as a decimal number (Monday as first DOW) \[00,53\]                |
# |           | All days in a new year preceding the first Monday are considered to be in week 0. |
# | `%x`      | Locale’s appropriate date representation.                                         |
# | `%X`      | Locale’s appropriate time representation.                                         |
# | `%y`      | Year without century as a decimal number \[00,99\]                                |
# | `%Y`      | Year with century as a decimal number.                                            |
# | `%z`      | Time zone offset as a +/- time difference from UTC/GMT of the form ±HHMM          |
# | `%Z`      | Time zone name (no characters if no time zone exists). 🛑 Deprecated.             |
# | `%%`      | A literal `'%'` character.                                                        |
#
# For ISO8601 format details, see
# - https://en.wikipedia.org/wiki/ISO_8601 : ISO8601
# - https://ijmacd.github.io/rfc3339-iso8601/ : RFC 3339 vs ISO 8601
# - https://www.rfc-editor.org/rfc/rfc3339.html : Date and Time on the Internet: Timestamps
#

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

# Time Zones: {time}Z | {time}±hh:mm | {time}±hhmm | {time}±hh
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

YEAR = 2000
MONTH = 1
DAY = 1
WEEK = 1
ORDINAL_1 = 1
EPOCH_STR = "1970-01-01 00:00:00"  # FS_ISO8601_DT format

dt_now = datetime.datetime.now()  # current datetime in local timezone, since the Unix Epoch
ts_now = datetime.datetime.now().timestamp()  # current timestamp, in seconds, since the Unix Epoch
d_now = datetime.datetime.now().date()
t_now = datetime.datetime.now().timestamp()

print(
    f"""
dt_now: { datetime.datetime.now()             } # current datetime in local timezone, since the Unix Epoch
ts_now: { datetime.datetime.now().timestamp() } # current timestamp, in seconds, since the Unix Epoch
d_now : { datetime.datetime.now().date()      } 
t_now : { datetime.datetime.now().timestamp() }
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

Date Constructors

date_today        = { datetime.date.today()                          } # current local date. This is equivalent to date.fromtimestamp(time.time()).
date_from_ts      = { datetime.date.fromtimestamp(dt.timestamp())    } # local date of the POSIX timestamp
date_from_ord     = { datetime.date.fromordinal(ORDINAL_1)           } # date in the proleptic Gregorian ordinal, where January 1 of year 1 has ordinal 1.
date_from_iso     = { datetime.date.fromisoformat("2000-01-01")      } # date in a valid ISO 8601 format; datetime.date(2000, 1, 1)
date_from_iso     = { datetime.date.fromisoformat("20191204")        } # datetime.date(2019, 12, 4)
date_from_iso_cal = { datetime.date.fromisocalendar(YEAR, WEEK, DAY) } # date in ISO calendar; inverse of date.isocalendar().
date_from_iso_cal = { datetime.date.fromisoformat("2021-W01-1")      } # datetime.date(2021, 1, 4)

date Class Atributes

datetime.date.min        { datetime.date.min        } # The earliest representable date, date(MINYEAR, 1, 1).
datetime.date.max        { datetime.date.max        } # The latest representable date, date(MAXYEAR, 12, 31).
datetime.date.resolution { datetime.date.resolution } # The smallest possible difference between non-equal date objects, timedelta(days=1).
datetime.date.year       { datetime.date.year       } # Between MINYEAR and MAXYEAR inclusive.
datetime.date.month      { datetime.date.month      } # Between 1 and 12 inclusive.
datetime.date.day        { datetime.date.day        } # Between 1 and the number of days in the given month of the given year.

date Instance methods

datetime.date(2000, 12, 26) { datetime.date(2000, 12, 26) }
d.replace(year=YEAR, month=MONTH, day=DAY)  # same date, except for parameters given new values by keyword args
d.replace(day=31)      { d.replace(day=31)      }
d.timetuple()          { d.timetuple()          } # Return a time.struct_time. hours, minutes and seconds are 0, and the DST flag is -1.
d.toordinal()          { d.toordinal()          } # Return the proleptic Gregorian ordinal of the date, where January 1 of year 1 has ordinal 1. For any date object d, date.fromordinal(d.toordinal()) == d.
d.weekday()            { d.weekday()            } # Return the day of the week as an integer, where Monday is 0 and Sunday is 6. For example, date(2002, 12, 4).weekday() == 2, a Wednesday. See also isoweekday().
d.isoweekday()         { d.isoweekday()         } # Return the day of the week as an integer, where Monday is 1 and Sunday is 7. For example, date(2002, 12, 4).isoweekday() == 3, a Wednesday. See also weekday(), isocalendar().
d.isocalendar()        { d.isocalendar()        } # Return a named tuple object with three components: year, week and weekday.
d.isoformat()          { d.isoformat()          } # Return a string representing the date in ISO 8601 format, YYYY-MM-DD:
d.ctime()              { d.ctime()              } # Return a string representing the date:
d.strftime(FS_ISO8601) { d.strftime(FS_ISO8601_DT) } # Return a string representing the date, controlled by an explicit format string
"""
)

# -----------------------------------------------------------------------------
# datetime
# A datetime object is a single object containing all the information from a date object and a time object.
# class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
# -----------------------------------------------------------------------------

dt = datetime.datetime.now()  # 2023-10-28 12:30:16.479646
today = datetime.date.today()

print(
    f"""

DateTime Constructors

dt_from_ts = datetime.datetime.fromtimestamp(dt.timestamp(), tz=None)  # tz=None uses the local system's timezone

datetime.datetime.now()             { datetime.datetime.now()             } # 2023-11-05 10:43:30.552238
datetime.datetime.now().timestamp() { datetime.datetime.now().timestamp() } # 1699209810.552254

datetime.datetime.today()      { datetime.datetime.today()      } # ⚠ Current local date or naive datetime
datetime.date.today()          { datetime.date.today()          } # 
datetime.datetime.now()        { datetime.datetime.now()        } # ⚠ naive datetime is timezone unaware!
datetime.datetime.now(tz=None) { datetime.datetime.now(tz=None) } # tz=None uses the local system's timezone

datetime.datetime.now(tz=datetime.timezone.utc)  # Built-in: UTC
pacific_tz = zoneinfo.ZoneInfo("America/Los_Angeles")
datetime_now_pt = now.replace(tzinfo=pacific_tz)

datetime.datetime.now(tz=None)                      { datetime.datetime.now(tz=None)                      } # TZ-aware datetime from current tz time.
datetime.datetime.utcnow()                          { datetime.datetime.utcnow()                          } # ⌫␡ Deprecated Naive datetime from current UTC time.
datetime.datetime.utcfromtimestamp(dt.timestamp())  { datetime.datetime.utcfromtimestamp(dt.timestamp())  } #
datetime.datetime.combine(d, t, tzinfo=None)        { datetime.datetime.combine(d, t, tzinfo=None)        } # tzinfo = None is naive
datetime.datetime.strptime("20000101", FS_YYYYMMDD) { datetime.datetime.strptime("20000101", FS_YYYYMMDD) } #

# Python 3.12+ safe constructors
# Python 3.11 or newer, may replace datetime.timezone.utc with datetime.UTC

datetime.datetime.now(datetime.UTC)                            # tz=None uses the local system's timezone
datetime.datetime.fromtimestamp(dt.timestamp(), datetime.UTC)  # aware_utcfromtimestamp(timestamp)
datetime.datetime.now(datetime.UTC).replace(tzinfo=None)       # naive_utcnow()
datetime.datetime.fromtimestamp(dt.timestamp(), datetime.UTC).replace(tzinfo=None)  # naive_utcfromtimestamp(timestamp)

datetime attributes

datetime.datetime.max        { datetime.datetime.max        } # latest datetime: datetime(MAXYEAR, 12, 31, 23, 59, 59, 999999, tzinfo=None)
datetime.datetime.resolution { datetime.datetime.resolution } # smallest difference between datetime objects, timedelta(microseconds=1)

datetime Instance Attributes (read-only)

dt.year        { dt.year        } # Between MINYEAR and MAXYEAR inclusive.
dt.month       { dt.month       } # Between 1 and 12 inclusive.
dt.day         { dt.day         } # Between 1 and the number of days in the given month of the given year.
dt.hour        { dt.hour        } # In range(24).
dt.minute      { dt.minute      } # In range(60).
dt.second      { dt.second      } # In range(60).
dt.microsecond { dt.microsecond } # In range(1000000).
dt.tzinfo      { dt.tzinfo      } # object passed as tzinfo argument to constructor, or None
dt.fold        { dt.fold        } # In [0, 1]. Used to disambiguate wall times during a repeated interval.

datetime Instance Methods

datetime.datetime.now() { datetime.datetime.now() }

dt.today()      { dt.today()     } # 2023-10-28 12:30:15.475201
dt.timestamp()  { dt.timestamp() } # 1698521416.47965
dt.date()       { dt.date()      } # Return `date` object with same year, month and day
dt.time()       { dt.time()      } # Return datetime's `time` component however tzinfo is None.
dt.timetz()     { dt.timetz()    } # Return DateTime's `time` component with tzinfo
dt.replace(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)

# timezone aware!
dt.astimezone(tz=None)  { dt.astimezone(tz=None)  } # Return a datetime with new tzinfo attribute tz's local time
dt.utcoffset()          { dt.utcoffset()          } # Returns self.tzinfo.utcoffset(self), otherwise None
dt.dst()                { dt.dst()                } # If tzinfo is None, returns None, else returns self.tzinfo.dst(self)
dt.tzname()             { dt.tzname()             } # If tzinfo is None, returns None, else returns self.tzinfo.tzname(self)
dt.timetuple()          { dt.timetuple()          } # Return a time.struct_time such as returned by time.localtime().
dt.utctimetuple()       { dt.utctimetuple()       } # 
dt.toordinal()          { dt.toordinal()          } # Return the proleptic Gregorian ordinal of the date; same as dt.date().toordinal()
dt.timestamp()          { dt.timestamp()          } # Return POSIX timestamp
dt.replace(tzinfo=None) { dt.replace(tzinfo=None) } # attach/change a time zone (tz) object to datetime without adjustment
dt.weekday()            { dt.weekday()            } # day of the week as an integer, where Monday is 0 and Sunday is 6
dt.isoweekday()         { dt.isoweekday()         } # day of the week as an integer, where Monday is 1 and Sunday is 7
dt.isocalendar()        { dt.isocalendar()        } # named tuple with 3 components: year, week, weekday; same as dt.date().isocalendar()
dt.isoformat(sep="T", timespec="auto") { dt.isoformat(sep="T", timespec="auto") } # ISO 8601: YYYY-MM-DDTHH:MM:SS.ffffff, if microsecond is not 0
dt.ctime()              { dt.ctime() } # a string representing the date and time: 'Wed Dec  4 20:30:40 2002'
dt.strftime("%s")       { int(dt.strftime("%s")) }  # seconds!
dt.strftime(FS_ISO8601_DT) { dt.strftime(FS_ISO8601_DT) } # format the date and time using for format specifier string
"""
)


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


# -----------------------------------------------------------------------------
# time
# A time object represents a (local) time of day, independent of any particular day, and subject to adjustment via a tzinfo object.
# class datetime.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
# -----------------------------------------------------------------------------

print(
    f"""

# Constructors
# t = time.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)
datetime.time.fromisoformat("01:02:03")        { datetime.time.fromisoformat("01:02:03")        } # Return a time from a valid ISO 8601 format
datetime.time.fromisoformat("04:23:01")        { datetime.time.fromisoformat("04:23:01")        } # datetime.time(4, 23, 1)
datetime.time.fromisoformat("T04:23:01")       { datetime.time.fromisoformat("T04:23:01")       } # datetime.time(4, 23, 1)
datetime.time.fromisoformat("T042301")         { datetime.time.fromisoformat("T042301")         } # datetime.time(4, 23, 1)
datetime.time.fromisoformat("04:23:01.000384") { datetime.time.fromisoformat("04:23:01.000384") } # datetime.time(4, 23, 1, 384)
datetime.time.fromisoformat("04:23:01,000384") { datetime.time.fromisoformat("04:23:01,000384") } # datetime.time(4, 23, 1, 384)
datetime.time.fromisoformat("04:23:01+04:00")  { datetime.time.fromisoformat("04:23:01+04:00")  } # datetime.time(4, 23, 1, tzinfo=datetime.timezone(datetime.timedelta(seconds=14400)))
datetime.time.fromisoformat("04:23:01Z")       { datetime.time.fromisoformat("04:23:01Z")       } # datetime.time(4, 23, 1, tzinfo=datetime.timezone.utc)
datetime.time.fromisoformat("04:23:01+00:00")  { datetime.time.fromisoformat("04:23:01+00:00")  } # datetime.time(4, 23, 1, tzinfo=datetime.timezone.utc)

# Class attributes:
datetime.time.min        { datetime.time.min        } # The earliest representable time, time(0, 0, 0, 0).
datetime.time.max        { datetime.time.max        } # The latest representable time, time(23, 59, 59, 999999).
datetime.time.resolution { datetime.time.resolution } # The smallest possible difference between non-equal time objects, timedelta(microseconds=1), although note that arithmetic on time objects is not supported.

# Instance attributes (read-only):
t.hour        { t.hour        } # In range(24).
t.minute      { t.minute      } # In range(60).
t.second      { t.second      } # In range(60).
t.microsecond { t.microsecond } # In range(1000000).
t.tzinfo      { t.tzinfo      } # The object passed as the tzinfo argument to the time constructor, or None if none was passed.
t.fold        { t.fold        } # In [0, 1]. Used to disambiguate wall times during a repeated interval.

# Instance methods:
t.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.UTC, fold=0)  # Same time, updated values. tzinfo=None is naive
t.isoformat(timespec="auto")         { t.isoformat(timespec="auto")         } # Return a string representing the time in ISO 8601 format, where:
t.isoformat(timespec='auto')         { t.isoformat(timespec='auto')         } # Same as 'seconds' if microsecond is 0, same as 'microseconds' otherwise.
t.isoformat(timespec='hours')        { t.isoformat(timespec='hours')        } # Include the hour in the two-digit HH format.
t.isoformat(timespec='minutes')      { t.isoformat(timespec='minutes')      } # Include hour and minute in HH:MM format.
t.isoformat(timespec='seconds')      { t.isoformat(timespec='seconds')      } # Include hour, minute, and second in HH:MM:SS format.
t.isoformat(timespec='milliseconds') { t.isoformat(timespec='milliseconds') } # Include full time, but truncate fractional second part to milliseconds. HH:MM:SS.sss format.
t.isoformat(timespec='microseconds') { t.isoformat(timespec='microseconds') } # Include full time in HH:MM:SS.ffffff format.

t.__str__()               { t.__str__()               } # For a time t, str(t) is equivalent to t.isoformat().
t.strftime(FS_HH_MM_SS)   { t.strftime(FS_HH_MM_SS)   } # Return a string representing the time, with format string. See also strftime() and strptime()
t.__format__(FS_HH_MM_SS) { t.__format__(FS_HH_MM_SS) } # Same as time.strftime(). See also strftime() and strptime() Behavior and time.isoformat().
t.utcoffset()             { t.utcoffset()             } # If tzinfo is None, returns None, else returns self.tzinfo.utcoffset(None), and raises an exception if the latter doesn’t return None or a timedelta object with magnitude less than one day.
t.dst()                   { t.dst()                   } # If tzinfo is None, returns None, else returns self.tzinfo.dst(None), and raises an exception if the latter doesn’t return None, or a timedelta object with magnitude less than one day.
t.tzname()                { t.tzname()                } # If tzinfo is None, returns None, else returns self.tzinfo.tzname(None), or raises an exception if the latter doesn’t return None or a string object.
"""
)

# -----------------------------------------------------------------------------
# tzinfo
# datetime.tzinfo
# An abstract base class, and should not be instantiated directly. Define a subclass to capture information about a time zone.
# An instance of (a concrete subclass of) tzinfo can be passed to the constructors for datetime and time objects.
# The latter objects view their attributes as being in local time, and the tzinfo object supports methods revealing offset of local time from UTC, the name of the time zone, and DST offset, all relative to a date or time object passed to them.
# -----------------------------------------------------------------------------

tzi = datetime.datetime.now(tz=zoneinfo.ZoneInfo("UTC"))
tzi.utcoffset()  # offset of local time from UTC as a timedelta object: positive east of UTC, negative west of UTC.
tzi.dst()  # the daylight saving time (DST) adjustment, as a timedelta object or None if DST information isn’t known.
tzi.tzname()  # time zone name of the datetime object. May be anything: "UTC", "-500", "-5:00", "EDT", "US/Eastern"... None if unknown.

# -----------------------------------------------------------------------------
# timezone
# The timezone class is a *subclass* of tzinfo - each instance represents a time zone defined by a fixed offset from UTC.
# class datetime.timezone(offset, name=None) where offset is a timedelta object representing the difference between the local time and UTC
# -----------------------------------------------------------------------------

tz = datetime.timezone(datetime.timedelta(hours=-8), name="HBC")
utc = datetime.timezone(datetime.timedelta(0), name="UTC")

# Class Attributes
datetime.timezone.utc  # The UTC time zone, timezone(timedelta(0)).

# Class methods
tz.utcoffset(None)  # Return the fixed value specified when the timezone instance is constructed.
tz.tzname(None)  # Return the fixed value specified when the timezone instance is constructed.
tz.dst(None)  # Always returns None.
# tz.fromutc( datetime.datetime.now(tz=None) )  # Return dt + offset. The dt argument must be an *aware* datetime instance, with tzinfo set to self.

# Class attributes
# timezone.utc # The UTC time zone, timezone(timedelta(0)).


# -----------------------------------------------------------------------------
# timedelta
# A timedelta object represents a duration, the difference between two datetime or date instances.
# class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
# -----------------------------------------------------------------------------

from datetime import timedelta

td = datetime.timedelta(minutes=60)

# FY24,2023-07-30,2024-07-27
dt_fy24_beg = datetime.date(2023, 7, 30)
dt_fy24_end = datetime.date(2024, 7, 27)

print(
    f"""

timedelta

timedelta(days=0)   | { timedelta(days=0)   } 
timedelta(weeks=2)  | { timedelta(weeks=2)  } 
timedelta(days=1)   | { timedelta(days=1)   } 
timedelta(hours=24) | { timedelta(hours=24) } 
timedelta(days=365) | { timedelta(days=365) } 
10 * td_year        | { 10*timedelta(days=365)}

td                 | { td                 } # timedelta
td.days            | { td.days            } # Between -999,999,999 and 999,999,999 inclusive.
td.seconds         | { td.seconds         } # 0 and 86,399 inclusive
td.microseconds    | { td.microseconds    } # Between 0 and 999,999 inclusive
td.total_seconds() | { td.total_seconds() } # Return the total number of seconds contained in the duration    

dt_period_end_2y  | { dt_fy24_end - datetime.timedelta(days=730) }
dt_period_end_1y  | { dt_fy24_end - datetime.timedelta(days=365) }
dt_period_end_90d | { dt_fy24_end - datetime.timedelta(days=90)  }
"""
)

assert timedelta(days=1).seconds == timedelta(hours=24).seconds, "1 day == 24 hours"

# -----------------------------------------------------------------------------
# Timestamps (seconds from the Unix epoch)
# -----------------------------------------------------------------------------

t_now = datetime.time()  # time
now_str = t.strftime("HH:MM:SS")
# print(f"now isinstance int: {isinstance(now, int)}")  # now timestamp as int
# print(f"now_str isinstance str: {isinstance(now, now_str)}")  # verify timestamp is string

# Convert any timestamp to UTC using the 'second' and 'utc' args:
# Local (int) = { '%s' | strftime(second=0) | int }
# UTC   (int) = { '%s' | strftime(second=0, utc=true) | int }
# Offset = { '%s' | strftime(second=0, utc=true) | int }

# -----------------------------------------------------------------------------
# strftime(): Timestamp Formatting of date, datetime, time classes
# -----------------------------------------------------------------------------

print(
    f"""
dt_now.strftime('%Y-%m-%d')      | { dt_now.strftime('%Y-%m-%d')      } # Display now as year-month-day
dt_now.strftime('%H:%M:%S')      | { dt_now.strftime('%H:%M:%S')      } # Display now as hour:min:sec
dt_now.strftime(FS_ISO8601_DATE) | { dt_now.strftime(FS_ISO8601_DATE) } # Display now as date only
dt_now.strftime(FS_ISO8601_TIME) | { dt_now.strftime(FS_ISO8601_TIME) } # Display now as time only
dt_now.strftime(FS_ISO8601_UTC)  | { dt_now.strftime(FS_ISO8601_UTC)  } # Display now as UTC
datetime.date(1,1,1).strftime('%Y-%m-%d') { datetime.date(1,1,1).strftime('%Y-%m-%d') } # First year
datetime.datetime.fromtimestamp(0).replace(tzinfo=None).strftime(FS_ISO8601_DT) { datetime.datetime.fromtimestamp(0).replace(tzinfo=None).strftime(FS_ISO8601_DT) } # Start of the Unix epoch (local time)
datetime.datetime.fromtimestamp(0).strftime(FS_ISO8601_UTC) { datetime.datetime.fromtimestamp(0).strftime(FS_ISO8601_UTC) } # Start of the Unix epoch (local time in UTC)
"""
)

# Standard Date Format Strings
print(
    f"""

Standard Date Format Strings

FS_YYYYMMDD     | { FS_YYYYMMDD     } | { dt_now.strftime(FS_YYYYMMDD    ) }
FS_YYYY_MM_DD   | { FS_YYYY_MM_DD   } | { dt_now.strftime(FS_YYYY_MM_DD  ) }

# Times
FS_HHMM         | { FS_HHMM         } | { dt_now.strftime(FS_HHMM        ) }
FS_HH_MM        | { FS_HH_MM        } | { dt_now.strftime(FS_HH_MM       ) }
FS_HHMMSS       | { FS_HHMMSS       } | { dt_now.strftime(FS_HHMMSS      ) }
FS_HH_MM_SS     | { FS_HH_MM_SS     } | { dt_now.strftime(FS_HH_MM_SS    ) }
FS_HHMMSS_SSS   | { FS_HHMMSS_SSS   } | { dt_now.strftime(FS_HHMMSS_SSS  ) }
FS_HH_MM_SS_SSS | { FS_HH_MM_SS_SSS } | { dt_now.strftime(FS_HH_MM_SS_SSS) }

# Time Zones: {FS_TZ_UTC}Z | {FS_TZ_OFFSET}±hh:mm {FS_TZ_NAME}±hh

# ISO8601
FS_ISO8601_DATE | { FS_ISO8601_DATE } | { dt_now.strftime(FS_ISO8601_DATE) }
FS_ISO8601_TIME | { FS_ISO8601_TIME } | { dt_now.strftime(FS_ISO8601_TIME) }
FS_ISO8601_UTC  | { FS_ISO8601_UTC  } | { dt_now.strftime(FS_ISO8601_UTC ) }
FS_ISO8601_DT   | { FS_ISO8601_DT   } | { dt_now.strftime(FS_ISO8601_DT  ) }

# Other Date & Time formats
FS_ATOM         | { FS_ATOM         } | { dt_now.strftime(FS_ATOM        ) }
FS_COOKIE       | { FS_COOKIE       } | { dt_now.strftime(FS_COOKIE      ) }
FS_RSS          | { FS_RSS          } | { dt_now.strftime(FS_RSS         ) }
FS_W3C          | { FS_W3C          } | { dt_now.strftime(FS_W3C         ) }
FS_RFC822       | { FS_RFC822       } | { dt_now.strftime(FS_RFC822      ) }
FS_RFC850       | { FS_RFC850       } | { dt_now.strftime(FS_RFC850      ) }
FS_RFC1036      | { FS_RFC1036      } | { dt_now.strftime(FS_RFC1036     ) }
FS_RFC1123      | { FS_RFC1123      } | { dt_now.strftime(FS_RFC1123     ) }
FS_RFC2822      | { FS_RFC2822      } | { dt_now.strftime(FS_RFC2822     ) }
FS_RFC3339      | { FS_RFC3339      } | { dt_now.strftime(FS_RFC3339     ) }
"""
)

# Use the `datetime` object's instance methods after conversion:
print(
    f"""
dt_now.date()      { dt_now.date() }
dt_now.time()      { dt_now.time() }
dt_now.timetz()    { dt_now.timetz() }
dt_now.timestamp() { dt_now.timestamp() } (float)

.astimezone(tz=None) { dt_now.astimezone(tz=None) }
.utcoffset()         { dt_now.utcoffset() }
.dst()               { dt_now.dst() } # If tzinfo is None, returns None
.tzname()            { dt_now.tzname() } # If tzinfo is None, returns None
.timetuple()         { dt_now.timetuple() }
.utctimetuple()      { dt_now.utctimetuple() }
.toordinal()         { dt_now.toordinal() }
.timestamp()         { dt_now.timestamp() }
.weekday()           { dt_now.weekday() }
.isoweekday()        { dt_now.isoweekday() }
.isocalendar()       { dt_now.isocalendar() }
.isoformat()         { dt_now.isoformat() }
.ctime()             { dt_now.ctime() }
"""
)


# -----------------------------------------------------------------------------
# datetime Differences
# -----------------------------------------------------------------------------
date1_str = "2020-01-01T00:00:00Z"
date2_str = "2021-01-01T00:00:00Z"

print(
    f"""
date1_str: {date1_str}
date2_str: {date2_str}
date1_dt:  {datetime.datetime.strptime(date1_str, FS_ISO8601_UTC)}
date2_dt:  {datetime.datetime.strptime(date2_str, FS_ISO8601_UTC)}
date_diff: {(datetime.datetime.strptime(date2_str, FS_ISO8601_UTC) - datetime.datetime.strptime(date1_str, FS_ISO8601_UTC)).total_seconds()} (seconds)
"""
)

# -----------------------------------------------------------------------------
# datetime.strptime(): Parse date strings to datetime object
# datetime.strptime(date_string, format)
# -----------------------------------------------------------------------------
datetime.datetime.strptime("2020-02-02 02:02:02", FS_ISO8601_DT)  # datetime requires format '%Y-%m-%d %H:%M:%S'
d = datetime.datetime.strptime("2020-02-02 02:02:02", FS_ISO8601_DT).date()
t = datetime.datetime.strptime("2020-02-02 02:02:02", FS_ISO8601_DT).time()
# isoformat = { (FS_DATETIME | strftime(now) | to_datetime).isoformat() }
# utcoffset = { (FS_DATETIME | strftime(now) | to_datetime).utcoffset() }
# timetz = { (FS_DATETIME | strftime(now) | to_datetime).timetz() } # None if no tzinfo
# dst = { (FS_DATETIME | strftime(now) | to_datetime).dst() }  # None if no tzinfo
# tzname = { (FS_DATETIME | strftime(now) | to_datetime).tzname() }
# weekday = { (FS_DATETIME | strftime(now) | to_datetime).weekday() } # Monday is 0 and Sunday is 6
# isoweekday = { (FS_DATETIME | strftime(now) | to_datetime).isoweekday() } # Monday is 1 and Sunday is 7
# toordinal = { (FS_DATETIME | strftime(now) | to_datetime).toordinal() } # Days since Christ
