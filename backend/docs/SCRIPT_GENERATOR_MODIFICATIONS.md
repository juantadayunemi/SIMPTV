# 🔧 MODIFICACIONES AL SCRIPT GENERADOR

## Archivo: `backend/apps/entities/management/commands/generate_entities.py`

### MODIFICACIÓN 1: Agregar parser de anotaciones

Insertar después de la línea 364 (`def _parse_interface_properties`):

```python
def _extract_annotations_from_comment(self, comment: str) -> Dict[str, Any]:
    """
    Extrae anotaciones @db: desde comentarios TypeScript
    
    Anotaciones soportadas:
    - @db:primary - Campo primary key
    - @db:identity - IDENTITY(1,1) autoincremental  
    - @db:foreignKey ModelName - Foreign Key
    - @db:varchar(n) - VARCHAR(n)
    - @db:int - INT
    - @db:bigint - BIGINT
    - @db:float - FLOAT
    - @db:decimal(p,s) - DECIMAL
    - @db:text - TEXT/NVARCHAR(MAX)
    - @db:datetime - DATETIME2
    - @default(value) - Valor por defecto
    
    Returns:
        Dict con: {
            'is_primary': bool,
            'is_identity': bool,
            'foreign_key': str | None,
            'db_type': str | None,
            'default_value': str | None
        }
    """
    import re
    
    annotations = {
        'is_primary': False,
        'is_identity': False,
        'foreign_key': None,
        'db_type': None,
        'default_value': None,
        'max_length': None,
        'decimal_precision': None,
        'decimal_scale': None,
    }
    
    if not comment:
        return annotations
    
    # Detectar @db:primary
    if '@db:primary' in comment:
        annotations['is_primary'] = True
    
    # Detectar @db:identity
    if '@db:identity' in comment:
        annotations['is_identity'] = True
    
    # Detectar @db:foreignKey ModelName
    fk_match = re.search(r'@db:foreignKey\s+(\w+)', comment)
    if fk_match:
        annotations['foreign_key'] = fk_match.group(1)
    
    # Detectar @db:varchar(n)
    varchar_match = re.search(r'@db:varchar\((\d+)\)', comment)
    if varchar_match:
        annotations['db_type'] = 'varchar'
        annotations['max_length'] = int(varchar_match.group(1))
    
    # Detectar @db:decimal(p,s)
    decimal_match = re.search(r'@db:decimal\((\d+),(\d+)\)', comment)
    if decimal_match:
        annotations['db_type'] = 'decimal'
        annotations['decimal_precision'] = int(decimal_match.group(1))
        annotations['decimal_scale'] = int(decimal_match.group(2))
    
    # Detectar @db:int, @db:bigint, @db:float, @db:text, @db:datetime
    for db_type in ['int', 'bigint', 'float', 'text', 'datetime']:
        if f'@db:{db_type}' in comment:
            annotations['db_type'] = db_type
            break
    
    # Detectar @default(value)
    default_match = re.search(r'@default\(([^)]+)\)', comment)
    if default_match:
        annotations['default_value'] = default_match.group(1)
    
    return annotations
```

### MODIFICACIÓN 2: Actualizar `_parse_interface_properties`

Reemplazar la función `_parse_interface_properties` (línea 364) con:

```python
def _parse_interface_properties(self, body: str) -> Dict[str, Dict]:
    """Parse interface properties from the body content"""
    properties = {}

    # Clean up the body pero PRESERVAR comentarios para extraer anotaciones
    body_no_multiline = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)

    # Pattern to match property definitions CON comentarios
    property_pattern = r"(\w+)(\?)?:\s*([^;,\n]+)(?://(.*))?[\n;]"

    matches = re.finditer(property_pattern, body_no_multiline)

    for match in matches:
        prop_name = match.group(1).strip()
        is_optional = match.group(2) == "?"
        prop_type = match.group(3).strip()
        comment = match.group(4).strip() if match.group(4) else ""

        # Extraer anotaciones del comentario
        annotations = self._extract_annotations_from_comment(comment)

        properties[prop_name] = {
            "name": prop_name,
            "type": prop_type,
            "optional": is_optional,
            "comment": comment,
            "annotations": annotations,
            "django_field": self._map_ts_type_to_django_field(
                prop_type, prop_name, is_optional, annotations
            ),
        }

    return properties
```

### MODIFICACIÓN 3: Actualizar `_map_ts_type_to_django_field`

Reemplazar la función `_map_ts_type_to_django_field` (línea 390) con:

