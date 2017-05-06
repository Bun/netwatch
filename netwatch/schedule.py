from datetime import datetime
from datetime import timedelta


def schedule_from_datetime(dt, h, m):
    return dt.replace(hour=h, minute=m, second=0, microsecond=0)


def schedule_blob(blob, now=None):
    """Compute next time event should occur, disregarding seconds and
    microseconds."""
    if now is None:
        now = datetime.now()

    if 'minutes' in blob:
        delta = timedelta(minutes=blob['minutes'])
        return now.replace(second=0, microsecond=0) + delta

    if 'hours' in blob:
        delta = timedelta(hours=blob['hours'])
        minute = blob.get('at', 0)
        # This might leak into the next day
        return now.replace(minute=minute, second=0, microsecond=0) + delta

    if 'days' in blob:
        days = max(blob['days'], 1)
        hour = blob.get('at', 0)
        return schedule_from_datetime(now, hour, 0) + timedelta(days=days)

    return schedule_next(blob['schedule'], now)


def schedule_next(hours, now):
    for h, m in hours:
        if now.hour <= h and (now.hour != h or now.minute < m):
            return schedule_from_datetime(now, h, m)

    # Schedule next thing tomorrow
    return schedule_from_datetime(now, *hours[0]) + timedelta(days=1)


if __name__ == '__main__':
    hours = [(0, 0),
             (17, 30),
             (19, 5),
             (21, 0),
             (22, 0),
             (23, 0)]

    now = datetime.now()
    now = now.replace(hour=3, minute=00)
    print(now)
    print(schedule_next(hours, now))

    print(schedule_blob({'hours': 2}))
