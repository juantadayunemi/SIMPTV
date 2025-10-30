import holidays as pyholidays
import pandas as pd
import translators as ts

YEAR_RANGE = range(2025, 2027)

def create_holidays_object() -> object:
    """
    Crea el objeto de feriados de Ecuador en un rango de años
    Returns:
          obj: Objeto de feriados nacional
    """

    local_holidays = pyholidays.Ecuador(years=YEAR_RANGE)
    local_holidays = extra_holiday(local_holidays)

    return local_holidays


def extra_holiday(local_holidays) -> object:
    """
    Agrega días considerables que afectan al tráfico en el objeto de feriados.
    Return:
        obj: Objeto con los feriados y días considerados que afectan
        el tráfico nacional.
    """
    # (MM-DD),(Nombre)
    extra_holidays = [("12-30", "Day Before End of Year"), ("12-31", "End of Year")]
    for year in YEAR_RANGE:
        for key, value in extra_holidays:
            local_holidays[pd.to_datetime(str(year) + "-" + key).date()] = value

    return local_holidays


def get_name_holiday(local_holidays, date) -> str:
    """
    Obtiene el nombre del feriado para una fecha dada.
    Args:
        local_holidays (holidays.HolidayBase): Objeto de feriados.
        date (str): Fecha en formato 'YYYY-MM-DD'.
    Returns:
        str: Nombre del feriado o 'No es feriado'.
    """
    name_holiday = local_holidays.get(pd.to_datetime(date).date(), "Día normal")
    translate = ts.translate_text(name_holiday, translator="google", to_language="es")

    print(f"Holiday on {date}: {translate}")

    return translate


def create_dataframe_holiday(
    local_holidays, name="national_holiday", lower_window=0, upper_window=1
) -> pd.DataFrame:
    """
    Crea un DataFrame para feriados compatible con Prophet.
    Args:
    local_holidays : dict
        Diccionario con fechas de los feriados.
    name : str
        Nombre del feriado.
    lower_window : int
        Días antes del feriado incluidos.
    upper_window : int
        Días después del feriado incluidos.

    Returns:
    pd.DataFrame con columnas: holiday, ds, lower_window, upper_window.
    """
    return pd.DataFrame(
        {
            "holiday": name,
            "ds": pd.to_datetime(list(local_holidays.keys())),
            "lower_window": lower_window,
            "upper_window": upper_window,
        }
    )
