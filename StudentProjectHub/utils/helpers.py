from datetime import datetime


def format_date(value, fmt="%d %b %Y"):
    if not value:
        return "-"
    return value.strftime(fmt)


def format_datetime(value, fmt="%d %b %Y, %I:%M %p"):
    if not value:
        return "-"
    return value.strftime(fmt)


def currency(amount):
    try:
        return f"₹{int(amount):,}"
    except (TypeError, ValueError):
        return "₹0"


def register_template_filters(app):
    app.jinja_env.filters["date"] = format_date
    app.jinja_env.filters["datetime"] = format_datetime
    app.jinja_env.filters["currency"] = currency
    app.jinja_env.globals["now"] = datetime.utcnow
