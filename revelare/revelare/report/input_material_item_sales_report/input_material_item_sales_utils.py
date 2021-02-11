import frappe
from frappe.utils import getdate, get_user_format
from datetime import date, timedelta
import pandas as pd

DATE_FORMAT = "%Y-%m-%d"


def html_wrap(txt: str, tags: list) -> str:
    """
    Wrap text in one or more html tags and return as a string
      Args:
        txt*: The text to wrap in html
        tags*: The html tags without brackets, outward in order

      Tags should have a shape like the following example:
        {
          markup: 'p',
          style: 'color: white;'
        }
    """
    # Remove any unwantted chars to allow css to render equally in all browsers
    replacements = {"\n": "", "\t": "", "  ": ""}

    # Wrap the tags in order, from inside out, applying styles to each tag
    wrapped = txt
    tags_to_wrap = tags.copy()
    while tags_to_wrap:
        # Grab the tag
        tag = tags_to_wrap.pop()
        # Sanitize any script tags
        if "script" in tag.keys():
            continue
        markup = tag["markup"]
        style = format_style(tag["style"], replacements)

        # Wrap each level of the html in the tag
        if len(style):
            wrapped = f"<{markup} style='{style}'>{wrapped}</{markup}>"
        else:
            wrapped = f"<{markup}>{wrapped}</{markup}>"

    return wrapped


def format_style(style: str, replacements: list) -> str:
    """
    Remove unwanted characters from the style, such as newlines, tabs and spaces
    """
    formatted_style = style
    if formatted_style:
        for old, new in replacements.items():
            formatted_style = formatted_style.replace(old, new)

    return formatted_style


def weeks_in_year(year):
    """Find the total number of weeks in a year"""
    final_week = date(year, 12, 28)
    total_weeks = final_week.isocalendar()[1]
    return total_weeks


def days_between(start_date: str, end_date: str) -> int:
    """Find the number of days between two dates"""
    start = getdate(start_date)
    end = getdate(end_date)
    days = abs(start - end).days
    return days


def weeks_between(start_date: str, end_date: str) -> int:
    """Find the number of weeks between two dates"""
    DAYS_PER_WEEK = 7
    days = days_between(start_date, end_date)
    return days // DAYS_PER_WEEK


def quarter_dates(start_date: str, end_date: str):
    """Returns an array of quarter start dates"""
    user_date_format = get_user_format()
    quarter_dates = (pd.date_range(pd.to_datetime(start_date),
                                   pd.to_datetime(end_date) + pd.offsets.QuarterBegin(1), freq='Q')
                     .strftime(user_date_format)
                     .tolist())
    return quarter_dates


def get_periods(start_date: str, end_date: str, freq: str):
    """Get periods between two dates"""
    periods = (pd.date_range(pd.to_datetime(start_date),
                             pd.to_datetime(end_date), freq=freq)
               .strftime(DATE_FORMAT)
               .tolist())
    return periods


def get_next_day(start_date: str) -> str:
    """Take a date string and return the date string for one day forward"""
    date = ((pd.to_datetime(start_date) + pd.to_timedelta(1, unit='d'))
            .strftime(DATE_FORMAT))
    return date


def get_prior_day(start_date: str) -> str:
    """Take a date string and return the date string for one day prior"""
    date = ((pd.to_datetime(start_date) + pd.to_timedelta(-1, unit='d'))
            .strftime(DATE_FORMAT))
    return date


def get_week_number(date: str) -> int:
    """Get the ISO week number of a date"""
    date = pd.to_datetime(date).strftime("%V")
    return date