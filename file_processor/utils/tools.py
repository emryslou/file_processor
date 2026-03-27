from datetime import datetime


def support_formats():
    return [
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M',
        '%Y/%m/%d %H:%M:%S',
    ]

def valid_time_format(time_value: str) -> datetime:
    time_formats = support_formats()

    valid_errs = []
    cell_0 = None
    for time_format in time_formats:
        try:
            cell_0 = datetime.strptime(str(time_value).strip(), time_format)
        except ValueError as _e:
            valid_errs.append(_e)

    if cell_0 is None:
        err_msg = ', '.join(time_formats)
        raise ValueError('All formats (%s) Are Missing' % (err_msg))
    
    return cell_0
