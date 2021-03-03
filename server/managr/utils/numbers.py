from decimal import (
    Decimal,
    ROUND_DOWN,
)
import random
import re


def generate_random_numbers(length=10):
    value = ""
    for i in range(10):
        value += str(random.randint(1, 9))
    return value


def round_decimal(value, quantize=".01"):
    """"""
    if value is not None:
        return Decimal(value).quantize(Decimal(quantize), rounding=ROUND_DOWN)


def format_phone_number(value, format="+1%d%d%d%d%d%d%d%d%d%d"):
    """ 
        format phone number (numbers only) 
        value = 10 or 11 digit phone number 
        format = the format you want to conver to 
            ether string literals of the characters you want or %d for digits %w for whitespace 
        example +1(%d%d%d)%w%d%d%d-%d%d%d%d"
    """

    # final string should have this length - the special % sign
    regex_format_chars = r"(\%[d|w])"
    matches = re.findall(regex_format_chars, format)
    matches_length = len(matches)
    # final string should have this length - the special % sign
    format_length = len(format) - matches_length

    # get the integers and push them into an array
    value_array = [None] * 11
    cnt = 0
    for char in value:
        try:
            if type(int(char)) is int:
                value_array[cnt] = char
                cnt += 1
        except ValueError:
            pass

    if value_array[10]:
        value_array.pop(0)

    # take each char in the format and put it into an array
    empty_str = ""
    cnt = 0
    value_cnt = 0
    _format = format
    while len(empty_str) <= format_length:

        if len(empty_str) >= format_length:
            break
        _format = format[cnt:]
        test = re.search(regex_format_chars, _format)
        if test:
            if cnt == cnt + test.start():
                if format[cnt + test.start() : cnt + test.end()] == "%w":
                    empty_str += " "
                elif format[cnt + test.start() : cnt + test.end()] == "%d":
                    empty_str += value_array[value_cnt]
                    value_cnt += 1
                cnt = cnt + test.end()
            else:
                empty_str += format[cnt]
                cnt += 1
        else:
            empty_str += format[cnt]
            cnt += 1
    return empty_str


# print(format_phone_number('+18572056014',
#                          format="+1(%d%d%d)%w%d%d%d-%d%d%d%d"))


def validate_phone_number(value, country="US"):
    """ 
        validates phone number depending on country (default is us) 
        Currently only supports US, will accept formats 
        ########################
        0000000000, +10000000000,
        +1(000) 000-0000, (000) 000-0000,
        000-000-0000
    """
    value_length = len(value)
    if value_length < 10:
        # currently only supporting US which requires a minimum of 10 numbers including area code
        raise ValueError(f"{value} must be at least 10 characters")
    # phone numbers can contain (), -, + collect them
    regex_format_chars = r"([\+\(\)\-\s])"
    matches = re.findall(regex_format_chars, value)
    matches_length = len(matches)
    if (value_length - matches_length) < 10 or value_length - matches_length > 11:
        # make sure at least 10 chars are included and no more than 11 (including the 1)
        raise ValueError(f"{value} must be at least 10 numeric characters and no more than 11")
    return True


# validate_phone_number('+1(857)205-6014')
