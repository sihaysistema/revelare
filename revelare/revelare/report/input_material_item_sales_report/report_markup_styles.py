# Styles
quantity_style_estimate_1 = """
  color: white;
  background-color: darkorange;
  display: block;
  text-align: right;
  vertical-align: middle;
  height: 100%;
  width: 100%;
"""

quantity_style_plenty_1 = """
  color: black;
  background-color: orange;
  float: right;
  text-align: right;
  vertical-align: middle;
  height: 100%;
  width: 100%;
"""

quantity_style_few_1 = """
  color: black;
  background-color: blue;
  float: right;
  text-align: right;
  vertical-align: text-top;
"""

quantity_style_sold_1 = """
  color: black;
  background-color: #60A917;
  float: right;
  text-align: right;
  vertical-align: middle;
  height: 100%;
  width: 100%;
"""

quantity_style_sold_dk_1 = """
  color: white;
  background-color: darkgreen;
  display: block;
  text-align: center;
  vertical-align: middle;
  height: 100%;
  width: 100%;
"""

label_style_item_gray = """
  color: #333;
  display: block;
  text-align: center;
  vertical-align: middle;
  height: 100%;
  width: 100%;
"""

# Tag arrays
strong = {"markup": "strong", "style": ""}
strong_gray = {"markup": "strong", "style": "color: #686868"}

qty_plenty1_strong = [
    {"markup": "span", "style": quantity_style_plenty_1}, strong]

qty_estimate1_strong = [
    {"markup": "span", "style": quantity_style_estimate_1}, strong]

qty_sold1_strong = [
    {"markup": "span", "style": quantity_style_sold_1}, strong]

qty_sold1_dk_strong = [
    {"markup": "span", "style": quantity_style_sold_dk_1}, strong]

label_style_item_gray1 = [
    {"markup": "span", "style": label_style_item_gray}, strong]

item_link_open = "<a href='#Form/Item"
item_link_style = "style='color: #1862AA;'"
item_link_open_end = " target='_blank'>"
item_link_close = "</a>"
