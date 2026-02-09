from flask import current_app


def get_parking_info():
    # Replace with live data integration
    currency = current_app.config.get("CURRENCY", "USD")
    return (
        "Visitor parking is available at North Wing Parking Lot A (free 2h),"
        f" or South Garage on Elm St ({currency} 2/hour after first 2h)."
    )
