import calendar
import logging as logger
import time
from calendar import timegm
from datetime import datetime, timedelta, timezone

import pytz
from num2words import num2words
from scripts.core.constants.defaults import DEFAULT_TIME_FORMAT, TIMEZONE
from scripts.core.constants.time_formats import AppTimeFormats
from scripts.core.schemas.common_model import TimeCalcRequest
from scripts.utils import word_to_time


def get_time_range(
    custom_time,
    time_range=None,
    custom=False,
    optional_time_range=None,
    tz=TIMEZONE,
    future_days=None,
    month_filter=None,
    year_filter=None,
    project_info=None,
):
    try:
        compare = False
        if year_filter:
            from_date = datetime(
                year=year_filter, month=1, day=1, tzinfo=pytz.timezone(tz)
            )
            now = datetime.now()
            to_date = datetime(
                year=year_filter,
                month=12,
                day=calendar.monthrange(now.year, 12)[1],
                hour=23,
                minute=59,
                second=59,
                tzinfo=pytz.timezone(tz),
            )
            return int(from_date.timestamp() * 1000), int(to_date.timestamp() * 1000)
        if month_filter:
            # Option selected: Month and Year
            _, last_day = calendar.monthrange(*list(reversed(month_filter)))
            from_date = datetime(
                year=month_filter[1],
                month=month_filter[0],
                day=1,
                tzinfo=pytz.timezone(tz),
            )
            to_date = datetime(
                year=month_filter[1],
                month=month_filter[0],
                day=last_day,
                hour=23,
                minute=59,
                second=59,
                tzinfo=pytz.timezone(tz),
            )
            return int(from_date.timestamp() * 1000), int(to_date.timestamp() * 1000)
        if time_range in ["previous_period"]:
            time_range = optional_time_range
            compare = True
        if not custom and time_range:
            to_time, from_time = word_to_time.word_to_time(
                time_range,
                tz,
                compare=compare,
                project_info=project_info,
                future_days=future_days,
            )
        else:
            from_time = custom_time.get("from")
            to_time = custom_time.get("to")
            if not all([from_time, to_time]):
                return None, None
            if not isinstance(from_time, int):
                utc_time = time.strptime(from_time, DEFAULT_TIME_FORMAT)
                from_time = timegm(utc_time) * 1000
            if not isinstance(to_time, int):
                utc_time = time.strptime(to_time, DEFAULT_TIME_FORMAT)
                to_time = timegm(utc_time) * 1000

        """
        you might be wondering why there is -1, future developer...
        it's because of regression in latest version of Kairos,
        which considers boundaries as inclusive.
        """
        return from_time, to_time - 1
    except Exception as e:
        logger.exception(f"Exception in getting time range: {e}")
        raise


def get_custom_time(enable_custom, custom_time):
    try:
        if not enable_custom:
            return None, None
        from_time = custom_time.get("from")
        to_time = custom_time.get("to")
        if not isinstance(from_time, int):
            utc_time = time.strptime(from_time, DEFAULT_TIME_FORMAT)
            from_time = timegm(utc_time) * 1000
        if not isinstance(to_time, int):
            utc_time = time.strptime(to_time, DEFAULT_TIME_FORMAT)
            to_time = timegm(utc_time) * 1000
        return from_time, to_time
    except Exception as e:
        logger.exception(f"Exception in getting custom time range: {e}")
        raise


def time_calc_std(req_body: TimeCalcRequest):
    try:
        import datetime

        time_picker = req_body.widget_filter.get("timePickerValue", {})
        time_range = num_to_words_custom(
            time_picker, req_body.widget_filter.get("timeRange", "")
        )
        from_date, to_date = get_time_range(
            custom_time=time_picker.get("custom", None),
            time_range=time_range,
            custom=time_picker.get("isCustom", False),
            tz=req_body.tz,
            project_info={},
        )
        from_timestamp_seconds = from_date / 1000
        to_timestamp_seconds = to_date / 1000
        start_time = datetime.datetime.fromtimestamp(from_timestamp_seconds).strftime(
            AppTimeFormats.USER_META_TIME_FORMAT
        )
        end_time = datetime.datetime.fromtimestamp(to_timestamp_seconds).strftime(
            AppTimeFormats.USER_META_TIME_FORMAT
        )
        return start_time, end_time
    except Exception as e:
        logger.exception(f"Failed to time_calc_std: {e}")
        raise e


def num_to_words_custom(time_picker, filter_time_range):
    try:
        time_range = filter_time_range or time_picker.get("timeRange", None)
        n_value = time_picker.get("n_value", 1)
        if time_range and "_n_" in time_range and n_value:
            n_value = time_picker.get("n_value", 1)
        to_words = num2words(n_value)
        time_range = time_range.replace("_n_", f"_{to_words}_")
        return time_range
    except Exception:
        pass

def parse_custom_filter_timestamp(req_body, time_zone):
    try:
        time_duration = req_body.get("duration", "")
        if time_duration in ["year", "month", "week", "day"]:
            start_time_string = req_body.get("label").get("start")
            end_time_string = req_body.get("label").get("end")
            formatted_start_time = format_timestamp_to_timezone(
                start_time_string, time_zone
            )
            formatted_end_time = format_timestamp_to_timezone(end_time_string, time_zone)
            return formatted_start_time, formatted_end_time, time_duration
        return None, None, time_duration
    except Exception as e:
        logger.exception(f"Exception in parse_custom_filter_timestamp: {e}")
        raise e


def format_timestamp_to_timezone(time_string, time_zone):
    # Converted to Europe/London Time zone
    try:
        # Parse the string into a datetime object in UTC
        utc_time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_time = pytz.utc.localize(utc_time)

        given_zone_time = utc_time.astimezone(pytz.timezone(time_zone))

        return given_zone_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.exception(f"Exception in format_timestamp_to_timezone: {e}")
        raise e


def increment_timestring_by_1day(timestamp):
    try:
        datetime_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        # get end time of the same day
        next_day = datetime_obj.replace(hour=23, minute=59, second=59, microsecond=999000)
        # Format it back to the same format
        return next_day.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"
    except Exception as e:
        logger.exception(f"Exception in increment_timestring_by_1day: {e}")
        raise e


