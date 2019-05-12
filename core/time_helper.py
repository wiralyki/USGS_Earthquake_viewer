import calendar
import datetime


def get_month_start_end_date(year, month):
    first_month_day = datetime.date(year, month, 1)
    last_month_day = first_month_day.replace(
        day=calendar.monthrange(first_month_day.year, first_month_day.month)[1]
    )
    return first_month_day, last_month_day


def get_month_start_end_date_from_period(start_year, end_year):

    dates_list = []
    current_year = start_year

    while current_year < end_year:
        dates_list.extend([
            get_month_start_end_date(current_year, month_nb)
            for month_nb in range(1, 13)
            if datetime.datetime(current_year, month_nb, 1) <= datetime.datetime.now()
        ])
        current_year += 1

    return dates_list