```python
def _map_ts_type_to_django_field(
    self, ts_type: str, prop_name: str = "", is_optional: bool = False, annotations: Dict = None
) -> Dict[str, Any]:
    """
    Map TypeScript types to Django model fields
    
    PRIORITY ORDER:
    1. @db: annotations (highest priority)
    2. TypeScript type
    3. Field name patterns (lowest priority)
    """
    ts_type = ts_type.strip()
    prop_name_lower = prop_name.lower()
    annotations = annotations or {}
    
    # =====================================================
    # PRIORITY 1: @db: ANNOTATIONS
    # =====================================================
    
    # Handle @db:foreignKey
    if annotations.get('foreign_key'):
        related_model = annotations['foreign_key']
        field_options = {
            "on_delete": "models.CASCADE",
            "related_name": f"%(class)s_set",
        }
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        return {
            "field_type": "ForeignKey",
            "options": field_options,
            "import": "from django.db import models",
            "related_model": related_model,
        }
    
    # Handle @db:primary with specific types
    if annotations.get('is_primary'):
        if annotations.get('is_identity'):
            # IDENTITY(1,1) autoincremental
            return {
                "field_type": "BigAutoField",
                "options": {"primary_key": True},
                "import": "from django.db import models",
            }
        elif annotations.get('db_type') == 'varchar' or ts_type.lower() == 'string':
            # Primary key VARCHAR (para CUIDs)
            max_length = annotations.get('max_length', 50)
            return {
                "field_type": "CharField",
                "options": {
                    "max_length": max_length,
                    "primary_key": True,
                    "editable": False,
                },
                "import": "from django.db import models",
            }
    
    # Handle @db:varchar(n)
    if annotations.get('db_type') == 'varchar':
        max_length = annotations.get('max_length', 255)
        field_options = {"max_length": max_length}
        
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        if annotations.get('default_value'):
            default = annotations['default_value']
            if default not in ['cuid()', 'uuid()', 'now()']:
                field_options["default"] = f"'{default}'"
        
        return {
            "field_type": "CharField",
            "options": field_options,
            "import": "from django.db import models",
        }
    
    # Handle @db:text
    if annotations.get('db_type') == 'text':
        field_options = {}
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        return {
            "field_type": "TextField",
            "options": field_options,
            "import": "from django.db import models",
        }
    
    # Handle @db:int or @db:bigint
    if annotations.get('db_type') in ['int', 'bigint']:
        field_type = "BigIntegerField" if annotations['db_type'] == 'bigint' else "IntegerField"
        field_options = {}
        
        if annotations.get('default_value'):
            field_options["default"] = int(annotations['default_value'])
        
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        return {
            "field_type": field_type,
            "options": field_options,
            "import": "from django.db import models",
        }
    
    # Handle @db:decimal(p,s)
    if annotations.get('db_type') == 'decimal':
        precision = annotations.get('decimal_precision', 10)
        scale = annotations.get('decimal_scale', 2)
        field_options = {
            "max_digits": precision,
            "decimal_places": scale,
        }
        
        if annotations.get('default_value'):
            field_options["default"] = annotations['default_value']
        
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        return {
            "field_type": "DecimalField",
            "options": field_options,
            "import": "from django.db import models",
        }
    
    # Handle @db:float
    if annotations.get('db_type') == 'float':
        field_options = {}
        
        if annotations.get('default_value'):
            field_options["default"] = float(annotations['default_value'])
        
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        return {
            "field_type": "FloatField",
            "options": field_options,
            "import": "from django.db import models",
        }
    
    # Handle @db:datetime
    if annotations.get('db_type') == 'datetime':
        field_options = {}
        
        if prop_name_lower in ['createdat', 'created_at']:
            field_options["auto_now_add"] = True
        elif prop_name_lower in ['updatedat', 'updated_at']:
            field_options["auto_now"] = True
        
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        return {
            "field_type": "DateTimeField",
            "options": field_options,
            "import": "from django.db import models",
        }
    
    # =====================================================
    # PRIORITY 2: TYPESCRIPT TYPE MAPPING
    # =====================================================
    
    # Handle array types
    if ts_type.endswith("[]"):
        field_options = {"default": list}
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        return {
            "field_type": "JSONField",
            "options": field_options,
            "import": "from django.db import models",
        }
    
    # Handle TypeScript type references to constants
    type_choices_map = {
        "UserRoleType": ("CharField", "USER_ROLES_CHOICES", 50),
        "PermissionType": ("CharField", "PERMISSION_CHOICES", 50),
        "VehicleTypeKey": ("CharField", "VEHICLE_TYPES_CHOICES", 20),
        "AnalysisStatusKey": ("CharField", "ANALYSIS_STATUS_CHOICES", 20),
        "DensityLevelKey": ("CharField", "DENSITY_LEVELS_CHOICES", 10),
        "NotificationTypeKey": ("CharField", "NOTIFICATION_TYPES_CHOICES", 30),
        "AlertTypeKey": ("CharField", "ALERT_TYPE_CHOICES", 30),
        "PlateProcessingStatusKey": ("CharField", "PLATE_PROCESSING_STATUS_CHOICES", 20),
        "TrackingStatusKey": ("CharField", "TRACKING_STATUS_CHOICES", 20),
        "TrafficDirectionKey": ("CharField", "TRAFFIC_DIRECTION_CHOICES", 20),
    }
    
    if ts_type in type_choices_map:
        field_type, choices, max_length = type_choices_map[ts_type]
        field_options = {
            "max_length": max_length,
            "choices": choices,
        }
        if is_optional:
            field_options["blank"] = True
            field_options["null"] = True
        
        return {
            "field_type": field_type,
            "options": field_options,
            "import": "from django.db import models",
            "choices_import": choices,
        }
    
    # Basic type mappings
    type_mapping = {
        "string": {
            "field_type": "CharField",
            "options": {"max_length": 255},
        },
        "number": {
            "field_type": "IntegerField",
            "options": {},
        },
        "boolean": {
            "field_type": "BooleanField",
            "options": {"default": False},
        },
        "Date": {
            "field_type": "DateTimeField",
            "options": {},
        },
    }
    
    if ts_type.lower() in type_mapping:
        result = type_mapping[ts_type.lower()].copy()
        
        # Apply optional (nullable) rules
        if is_optional:
            result["options"]["blank"] = True
            result["options"]["null"] = True
        
        # Apply @default if specified
        if annotations.get('default_value'):
            default = annotations['default_value']
            if ts_type.lower() == 'boolean':
                result["options"]["default"] = default.lower() == 'true'
            elif ts_type.lower() == 'number':
                result["options"]["default"] = int(default) if default.isdigit() else 0
            elif default not in ['cuid()', 'uuid()', 'now()']:
                result["options"]["default"] = f"'{default}'"
        
        result["import"] = "from django.db import models"
        return result
    
    # Default fallback
    field_options = {}
    if is_optional:
        field_options["blank"] = True
        field_options["null"] = True
    
    return {
        "field_type": "TextField",
        "options": field_options,
        "import": "from django.db import models",
    }
```

