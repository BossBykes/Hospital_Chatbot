def lookup_appointment(query: str):
    # Dummy lookup: in production, parse patient ID from query & query EHR
    return "Your next appointment is on July 30, 2025 at 3:00 PM with Dr. Müller."


def schedule_appointment(query: str):
    # Dummy scheduling: parse date/department & call EHR API
    return "Sure—I've scheduled you for August 5, 2025 at 10:00 AM in Cardiology."