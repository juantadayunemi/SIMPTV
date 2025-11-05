import json
import pandas as pd
import numpy as np
from apps.predictions_app.utils.calculations import (
    add_to_date,
    calculate_previous_growth_decrease,
)
import datetime
from prophet import Prophet


def get_forecast(
    df, periods: int, holidays: pd.DataFrame, freq: str = "10T"
) -> pd.DataFrame:
    """
    Genera un DataFrame de predicciones utilizando el modelo Prophet.
    Args:
        df : pd.DataFrame
            DataFrame que contiene los datos históricos con columnas 'ds' (fechas) y 'y' (valores).
        periods : int
            Número de períodos futuros para los cuales se desea generar predicciones.
        holidays : pd.DataFrame
            DataFrame que contiene las fechas de días festivos para incluir en el modelo.
        freq : str, optional
            Frecuencia de los datos (por defecto es "10T" para intervalos de 10 minutos).
    Returns:
        pd.DataFrame
        DataFrame que contiene las predicciones generadas por Prophet.
    """
    model = Prophet(holidays=holidays)
    model.fit(df)
    future = model.make_future_dataframe(periods=periods, freq=freq)

    return model.predict(future)


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
    print("target datetime: ", target_datetime)

    # nearest_row = forecast.loc[forecast["ds"] == target_datetime]
    # if nearest_row.empty:
    #     return None
    forecast["diff"] = (forecast["ds"] - target_datetime).abs()
    nearest_row = forecast.loc[forecast["diff"].idxmin()]

    return nearest_row


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
    if row is None:
        return None

    for key, value in columns:
        previous_value = row[key]
        resp[key + "_change"] = calculate_previous_growth_decrease(
            value, previous_value
        )

    return resp


def traffic_level_classification(df_hist, yhat_count, yhat_speed) -> str:
    df_hist["avgSpeed"] = df_hist["avgSpeed"].astype(float)
    df_hist["totalVehicleCount"] = df_hist["totalVehicleCount"].astype(float)

    # Percentiles de velocidad (entre 0 y 100)
    percentiles_speed = np.percentile(df_hist["avgSpeed"], range(0, 101))

    # Percentiles de conteo vehicular (entre 0 y 100)
    percentiles_count = np.percentile(df_hist["totalVehicleCount"], range(0, 101))

    P_speed = np.searchsorted(percentiles_speed, yhat_speed) / 100  # valor entre 0 y 1
    P_count = np.searchsorted(percentiles_count, yhat_count) / 100  # valor entre 0 y 1

    # Indice de congestion (0–2)
    # Más velocidad: menor congestión (1 - P_speed)
    # Más cantidad: mayor congestión (+ P_count)
    IC = (1 - P_speed) + P_count

    if IC < 0.9:
        level = "Fluido"
    elif 0.9 <= IC < 1.6:
        level = "Denso"
    else:
        level = "Embotellamiento"

    return level, IC
