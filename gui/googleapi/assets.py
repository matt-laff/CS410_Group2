import re
import datetime
import humanize

def get_name(email):
    """
    extract the name from a email address parameter. The input
    has the form: Brett Hopt <hopt@pdx.edu>, but at the end the
    output should be Brett Hopt.

    :param str email: The email to extract the name from

    :return: str
    """
    pattern = r'([^<]+) <[^>]+>'

    match = re.search(pattern, email)

    if match:
        return match.group(1).strip()
    else:
        return None

def name_split(ch):
    """
    Return the first half of a name before the space

    :param str ch: The input name to split
    :return: str
    """
    space_index = ch.find(' ')
    if space_index != -1:
        return ch[:space_index]
    else:
        return None

def tm_fm(utc_timestamp):
    """
    Returns the time ago reading for the utc timestamp

    :param int utc_timestamp: The utc timestamp for a returned gmail message

    :return: The time ago equivalent for that timestamp
    """
    internal_date_seconds = int(utc_timestamp) / 1000

    dt_object = datetime.datetime.utcfromtimestamp(internal_date_seconds)
    time_difference = datetime.datetime.utcnow() - dt_object
    tm = humanize.naturaltime(time_difference)

    return tm

def get_month(utc_timestamp):
    internal_date_seconds = int(utc_timestamp) / 1000
    dt_object = datetime.datetime.utcfromtimestamp(internal_date_seconds)
    month = dt_object.strftime("%B")

    return month

if __name__ == "__main__":
    month = get_month(utc_timestamp=1647340800000)
    print(f"month: {month}")

