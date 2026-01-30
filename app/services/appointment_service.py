from datetime import datetime, timedelta


def _fmt(dt: datetime) -> str:
    return dt.strftime("%B %d, %Y at %H:%M")


def lookup_appointment(query: str):
    # Dummy: next appointment is 7 days from now at 15:00
    now = datetime.now()
    next_dt = (now + timedelta(days=7)).replace(hour=15, minute=0, second=0, microsecond=0)
    return f"Your next appointment is on {_fmt(next_dt)} with Dr. Müller."


def schedule_appointment(query: str):
    # Dummy scheduling: schedule 14 days from now at 10:00
    now = datetime.now()
    sched_dt = (now + timedelta(days=14)).replace(hour=10, minute=0, second=0, microsecond=0)
    return f"Sure - I've scheduled you for {_fmt(sched_dt)} in Cardiology."
