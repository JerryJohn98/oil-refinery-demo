import logging
from datetime import timedelta

import pytz
from dateutil import parser


class AppTimeFormats:
    USER_META_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    USER_META_24_HR_FORMAT = "DD/MM/YYYY HH24:MI:SS"
    USER_META_24_HR_FORMAT_YYYY_MM_DD = "YYYY-MM-DD HH24:MI:SS"
    DFLT_MONTH_START = "%Y-%m-01 00:00:00"
    DFLT_DAY_START = "%Y-%m-%d 00:00:00"
    DFLT_DAY_END = "%Y-%m-%d 23:59:59"
    DFLT_YEAR_START = "%Y-01-01 00:00:00"
    DFLT_YEAR_END = "%Y-12-31 23:59:59"

    time_quick_ranges_list = [
        "today",
        "today_so_far",
        "this_week",
        "this_week_so_far",
        "this_month",
        "this_month_so_far",
        "this_year",
        "this_year_so_far",
        "yesterday",
        "day_before_yesterday",
        "this_day_last_week",
        "previous_week",
        "previous_month",
        "previous_year",
    ]
    YEARS = "years"
    MONTHS = "months"
    WEEKS = "weeks"
    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"

    DAY_ORDER_MON = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    MONTH_ORDER = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    DAY_ORDER_SUN = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    sql_date_format = {
        "dd/MM/yyyy HH:mm:ss": "dd/MM/yyyy HH:MI:ss",
        "dd/MM/yyyy HH:mm": "dd/MM/yyyy HH:MI",
        "dd/MM/yyyy HH:mm:ss:ms": "dd/MM/yyyy HH:MI:ss:ms",
        "dd-MM-yyyy HH:mm:ss": "dd-MM-yyyy HH:MI:ss",
        "dd-MM-yyyy HH:mm": "dd-MM-yyyy HH:MI",
        "yyyy/dd/MM HH:mm:ss": "yyyy/dd/MM HH:MI:ss",
        "yyyy/dd/MM HH:mm:ss:ms": "yyyy/dd/MM HH:MI:ss:ms",
        "yyyy-dd-MM HH:mm:ss": "yyyy-dd-MM HH:MI:ss",
        "yyyy-dd-MM HH:mm": "yyyy-dd-MM HH:MI",
        "yyyy/MM/dd HH:mm:ss": "yyyy/MM/dd HH:MI:ss",
        "dd-MM HH:mm:ss": "dd-MM HH:MI:ss",
        "dd/MM HH:mm:ss": "dd/MM HH:MI:ss",
        "MM-dd HH:mm:ss": "MM-dd HH:MI:ss",
        "MM/dd HH:mm:ss": "MM/dd HH:MI:ss",
        "dd-MM HH:mm": "dd-MM HH:MM",
        "dd/MM HH:mm": "dd/MM HH:MI",
        "MM-dd HH:mm": "MM-dd HH:MI",
        "MM/dd HH:mm": "MM/dd HH:MI",
        "yyyy/MM/dd HH:mm:ss:ms": "yyyy/MM/dd HH:MI:ss:ms",
        "yyyy-MM-dd HH:mm:ss": "yyyy-MM-dd HH:MI:ss",
        "dd/MM/yyyy": "dd/MM/yyyy",
        "dd-MM-yyyy": "dd-MM-yyyy",
        "yyyy/MM/dd": "yyyy/MM/dd",
        "yyyy-MM-dd": "yyyy-MM-dd",
        "MM/dd/yyyy": "MM/dd/yyyy",
        "MM-dd-yyyy": "MM-dd-yyyy",
        "dateMonth": "D Month",
        "monthDate": "Month D",
        "dateMonthYear": "D Month, YYYY",
        "yearDateMonth": "YYYY, D Month",
        "monthDateYear": "Month D, YYYY",
        "yearMonthDate": "YYYY, Month D",
        "monthYear": "Month, YYYY",
        "year": "YYYY",
        "month": "Month",
    }


