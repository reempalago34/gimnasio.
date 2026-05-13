from datetime import datetime, timedelta, timezone

def get_colombia_time():
    # Colombia is UTC-5
    offset = timezone(timedelta(hours=-5))
    # Return naive datetime representing Colombia time
    return datetime.now(offset).replace(tzinfo=None)

def get_colombia_date():
    return get_colombia_time().date()
