from dateutil.relativedelta import relativedelta
import pandas as pd
from datetime import datetime, date


def get_percentage(value, value_total=1) -> float:
    """
    Devuelve el porcentaje

    Returns:
        float: porcentaje

    """
    try:
        return (value / value_total) * 100
    except ZeroDivisionError:
        return 0


def calculate_previous_growth_decrease(selected_value, previous_value) -> float:
    """
    Devuelve el porcentaje de aumento o disminución del tráfico en la predicción o en la tendencia
    con respecto al periodo (año, mes, dia) anterior al seleccionado.

    Un valor positivo indica un incremento y un valor negativo indica
    un decremento.
    """

    try:
        return ((selected_value - previous_value) / previous_value) * 100
    except ZeroDivisionError:
        return 0


def add_to_date(date, days=0, months=0, years=0) -> date:
    """
    Suma o resta un período de tiempo (días, meses o años) a una fecha dada.

    Args:
        date:
        La fecha base a la que se le sumará o restará tiempo. days : int, opcional
        Número de días a sumar (puede ser negativo para restar). Por defecto 0.
        months : int, opcional
        Número de meses a sumar (puede ser negativo para restar). Por defecto 0.
        years : int, opcional
        Número de años a sumar (puede ser negativo para restar). Por defecto 0.

    Returns:
        datetime.date: La fecha resultante.
    """
    period_change = relativedelta(years=years, months=months, days=days)

    print("fecha add: ", pd.to_datetime(date).date() + period_change)
    return pd.to_datetime(date).date() + period_change


def convert_datetime(date, hour, minute, second=0) -> datetime:
    """
    Convierte valores separados de fecha y hora en un objeto datetime.

    Args:
        date (str): Fecha en formato 'YYYY-MM-DD'.
        hour (int): Hora del día (0-23).
        minute (int): Minuto (0-59).
        second (int, opcional): Segundo (0-59). Por defecto es 0.

    Returns:
        datetime: Objeto datetime resultante de combinar los valores proporcionados.
    """

    return datetime.strptime(f"{date} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")


def previous_periods(date, period_type: str) -> date:
    """
    Obtiene la fecha correspondiente al periodo anterior basado en el tipo de periodo especificado.

    Args:
        date (date): Fecha base.
        period_type (str): Tipo de periodo ('yearly', 'monthly', 'daily').

    Returns:
        date: Fecha del periodo anterior.
    """
    periods = {
        "yearly": {"years": -1},
        "monthly": {"months": -1},
        "daily": {"days": -1},
    }
    if period_type in periods:
        return add_to_date(date, **periods[period_type])
    else:
        raise ValueError(
            "Tipo de periodo no válido. Use 'yearly', 'monthly' o 'daily'."
        )
