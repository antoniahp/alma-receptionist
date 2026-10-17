from datetime import timedelta


def calculate_due_date(last_visit_date, repeat_every_days):
    return last_visit_date + timedelta(days=repeat_every_days)


def is_reactivation_due(due_date, today, days_ahead):
    """Le toca repetir si la fecha recomendada ya llegó o llega en los próximos 'days_ahead' días."""
    return (due_date - today).days <= days_ahead