class TimeDelta:
    def __init__(self):
        self.DFLT_MONTH_START = {"day": 1, "hour": 0, "minute": 0, "second": 0}
        self.DFLT_DAY_START = {"hour": 0, "minute": 0, "second": 0}
        self.DFLT_DAY_END = {"hour": 23, "minute": 59, "second": 59}
        self.DFLT_YEAR_START = {
            "month": 1,
            "day": 1,
            "hour": 0,
            "minute": 0,
            "second": 0,
        }
        self.DFLT_YEAR_END = {
            "month": 12,
            "day": 31,
            "hour": 23,
            "minute": 59,
            "second": 59,
        }
        self.zero_second = {"second": 0, "microsecond": 0}

    @staticmethod
    def get_project_day_start(project_info):
        day_start_time = project_info.get("additional_fields", {}).get("day_start")
        if day_start_time:
            tz = pytz.timezone(project_info["timezone"])
            day_start = parser.parse(day_start_time).replace(second=0).astimezone(tz)
            return day_start.hour, day_start.minute
        day_start_time = "00:00"
        hour, minute = int(day_start_time.split(":")[0]), int(
            day_start_time.split(":")[1]
        )
        return hour, minute

    def custom_day_end(self, project_info, default_end_date):
        try:
            selected_date = default_end_date
            default_end_date = default_end_date.replace(**self.DFLT_DAY_END)
            if not project_info:
                return default_end_date
            hour, minute = self.get_project_day_start(project_info)
            if hour == 0:
                return default_end_date
            elif hour > selected_date.hour >= 0:
                custom_day_end = default_end_date.replace(
                    hour=hour, minute=minute, second=0
                )
            else:
                # End time spills on next day
                custom_day_end = default_end_date.replace(
                    hour=hour, minute=minute, second=0
                ) + timedelta(days=1)
            return custom_day_end - timedelta(seconds=1)

        except Exception as e:
            logging.exception(e)
            raise

    def custom_day_start(self, project_info, default_start_date):
        try:
            selected_date = default_start_date
            default_start_date = default_start_date.replace(**self.DFLT_DAY_START)
            if not project_info:
                return default_start_date
            hour, minute = self.get_project_day_start(project_info)
            if hour == 0:
                return default_start_date
            elif hour > selected_date.hour >= 0:
                return (default_start_date - timedelta(days=1)).replace(
                    hour=hour, minute=minute, second=0
                )
            # End time spills on next day
            return default_start_date.replace(hour=hour, minute=minute, second=0)

        except Exception as e:
            logging.exception(e)
            raise

    def dflt_month_end(self, project_info, now, month_end):
        try:
            defaults = {"day": month_end, "hour": 23, "minute": 59, "second": 59}
            hour, minute = self.get_project_day_start(project_info)
            if hour == 0 or not project_info:
                return now.replace(**defaults)
            elif hour > now.hour >= 0:
                month_end_date = (now.replace(**defaults) + timedelta(days=1)).replace(
                    hour=hour, minute=minute, second=0
                )
            else:
                # End Month date spills on next Month first date
                next_day = now.replace(**defaults) + timedelta(days=1)
                month_end_date = next_day.replace(hour=hour, minute=minute, second=0)
            return month_end_date - timedelta(seconds=1)

        except Exception as e:
            logging.exception(e)
            raise

    def get_month_start(self, project_info, now):
        try:
            hour, minute = self.get_project_day_start(project_info)
            month_start = now.replace(**self.DFLT_MONTH_START)
            if hour == 0 or not project_info:
                return month_start
            elif hour > now.hour >= 0:
                if now.month == 1 and now.day == 1:
                    return (month_start - timedelta(days=1)).replace(
                        hour=hour, minute=minute, second=0, day=1
                    )
                return month_start.replace(hour=hour, minute=minute, second=0)
            # Start month hour and minute replacement
            return month_start.replace(hour=hour, minute=minute, second=0)

        except Exception as e:
            logging.exception(e)
            raise

    def get_year_end(self, project_info, now):
        try:
            hour, minute = self.get_project_day_start(project_info)
            if hour == 0 or not project_info:
                return now.replace(**self.DFLT_YEAR_END)
            elif hour > now.hour >= 0:
                if now.month == 1 and now.day == 1:
                    return now.replace(hour=hour, minute=minute, second=0) - timedelta(
                        seconds=1
                    )
                year_end_date = (
                    now.replace(**self.DFLT_YEAR_END) + timedelta(days=1)
                ).replace(hour=hour, minute=minute, second=0)
            else:
                # End Year date spills on next Year first date
                next_day = now.replace(**self.DFLT_YEAR_END) + timedelta(days=1)
                year_end_date = next_day.replace(hour=hour, minute=minute, second=0)
            return year_end_date - timedelta(seconds=1)

        except Exception as e:
            logging.exception(e)
            raise

    def get_year_start(self, project_info, now):
        try:
            hour, minute = self.get_project_day_start(project_info)
            year_start = now.replace(**self.DFLT_YEAR_START)
            if hour == 0 or not project_info:
                return year_start
            elif hour > now.hour >= 0:
                if now.month == 1 and now.day == 1:
                    return (now - timedelta(days=1)).replace(
                        day=1, month=1, hour=hour, minute=minute, second=0
                    )
                return (year_start + timedelta(days=1)).replace(
                    hour=hour, minute=minute, second=0, day=1
                )
            # Start month hour and minute replacement
            return year_start.replace(hour=hour, minute=minute, second=0)

        except Exception as e:
            logging.exception(e)
            raise
