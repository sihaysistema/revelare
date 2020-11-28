def html_wrap(txt: str, tags: list, style: str = "") -> str:
    """
    Wrap text in an html tag and return as a string
      Args:
        txt*: The text to wrap in html
        tags*: The html tags without brackets, outward in order
        style: Any inline styles to include 
    """
    # Remove any newlines to allow it to render equally in all browsers
    replacements = {"\n": "", "\t": "", "  ": ""}
    if style:
        for old, new in replacements.items():
            style = style.replace(old, new)

    # Wrap the tags in order, from inside out, then apply styles to outmost tag
    wrapped = txt
    while tags:
        tag = tags.pop()
        if len(tags):
            wrapped = f"<{tag}>{wrapped}</{tag}>"
        else:
            wrapped = f"<{tag} style='{style}'>{wrapped}</{tag}>"

    return wrapped
