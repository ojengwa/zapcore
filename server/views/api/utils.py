import arrow


def humanize_date(value):
    return arrow.get(value).humanize()
