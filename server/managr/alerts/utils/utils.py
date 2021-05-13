import operator
import re
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


# group_1 = [[[True, "OR"], [False, "AND"], [True, "OR"]], "OR"]
# group_2 = [[[True, "AND"], [False, "AND"], [True, "AND"]], "AND"]
# group_3 = [[[True, "AND"], [False, "AND"], [True, "OR"]], "OR"]

group_3 = [[True, "AND"], [False, "AND"], [True, "OR"]]
group_2 = [[True, "AND"], [False, "AND"], [True, "AND"]]
group_1 = [[True, "OR"], [False, "AND"], [True, "AND"]]

## true false recurrsion
def test_fn(group, current_index, current_eval):
    group_length = len(group)
    current_conditional = f"__{group[current_index][1].lower()}__"
    if current_index == 0 and current_index == group_length - 1:
        return group[current_index][0]
    elif current_index == 0:
        # conditional does not matter for first item
        current_eval = group[0][0]
        return test_fn(group, current_index + 1, current_eval)
    else:
        __conditional = getattr(operator, current_conditional)
        current_eval = __conditional(current_eval, group[current_index][0])
        if current_index + 1 < group_length:
            return test_fn(group, current_index + 1, current_eval)
        return current_eval


# variable substition
def convertToSlackFormat(body):
    """
        converts em tags to _
        converts strong tags to *
        converst s tags to ~
        strips orphaned tags and cleans out other html
    """
    new_str = body
    new_str = re.sub(r"<s>\s?(?=[A-Za-z0-9])", "~", new_str)
    new_str = re.sub(r"(?<=[A-Za-z0-9])(\s*</s>)", "~", new_str)
    new_str = re.sub(r"<em>\s?(?=[A-Za-z0-9])", "_", new_str)
    new_str = re.sub(r"(?<=[A-Za-z0-9])(\s*</em>)", "_", new_str)
    new_str = re.sub(r"<strong>\s?(?=[A-Za-z0-9])", "*", new_str)
    new_str = re.sub(r"(?<=[A-Za-z0-9])(\s*</strong>)", "*", new_str)
    new_str = strip_tags(new_str)
    return new_str
