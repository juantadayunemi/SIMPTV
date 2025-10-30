# Dependencias para Predictions App

Listado mínimo de paquetes necesarios para el módulo de predicciones:

- Python (>=3.8)
- Django
- djangorestframework
- pandas
- numpy
- prophet (pip package: `prophet`)
- requests
- urllib3
- translators (si usas traducción automática en utilidades)
- drf-spectacular (opcional, para documentación OpenAPI)
- otras dependencias internas: `apps.predictions_app` (módulos utils, models)

Instalación recomendada (entorno virtual activado):

```bash
pip install django djangorestframework pandas numpy prophet requests urllib3 translators drf-spectacular
```

Verificación rápida:

```bash
python -c "import pandas, numpy, prophet, requests, urllib3; print('ok')"
```

🔧 Solución recomendada si falla la dependencia `translators` (o hay conflicto entre `requests` / `urllib3`)

Si la importación falla por errores relacionados con `requests` o `urllib3`, forzar la reinstalación de `requests` y luego `urllib3` suele resolverlo:

```bash
pip install --force-reinstall requests
pip install --force-reinstall urllib3
```

Notas:
- Usar un entorno virtual (venv) evita conflictos con paquetes del sistema.
- Si `translators` sigue fallando, revisar su documentación y probar a reinstalarla:
  ```bash
  pip install --force-reinstall translators
  ```
- Si continúa el problema, pegar el traceback completo para diagnóstico.