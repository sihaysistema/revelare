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


@frappe.whitelist()
def get_periods(start_date: str, end_date: str, freq: str):
    """Get periods between two dates"""
    periods = (pd.date_range(pd.to_datetime(start_date),
                             pd.to_datetime(end_date), freq=freq)
               .strftime(DATE_FORMAT)
               .tolist())
    return periods


@frappe.whitelist()
def get_date_ranges(start_date: str, end_date: str, freq: str):
    """Get date range tuples for a period"""
    # if start_date > end_date:
    #     return []
    dates = get_periods(start_date, end_date, freq)

    if dates:
        # Iterate through the dates and compile the column header
        date_ranges = [(start_date, dates[0])]
        next_start = get_next_day(dates[0])
        for date in dates[1:]:
            date_ranges.append((next_start, date))
            next_start = get_next_day(date)

        # Account for partial end range
        last_date = date_ranges[-1][1]
        if pd.to_datetime(end_date) > pd.to_datetime(last_date):
            next_start = get_next_day(last_date)
            date_ranges.append((next_start, end_date))
    else:
        date_ranges = [(start_date, end_date)]
    return date_ranges


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
    return int(date)


def get_quarter_number(date: str) -> int:
    """Get the quarter number for a date"""
    quarter = ((pd.to_datetime(date).month - 1) // 3) + 1
    return quarter


def get_month_number(date: str) -> int:
    """Get the month number for a date"""
    month = pd.to_datetime(date).strftime("%m")
    return int(month)


def get_year_number(date: str) -> int:
    """Get the year number for a date"""
    year = pd.to_datetime(date).strftime("%Y")
    return int(year)


def to_date(date_str):
    """Returns a datetime object for the date string"""
    return pd.to_datetime(date_str).strftime(DATE_FORMAT)


def group_data(dates, data, date_props):
    """Group data into date bins and return a dictionary of grouped data
       Args:
          dates: A list of date iterables in form (start, end)
          data: An array of dictionary objects to be filtered on their date
                property
          date_prop: The date property keys on the object in form (start, end)
    """
    (prop_start, prop_end) = date_props
    buckets = {}

    # Place objects in buckets based on their dates
    for date in dates:
        matches = []
        for obj in data:
            (start, end) = date
            start_date = obj[prop_start]
            end_date = obj[prop_end]
            if to_date(start_date) >= start and to_date(end_date) <= end:
                matches.append(obj)
        buckets[date] = matches
    return buckets


def convert_uom(total_sold, stock_qty, conversion_factor):
    """Convert quantities from original uom to target uom"""
    # Convert the items sold an amt in the target UOM
    target_quantity = float((total_sold * stock_qty) / conversion_factor)
    return target_quantity


def filter_dictionaries_first(list_of_dicts, configuration):
    """Return the first dictionary in list_of_dicts w/ matching key,value pair"""
    for dictionary in list_of_dicts:
        for key, val in configuration.items():
            if dictionary.get(key, {}) == val:
                return dictionary
    return {}


def filter_dictionaries(list_of_dicts, configuration):
    """Return all dictionaries in list_of_dicts w/ matching key,value pair"""
    dictionaries = []
    for dictionary in list_of_dicts:
        for key, val in configuration.items():
            if dictionary.get(key, {}) == val:
                dictionaries.append(dictionary)
    return dictionaries


def shorten_column(column, border_str, nchars):
    """Remove unwanted column text and shorten to n chars"""
    if column.find(border_str) != -1:
        column = column[:column.find(border_str)]

        # Shorten "Actual", "Estimated", and "Remaining"
        actual_pos = column.find('Actual')
        estimated_pos = column.find('Estimated')
        remaining_pos = column.find('Remaining')

        if actual_pos != -1:
            column = column[:actual_pos] + "Act."
        elif estimated_pos != -1:
            column = column[:estimated_pos] + "Est."
        elif remaining_pos != -1:
            column = column[:remaining_pos] + "Rem."

        # Shorten to the specified character limit
        if len(column) > nchars:
            column = column[:nchars]
    return column


def reverse_dictionary(dictionary):
    """Reverse  the key,val relationship in the dict"""
    if dictionary:
        return {val: key for key, val in dictionary.items()}
