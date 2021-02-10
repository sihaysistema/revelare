from datetime import date, timedelta


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
