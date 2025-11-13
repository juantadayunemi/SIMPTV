import joblib
import pandas as pd
import datetime
from prophet import Prophet


def train_prophet_models(holidays: pd.DataFrame, df: pd.DataFrame) -> Prophet:
    model = Prophet(holidays=holidays)
    model.fit(df)
    return model

def get_forecast(
    model: Prophet, periods: int, freq: str = "10T"
) -> pd.DataFrame:
    """
    Genera un DataFrame de predicciones utilizando el modelo Prophet.
    Args:
        model : Prophet
            Modelo Prophet entrenado para realizar predicciones.
        periods : int
            Número de períodos futuros para los cuales se desea generar predicciones.
        freq : str, optional
            Frecuencia de los datos (por defecto es "10T" para intervalos de 10 minutos).
    Returns:
        pd.DataFrame
        DataFrame que contiene las predicciones generadas por Prophet.
    """
    
    future = model.make_future_dataframe(periods=periods, freq=freq)
    
    return model.predict(future)





def get_forecast_by_date(forecast, target_datetime: datetime.datetime) -> pd.DataFrame:
    """
    Devuelve la fila del DataFrame de predicciones correspondiente a la fecha especificada.
    Args:
    forecast : pd.DataFrame
        DataFrame que contiene las predicciones generadas por Prophet,
        con al menos la columna 'ds' (fechas) y 'yhat' (predicción).
    target_datetime : datetime.datetime
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



