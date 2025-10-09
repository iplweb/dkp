from django import template

register = template.Library()


@register.filter
def duration_format(minutes):
    """
    Format duration in minutes to human-readable format.

    Args:
        minutes: Duration in minutes

    Returns:
        Formatted string like "2h 30m" or "45m"
    """
    if minutes is None:
        return "N/A"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours > 0:
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        else:
            return f"{hours}h"
    else:
        return f"{remaining_minutes}m"


@register.filter
def status_class(incomplete):
    """
    Return CSS class based on completion status.

    Args:
        incomplete: Boolean indicating if entry is incomplete

    Returns:
        CSS class name
    """
    if incomplete:
        return "incomplete-entry"
    else:
        return "complete-entry"


@register.filter
def status_badge(incomplete):
    """
    Return status badge HTML based on completion status.

    Args:
        incomplete: Boolean indicating if entry is incomplete

    Returns:
        HTML badge string
    """
    if incomplete:
        return '<span class="badge badge-danger">Incomplete</span>'
    else:
        return '<span class="badge badge-success">Complete</span>'
