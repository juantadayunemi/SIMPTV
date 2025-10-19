import json
import pandas as pd
from apps.predictions_app.utils.calculations import (
    add_to_date,
    calculate_previous_growth_decrease,
)
import datetime


def get_forecast_by_date(forecast, target_datetime: datetime) -> pd.DataFrame:
    """
    Devuelve la fila del DataFrame de predicciones correspondiente a la fecha especificada.
    Args:
    forecast : pd.DataFrame
        DataFrame que contiene las predicciones generadas por Prophet,
        con al menos la columna 'ds' (fechas) y 'yhat' (predicción).
    target_datetime : datetime
        Fecha específica para la que se desea obtener la predicción.

    Return:
    pd.Series
        Fila del DataFrame que coincide con la fecha indicada, incluyendo
        columnas como 'yhat', 'yhat_lower', 'yhat_upper', y componentes adicionales
        si existen (trend, seasonality, holidays, etc.).

    """
    filtered = forecast.loc[forecast["ds"] == target_datetime]
    if not filtered.empty:
        return filtered.iloc[0]
    return None


def get_total_seasonality(row, columns_name=("weekly", "yearly", "daily")) -> float:
    """
    Devuelve el total de la estacionalidad

    Args:
        row: Fila del DataFrame que coincide con la fecha indicada, incluyendo
        columnas como 'yhat', 'yhat_lower', 'yhat_upper'

        columns_name: Tupla con nombres de las columnas que se van a extraer su
        valor

    Return:
        float: valor total de la estacionalidad
    """
    seasonality_total = 0
    for column in columns_name:
        if column in row:
            seasonality_total += row[column]

    return seasonality_total


def get_previous_forecast(forecast, previous_date, yhat, trend) -> json:
    """
    Calcula la variación de las métricas de pronóstico ('yhat' y 'trend')
    con respecto a una fecha anterior.

    Args:
        forecast: DataFrame con los datos de pronóstico.
        previous_date: Fecha anterior usada para comparar.
        yhat: Valor actual de la predicción.
        trend: Valor actual de la tendencia.

    Returns:
        dict: Diccionario con las variaciones calculadas para 'yhat' y 'trend'.
    """

    resp = {}
    columns = [("yhat", yhat), ("trend", trend)]
    row = get_forecast_by_date(forecast, previous_date)

    for key, value in columns:
        previous_value = row[key]
        print(f"Previous values '{key}': {previous_value}")
        resp[key] = calculate_previous_growth_decrease(value, previous_value)
        print(f">>>>>>{key} = {resp[key]}")

    return resp


def traffic_level_classification(column, value) -> str:
    """
    Clasifica el nivel de tráfico en 'low', 'medium' o 'high' basado en los cuantiles 33 y 66.
    Args:
        column (pd.Series): Serie de pandas con los conteos de vehículos.
        value (int): Valor de conteo de vehículos a clasificar.
    Returns:
        str: Nivel de tráfico ('low', 'medium', 'high').
    """

    low = column.quantile(0.33)
    high = column.quantile(0.66)
    print(f"Quantiles: low={low}, high={high}, value={value}")

    if value <= low:
        return "Bajo"

    if value < high:
        return "Medio"

    return "Alto"