### MODIFICACIÓN 4: Actualizar generación de código de campos

En la función `_generate_field_code` (línea 1145), agregar manejo de ForeignKey:

```python
def _generate_field_code(self, prop_name: str, prop_info: Dict) -> str:
    """Generate Django field code for a property"""
    django_field = prop_info["django_field"]
    field_type = django_field["field_type"]
    options = django_field.get("options", {})
    
    # Skip fields that are in BaseModel
    base_model_fields = {
        "id", "createdat", "updatedat", "isactive",
        "created_at", "updated_at", "is_active",
    }
    if prop_name.lower() in base_model_fields:
        return None
    
    # Handle ForeignKey specially
    if field_type == "ForeignKey":
        related_model = django_field.get("related_model", "RelatedModel")
        option_parts = [f"'{related_model}'"]
        
        for key, value in options.items():
            if key == "on_delete":
                option_parts.append(f"on_delete={value}")
            elif key == "related_name":
                option_parts.append(f"related_name='{value}'")
            elif isinstance(value, bool):
                option_parts.append(f"{key}={value}")
            elif isinstance(value, str) and key != "related_name":
                option_parts.append(f"{key}='{value}'")
            else:
                option_parts.append(f"{key}={value}")
        
        options_str = ", ".join(option_parts)
        return f"{prop_name} = models.ForeignKey({options_str})"
    
    # Build options string for other fields
    option_parts = []
    for key, value in options.items():
        if key == "choices" and isinstance(value, str):
            option_parts.append(f"choices={value}")
        elif key == "default" and value == "uuid.uuid4":
            option_parts.append("default=uuid.uuid4")
        elif isinstance(value, str) and key not in ["choices", "on_delete", "related_name"]:
            if not value.startswith("'"):
                option_parts.append(f'{key}="{value}"')
            else:
                option_parts.append(f"{key}={value}")
        elif isinstance(value, bool):
            option_parts.append(f"{key}={value}")
        elif value is list:
            option_parts.append(f"{key}=list")
        elif value is dict:
            option_parts.append(f"{key}=dict")
        else:
            option_parts.append(f"{key}={value}")

    options_str = ", ".join(option_parts)
    return f"{prop_name} = models.{field_type}({options_str})"
```

## 🎯 RESULTADO ESPERADO

Después de estas modificaciones, el script podrá:

✅ Leer anotaciones `@db:` de comentarios TypeScript
✅ Generar campos con tipos SQL Server apropiados
✅ Detectar Foreign Keys automáticamente  
✅ Manejar IDENTITY vs VARCHAR primary keys
✅ Aplicar `blank=True, null=True` para campos opcionales (`?`)
✅ Respetar valores @default
✅ Generar DECIMAL con precisión/escala correcta

## 📝 TESTING

Después de aplicar cambios, probar:

```bash
cd d:\TrafiSmart\backend
.\venv\Scripts\python.exe manage.py generate_entities --source-dir="../shared/src/entities" --organized --dry-run
```

Debe generar:
- `VehicleEntity.id` → `CharField(max_length=50, primary_key=True)`
- `Vehicle.trafficAnalysisId` → `ForeignKey('TrafficAnalysis', ...)`
- `Camera.locationId` → `ForeignKey('Location', ...)`
- Campos opcionales → `blank=True, null=True`
