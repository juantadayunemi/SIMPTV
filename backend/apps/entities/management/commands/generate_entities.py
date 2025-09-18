import os
import re
import ast
from typing import Dict, List, Any, Tuple
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
import logging

logger = logging.getLogger("entities.generator")


class TypeScriptEntityParser:
    """Parser for TypeScript entity files to extract interface definitions"""

    def __init__(self):
        self.interfaces = {}
        self.imports = []

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a TypeScript file and extract interface definitions"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(f"Parsing TypeScript file: {file_path}")

            # Extract imports
            self.imports = self._extract_imports(content)

            # Extract interfaces
            interfaces = self._extract_interfaces(content)

            return {
                "file_path": str(file_path),
                "imports": self.imports,
                "interfaces": interfaces,
            }

        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return {}

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from TypeScript content"""
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(import_pattern, content)
        return matches

    def _extract_interfaces(self, content: str) -> Dict[str, Dict]:
        """Extract interface definitions from TypeScript content"""
        interfaces = {}

        # Pattern to match interface definitions
        interface_pattern = (
            r"export\s+interface\s+(\w+)(?:\s+extends\s+([^{]+))?\s*\{([^}]*)\}"
        )

        matches = re.finditer(interface_pattern, content, re.DOTALL)

        for match in matches:
            interface_name = match.group(1)
            extends_clause = match.group(2).strip() if match.group(2) else None
            interface_body = match.group(3)

            properties = self._parse_interface_properties(interface_body)

            interfaces[interface_name] = {
                "name": interface_name,
                "extends": extends_clause,
                "properties": properties,
            }

        return interfaces

    def _parse_interface_properties(self, body: str) -> Dict[str, Dict]:
        """Parse interface properties from the body content"""
        properties = {}

        # Clean up the body
        body = re.sub(r"//.*?\n", "", body)  # Remove single-line comments
        body = re.sub(
            r"/\*.*?\*/", "", body, flags=re.DOTALL
        )  # Remove multi-line comments

        # Pattern to match property definitions
        property_pattern = r"(\w+)(\?)?:\s*([^;,\n]+)"

        matches = re.finditer(property_pattern, body)

        for match in matches:
            prop_name = match.group(1).strip()
            is_optional = match.group(2) == "?"
            prop_type = match.group(3).strip()

            properties[prop_name] = {
                "name": prop_name,
                "type": prop_type,
                "optional": is_optional,
                "django_field": self._map_ts_type_to_django_field(prop_type, prop_name),
            }

        return properties

    def _map_ts_type_to_django_field(
        self, ts_type: str, prop_name: str = ""
    ) -> Dict[str, Any]:
        """Map TypeScript types to Django model fields"""
        ts_type = ts_type.strip()
        prop_name = prop_name.lower()

        # Handle array types
        if ts_type.endswith("[]"):
            base_type = ts_type[:-2]
            return {
                "field_type": "JSONField",
                "options": {"default": list},
                "import": "from django.db import models",
            }

        # Handle union types (e.g., string | null)
        if "|" in ts_type:
            # Take the first non-null type
            types = [t.strip() for t in ts_type.split("|")]
            non_null_types = [
                t for t in types if t.lower() not in ["null", "undefined"]
            ]
            if non_null_types:
                ts_type = non_null_types[0]

        # IMPROVED: Handle TypeScript type references to constants
        if ts_type in ["UserRoleType", "PermissionType"]:
            return {
                "field_type": "CharField",
                "options": {"max_length": 50, "choices": "USER_ROLES_CHOICES"},
                "import": "from django.db import models",
                "choices_import": "USER_ROLES_CHOICES",
            }
        elif ts_type in ["VehicleTypeKey", "VehicleType"]:
            return {
                "field_type": "CharField",
                "options": {"max_length": 20, "choices": "VEHICLE_TYPES_CHOICES"},
                "import": "from django.db import models",
                "choices_import": "VEHICLE_TYPES_CHOICES",
            }
        elif ts_type in ["AnalysisStatusKey", "AnalysisStatus"]:
            return {
                "field_type": "CharField",
                "options": {"max_length": 20, "choices": "ANALYSIS_STATUS_CHOICES"},
                "import": "from django.db import models",
                "choices_import": "ANALYSIS_STATUS_CHOICES",
            }
        elif ts_type in ["DensityLevelKey", "DensityLevel"]:
            return {
                "field_type": "CharField",
                "options": {"max_length": 10, "choices": "DENSITY_LEVELS_CHOICES"},
                "import": "from django.db import models",
                "choices_import": "DENSITY_LEVELS_CHOICES",
            }
        elif ts_type in ["NotificationTypeKey", "NotificationType"]:
            return {
                "field_type": "CharField",
                "options": {"max_length": 30, "choices": "NOTIFICATION_TYPES_CHOICES"},
                "import": "from django.db import models",
                "choices_import": "NOTIFICATION_TYPES_CHOICES",
            }

        # Special handling for common field patterns
        if "id" in prop_name and ts_type.lower() == "number":
            return {
                "field_type": "BigIntegerField",
                "options": {},
                "import": "from django.db import models",
            }
        elif "email" in prop_name:
            return {
                "field_type": "EmailField",
                "options": {"max_length": 255},
                "import": "from django.db import models",
            }
        elif "phone" in prop_name:
            return {
                "field_type": "CharField",
                "options": {"max_length": 20},
                "import": "from django.db import models",
            }
        elif "price" in prop_name or "amount" in prop_name:
            return {
                "field_type": "DecimalField",
                "options": {"max_digits": 10, "decimal_places": 2},
                "import": "from django.db import models",
            }

        # Basic type mappings
        type_mapping = {
            "string": {
                "field_type": "CharField",
                "options": {"max_length": 255},
                "import": "from django.db import models",
            },
            "number": {
                "field_type": "FloatField",
                "options": {},
                "import": "from django.db import models",
            },
            "boolean": {
                "field_type": "BooleanField",
                "options": {"default": False},
                "import": "from django.db import models",
            },
            "Date": {
                "field_type": "DateTimeField",
                "options": {},
                "import": "from django.db import models",
            },
            "any": {
                "field_type": "JSONField",
                "options": {"default": dict},
                "import": "from django.db import models",
            },
            "object": {
                "field_type": "JSONField",
                "options": {"default": dict},
                "import": "from django.db import models",
            },
        }

        # Check for specific patterns
        if ts_type.lower() in type_mapping:
            return type_mapping[ts_type.lower()]
        elif ts_type.startswith("Array<"):
            return {
                "field_type": "JSONField",
                "options": {"default": list},
                "import": "from django.db import models",
            }
        elif ts_type.endswith("[]"):
            return {
                "field_type": "JSONField",
                "options": {"default": list},
                "import": "from django.db import models",
            }

        # Handle Date types properly
        if ts_type.lower() == "date":
            return {
                "field_type": "DateTimeField",
                "options": {"auto_now_add": False},
                "import": "from django.db import models",
            }

        # Check if it's a reference to another interface (relationship)
        if ts_type[0].isupper():  # Capitalized = likely interface reference
            return {
                "field_type": "JSONField",
                "options": {
                    "default": dict,
                    "help_text": f"Reference to {ts_type} interface",
                },
                "import": "from django.db import models",
            }

        # Default to TextField for unknown types
        return {
            "field_type": "TextField",
            "options": {"blank": True, "null": True},
            "import": "from django.db import models",
        }


class DjangoModelGenerator:
    """Generator for Django models from parsed TypeScript interfaces"""

    def __init__(self):
        self.generated_models = []
        self.categories = {
            "auth": ["UserEntity", "UserRoleEntity"],
            "traffic": [
                "TrafficAnalysisEntity",
                "VehicleDetectionEntity",
                "TrafficHistoricalDataEntity",
                "LocationTrafficPatternEntity",
            ],
            "plates": ["PlateDetectionEntity", "PlateAnalysisEntity"],
            "predictions": [
                "PredictionModelEntity",
                "ModelTrainingJobEntity",
                "TrafficPredictionEntity",
                "BatchPredictionEntity",
                "PredictionAccuracyEntity",
                "RealTimePredictionEntity",
            ],
            "notifications": ["NotificationEntity", "NotificationSettingsEntity"],
            "common": ["WeatherDataEntity", "EventDataEntity"],
        }

    def generate_model_code(self, interface_data: Dict[str, Any]) -> str:
        """Generate Django model code from interface data"""
        models_code = []

        # Add imports
        models_code.append("from django.db import models")
        models_code.append("from .models import BaseModel")
        models_code.append("")

        for interface_name, interface_info in interface_data.get(
            "interfaces", {}
        ).items():
            model_code = self._generate_single_model(interface_name, interface_info)
            models_code.append(model_code)
            models_code.append("")

        return "\n".join(models_code)

    def generate_organized_structure(
        self,
        interface_data: Dict[str, Any],
        constants_data: Dict[str, Any],
        base_path: Path,
    ) -> Dict[str, str]:
        """Generate organized file structure with separate files by category"""
        generated_files = {}

        # Categorize interfaces
        categorized_interfaces = self._categorize_interfaces(
            interface_data.get("interfaces", {})
        )

        # Generate base models file
        base_content = self._generate_base_file()
        generated_files["models/base.py"] = base_content

        # Generate category-specific model files
        for category, interfaces in categorized_interfaces.items():
            if interfaces:
                category_content = self._generate_category_models(category, interfaces)
                generated_files[f"models/{category}.py"] = category_content

        # Generate models __init__.py
        models_init = self._generate_models_init(categorized_interfaces)
        generated_files["models/__init__.py"] = models_init

        # Generate constants files
        constants_files = self._generate_constants_files(constants_data)
        generated_files.update(constants_files)

        # Generate constants __init__.py
        constants_init = self._generate_constants_init(constants_data)
        generated_files["constants/__init__.py"] = constants_init

        return generated_files

    def _categorize_interfaces(self, interfaces: Dict[str, Dict]) -> Dict[str, Dict]:
        """Categorize interfaces by their domain"""
        categorized = {category: {} for category in self.categories.keys()}

        for interface_name, interface_info in interfaces.items():
            # Find which category this interface belongs to
            category_found = False
            for category, entity_list in self.categories.items():
                if interface_name in entity_list:
                    categorized[category][interface_name] = interface_info
                    category_found = True
                    break

            # If not found in predefined categories, put in common
            if not category_found:
                categorized["common"][interface_name] = interface_info

        return categorized

    def _generate_base_file(self) -> str:
        """Generate the base.py file with BaseModel"""
        lines = []
        lines.append("from django.db import models")
        lines.append("")
        lines.append("")
        lines.append("class BaseModel(models.Model):")
        lines.append(
            '    """Base abstract model with common fields for all entities"""'
        )
        lines.append("")
        lines.append(
            '    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")'
        )
        lines.append(
            '    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")'
        )
        lines.append(
            '    is_active = models.BooleanField(default=True, verbose_name="Is Active")'
        )
        lines.append("")
        lines.append("    class Meta:")
        lines.append("        abstract = True")
        lines.append("")
        lines.append("    def __str__(self):")
        lines.append('        return f"{self.__class__.__name__} ({self.pk})"')

        return "\n".join(lines)

    def _generate_category_models(
        self, category: str, interfaces: Dict[str, Dict]
    ) -> str:
        """Generate models for a specific category"""
        lines = []
        lines.append("from django.db import models")
        lines.append("from .base import BaseModel")
        lines.append("from ..constants import (")

        # Add constants imports based on category
        if category == "auth":
            lines.append("    USER_ROLES_CHOICES,")
        elif category in ["traffic", "plates", "predictions", "common"]:
            lines.append("    VEHICLE_TYPES_CHOICES,")
            lines.append("    ANALYSIS_STATUS_CHOICES,")
            lines.append("    DENSITY_LEVELS_CHOICES,")
        if category == "notifications":
            lines.append("    NOTIFICATION_TYPES_CHOICES,")

        lines.append(")")
        lines.append("")
        lines.append("")

        # Generate models for this category
        for interface_name, interface_info in interfaces.items():
            model_code = self._generate_single_model(interface_name, interface_info)
            lines.append(model_code)
            lines.append("")

        return "\n".join(lines)

    def _generate_models_init(self, categorized_interfaces: Dict[str, Dict]) -> str:
        """Generate models/__init__.py with all imports"""
        lines = []
        lines.append('"""')
        lines.append("ENTITIES MODELS - Organized by Category")
        lines.append("Auto-generated from TypeScript entities")
        lines.append('"""')
        lines.append("")
        lines.append("from .base import BaseModel")
        lines.append("")

        # Import all models from each category
        for category, interfaces in categorized_interfaces.items():
            if interfaces:
                lines.append(f"# {category.title()} Models")
                model_names = list(interfaces.keys())
                lines.append(f"from .{category} import (")
                for model_name in model_names:
                    lines.append(f"    {model_name},")
                lines.append(")")
                lines.append("")

        # Create __all__ list
        lines.append("__all__ = [")
        lines.append('    "BaseModel",')
        for category, interfaces in categorized_interfaces.items():
            if interfaces:
                for model_name in interfaces.keys():
                    lines.append(f'    "{model_name}",')
        lines.append("]")

        return "\n".join(lines)

    def _generate_constants_files(
        self, constants_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate separate constants files by category"""
        constants_files = {}

        # Categorize constants by their domain
        constants_categories = {
            "roles": ["USER_ROLES", "PERMISSIONS", "ROLE_PERMISSIONS"],
            "traffic": ["VEHICLE_TYPES", "ANALYSIS_STATUS", "DENSITY_LEVELS"],
            "notifications": ["NOTIFICATION_TYPES", "NotificationType"],
            "common": [
                "DataTypeKey",
                "GroupByDataKey",
                "API_ENDPOINTS",
                "FILE_UPLOAD",
                "PAGINATION",
                "TIME",
                "SYSTEM_LIMITS",
            ],
        }

        for category, const_names in constants_categories.items():
            category_constants = {}

            # Find constants that belong to this category
            for file_data in constants_data.values():
                for const_name, const_info in file_data.get("constants", {}).items():
                    if const_name in const_names:
                        category_constants[const_name] = const_info

            # Generate file content if we have constants for this category
            if category_constants:
                content = self._generate_constants_category_file(
                    category, category_constants
                )
                constants_files[f"constants/{category}.py"] = content

        return constants_files

    def _generate_constants_category_file(
        self, category: str, constants: Dict[str, Dict]
    ) -> str:
        """Generate a constants file for a specific category"""
        lines = []
        lines.append(f'"""')
        lines.append(f"{category.upper()} CONSTANTS")
        lines.append("Auto-generated from TypeScript types")
        lines.append('"""')
        lines.append("")

        for const_name, const_info in constants.items():
            # Generate the constant class
            lines.append(f"class {const_name}:")
            lines.append(f'    """Constants from TypeScript {const_name}"""')

            # Add individual constants
            for key, value in const_info["values"].items():
                lines.append(f'    {key} = "{value}"')

            lines.append("")

            # Generate choices tuple
            choices_name = f"{const_name}_CHOICES"
            lines.append(f"{choices_name} = (")
            for choice_tuple in const_info["django_choices"]:
                lines.append(f'    ("{choice_tuple[0]}", "{choice_tuple[1]}"),')
            lines.append(")")
            lines.append("")

        return "\n".join(lines)

    def _generate_constants_init(self, constants_data: Dict[str, Any]) -> str:
        """Generate constants/__init__.py with all imports"""
        lines = []
        lines.append('"""')
        lines.append("ENTITIES CONSTANTS - Organized by Category")
        lines.append("Auto-generated from TypeScript types")
        lines.append('"""')
        lines.append("")

        # Determine which categories have constants
        categories_with_constants = set()
        constants_categories = {
            "roles": ["USER_ROLES", "PERMISSIONS", "ROLE_PERMISSIONS"],
            "traffic": ["VEHICLE_TYPES", "ANALYSIS_STATUS", "DENSITY_LEVELS"],
            "notifications": ["NOTIFICATION_TYPES", "NotificationType"],
            "common": [
                "DataTypeKey",
                "GroupByDataKey",
                "API_ENDPOINTS",
                "FILE_UPLOAD",
                "PAGINATION",
                "TIME",
                "SYSTEM_LIMITS",
            ],
        }

        all_constants = []
        for file_data in constants_data.values():
            for const_name in file_data.get("constants", {}).keys():
                for category, const_names in constants_categories.items():
                    if const_name in const_names:
                        categories_with_constants.add(category)
                        all_constants.append((const_name, category))
                        break

        # Import from each category
        for category in sorted(categories_with_constants):
            category_constants = [
                name for name, cat in all_constants if cat == category
            ]
            if category_constants:
                lines.append(f"# {category.title()} Constants")
                lines.append(f"from .{category} import (")
                for const_name in sorted(category_constants):
                    lines.append(f"    {const_name},")
                    lines.append(f"    {const_name}_CHOICES,")
                lines.append(")")
                lines.append("")

        # Create __all__ list
        lines.append("__all__ = [")
        for const_name, category in sorted(all_constants):
            lines.append(f'    "{const_name}",')
            lines.append(f'    "{const_name}_CHOICES",')
        lines.append("]")

        return "\n".join(lines)

    def _generate_single_model(self, interface_name: str, interface_info: Dict) -> str:
        """Generate code for a single Django model"""
        lines = []

        # Class definition
        base_class = "BaseModel"
        if interface_info.get("extends"):
            # TODO: Handle inheritance properly
            pass

        lines.append(f"class {interface_name}(BaseModel):")
        lines.append(
            f'    """Abstract DLL model from TypeScript interface {interface_name}"""'
        )
        lines.append(
            f'    """USAGE: Inherit in other apps - class User({interface_name}): pass"""'
        )
        lines.append("")

        # Generate fields
        properties = interface_info.get("properties", {})

        if not properties:
            lines.append("    pass")
        else:
            for prop_name, prop_info in properties.items():
                field_code = self._generate_field_code(prop_name, prop_info)
                lines.append(f"    {field_code}")

        # Add Meta class - ABSTRACT MODEL for DLL usage
        lines.append("")
        lines.append("    class Meta:")
        lines.append("        abstract = True  # DLL model - inherit in other apps")
        lines.append(f'        verbose_name = "Abstract {interface_name}"')
        lines.append(f'        verbose_name_plural = "Abstract {interface_name}s"')

        # Add __str__ method
        lines.append("")
        lines.append("    def __str__(self):")
        # Try to find a reasonable field for string representation
        name_fields = ["name", "title", "label", "description"]
        str_field = None
        for field in name_fields:
            if field in properties:
                str_field = field
                break

        if str_field:
            lines.append(f"        return f'{{self.{str_field}}} ({{self.pk}})'")
        else:
            lines.append(f"        return f'{interface_name} ({{self.pk}})'")

        return "\n".join(lines)

    def _generate_field_code(self, prop_name: str, prop_info: Dict) -> str:
        """Generate Django field code for a property"""
        django_field = prop_info["django_field"]
        field_type = django_field["field_type"]
        options = django_field.get("options", {})

        # Handle optional fields
        if prop_info["optional"]:
            options.update({"blank": True, "null": True})

        # Special handling for id fields - don't override Django's default id
        if prop_name.lower() == "id":
            return f"# {prop_name} field inherited from BaseModel (auto-generated primary key)"

        # Build options string
        option_parts = []
        for key, value in options.items():
            if key == "choices" and isinstance(value, str):
                # Handle choices references
                option_parts.append(f"{key}={value}")
            elif isinstance(value, str) and key != "choices":
                option_parts.append(f"{key}='{value}'")
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


class TypeScriptTypesParser:
    """Parser for TypeScript types and enums to Django choices/constants"""

    def __init__(self):
        self.constants = {}
        self.choices = {}
        self.types = {}

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a TypeScript types file and extract constants/enums"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(f"Parsing TypeScript types file: {file_path}")

            # Extract const objects (like USER_ROLES)
            constants = self._extract_constants(content)

            # Extract type definitions
            types = self._extract_types(content)

            return {
                "file_path": str(file_path),
                "constants": constants,
                "types": types,
            }

        except Exception as e:
            logger.error(f"Error parsing types file {file_path}: {e}")
            return {}

    def _extract_constants(self, content: str) -> Dict[str, Dict]:
        """Extract const object definitions like USER_ROLES, PERMISSIONS"""
        constants = {}

        # Pattern to match const objects like: export const USER_ROLES = { ... }
        const_pattern = r"export\s+const\s+(\w+)\s*=\s*\{([^}]*)\}\s*as\s+const"

        matches = re.finditer(const_pattern, content, re.DOTALL)

        for match in matches:
            const_name = match.group(1)
            const_body = match.group(2)

            # Parse key-value pairs within the const
            pairs = self._parse_const_body(const_body)

            constants[const_name] = {
                "name": const_name,
                "values": pairs,
                "django_choices": self._convert_to_django_choices(pairs, const_name),
            }

        return constants

    def _parse_const_body(self, body: str) -> Dict[str, str]:
        """Parse the body of a const object to extract key-value pairs"""
        pairs = {}

        # Clean up the body
        body = re.sub(r"//.*?\n", "", body)  # Remove comments
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)

        # Pattern for key: 'value' pairs
        pair_pattern = r"(\w+):\s*['\"]([^'\"]+)['\"]"

        matches = re.finditer(pair_pattern, body)

        for match in matches:
            key = match.group(1)
            value = match.group(2)
            pairs[key] = value

        return pairs

    def _convert_to_django_choices(
        self, pairs: Dict[str, str], const_name: str
    ) -> List[tuple]:
        """Convert TypeScript const values to Django choices format"""
        choices = []

        for key, value in pairs.items():
            # Create human-readable label
            label = key.replace("_", " ").title()
            choices.append((value, label))

        return choices

    def _extract_types(self, content: str) -> Dict[str, Dict]:
        """Extract type definitions"""
        types = {}

        # Pattern for type aliases like: export type UserRoleType = typeof USER_ROLES[keyof typeof USER_ROLES]
        type_pattern = r"export\s+type\s+(\w+)\s*=\s*(.+?);"

        matches = re.finditer(type_pattern, content, re.DOTALL)

        for match in matches:
            type_name = match.group(1)
            type_definition = match.group(2).strip()

            types[type_name] = {"name": type_name, "definition": type_definition}

        return types

    def generate_django_constants(self, all_types_data: Dict[str, Any]) -> str:
        """Generate Django constants and choices from all parsed types"""
        lines = []

        lines.append(
            "# ============================================================================"
        )
        lines.append("# DJANGO CONSTANTS & CHOICES")
        lines.append("# Auto-generated from TypeScript types")
        lines.append(
            "# ============================================================================"
        )
        lines.append("")

        # Generate constants for each file
        for file_data in all_types_data.values():
            constants = file_data.get("constants", {})

            if constants:
                file_name = Path(file_data["file_path"]).name
                lines.append(f"# From {file_name}")
                lines.append("")

                for const_name, const_data in constants.items():
                    # Generate the constant class
                    lines.append(f"class {const_name}:")
                    lines.append(f'    """Constants from TypeScript {const_name}"""')

                    # Add individual constants
                    for key, value in const_data["values"].items():
                        lines.append(f'    {key} = "{value}"')

                    lines.append("")

                    # Generate choices tuple
                    choices_name = f"{const_name}_CHOICES"
                    lines.append(f"{choices_name} = (")
                    for choice_tuple in const_data["django_choices"]:
                        lines.append(f'    ("{choice_tuple[0]}", "{choice_tuple[1]}"),')
                    lines.append(")")
                    lines.append("")

        return "\n".join(lines)


class Command(BaseCommand):
    help = "Generate Django models from TypeScript entity interfaces"

    def add_arguments(self, parser):
        parser.add_argument(
            "--shared-path",
            type=str,
            default="../shared/src",
            help="Path to TypeScript shared directory (default: ../shared/src)",
        )

        parser.add_argument(
            "--entities-only",
            action="store_true",
            help="Generate only entities (skip types/enums)",
        )

        parser.add_argument(
            "--organized",
            action="store_true",
            help="Generate organized structure with separate files by category",
        )

        parser.add_argument(
            "--output-file",
            type=str,
            default="apps/entities/models.py",
            help="Output file for generated models (default: apps/entities/models.py)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be generated without writing files",
        )

    def handle(self, *args, **options):
        shared_path = Path(options["shared_path"])
        output_file = Path(options["output_file"])
        dry_run = options["dry_run"]
        entities_only = options["entities_only"]
        organized = options["organized"]

        self.stdout.write(f"Looking for TypeScript files in: {shared_path.absolute()}")

        if not shared_path.exists():
            raise CommandError(f"Shared path does not exist: {shared_path.absolute()}")

        # Find all TypeScript files in all subdirectories
        ts_files = list(shared_path.glob("**/*.ts"))

        if not ts_files:
            raise CommandError(
                f"No TypeScript files found in: {shared_path.absolute()}"
            )

        self.stdout.write(f"Found {len(ts_files)} TypeScript files")

        # Categorize files (using Path separators for Windows compatibility)
        entity_files = [f for f in ts_files if "entities" in f.parts]
        type_files = [f for f in ts_files if "types" in f.parts]

        self.stdout.write(f"Entity files: {len(entity_files)}")
        self.stdout.write(f"Type files: {len(type_files)}")

        # Parse TypeScript files
        entity_parser = TypeScriptEntityParser()
        types_parser = TypeScriptTypesParser()
        model_generator = DjangoModelGenerator()

        all_interfaces = {}
        all_types = {}

        # Parse entity files
        for ts_file in entity_files:
            self.stdout.write(f"Parsing entity: {ts_file.name}")
            parsed_data = entity_parser.parse_file(ts_file)
            if parsed_data.get("interfaces"):
                all_interfaces.update(parsed_data["interfaces"])

        # Parse type files (unless entities-only)
        if not entities_only:
            for ts_file in type_files:
                self.stdout.write(f"Parsing types: {ts_file.name}")
                parsed_data = types_parser.parse_file(ts_file)
                if parsed_data:
                    all_types[ts_file.stem] = parsed_data

        if not all_interfaces:
            self.stdout.write(
                self.style.WARNING("No interfaces found in TypeScript files")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {len(all_interfaces)} interfaces: {', '.join(all_interfaces.keys())}"
            )
        )

        if all_types:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found types in {len(all_types)} files: {', '.join(all_types.keys())}"
                )
            )

        # Generate Django code
        if organized:
            # Generate organized structure with separate files
            self.stdout.write("Generating organized structure...")

            entities_base_path = Path("apps/entities")
            organized_files = model_generator.generate_organized_structure(
                {"interfaces": all_interfaces}, all_types, entities_base_path
            )

            if dry_run:
                self.stdout.write(
                    self.style.WARNING("\n--- DRY RUN - Organized Structure ---")
                )
                for file_path, content in organized_files.items():
                    self.stdout.write(f"\n=== {file_path} ===")
                    self.stdout.write(
                        content[:500] + "..." if len(content) > 500 else content
                    )
                return
            else:
                # Create the organized structure
                self._create_organized_structure(organized_files)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully generated organized structure with {len(organized_files)} files"
                    )
                )
                return
        else:
            # Generate single file (original behavior)
            generated_code_parts = []

            # Generate constants and choices from types
            if all_types:
                constants_code = types_parser.generate_django_constants(all_types)
                generated_code_parts.append(constants_code)

            # Generate models from interfaces
            models_code = model_generator.generate_model_code(
                {"interfaces": all_interfaces}
            )
            generated_code_parts.append(models_code)

            generated_code = "\n\n".join(generated_code_parts)

            if dry_run:
                self.stdout.write(
                    self.style.WARNING("\n--- DRY RUN - Generated Code ---")
                )
                self.stdout.write(generated_code)
                return

        # Read existing models.py to preserve BaseModel
        existing_code = ""
        if output_file.exists():
            with open(output_file, "r", encoding="utf-8") as f:
                existing_code = f.read()

        # Find the marker comment and preserve everything before it
        marker = "# Auto-generated models will be added below this comment"
        if marker in existing_code:
            preserved_part = existing_code.split(marker)[0] + marker
        else:
            preserved_part = (
                existing_code
                if existing_code
                else '''from django.db import models

# This file will contain auto-generated Django models from TypeScript entities
# Models will be generated by the entity generator system

class BaseModel(models.Model):
    """Base model with common fields for all entities"""
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    
    class Meta:
        abstract = True
        
    def __str__(self):
        return f"{self.__class__.__name__} ({self.pk})"


# Auto-generated models will be added below this comment'''
            )

        # Combine preserved part with generated models
        final_code = (
            preserved_part
            + "\n# DO NOT EDIT MANUALLY - Use the entity generator system\n"
        )
        final_code += f"# Generated models from {shared_path}\n\n"
        final_code += generated_code

        # Write the final code
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_code)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated {len(all_interfaces)} Django models in {output_file}"
            )
        )

    def _create_organized_structure(self, organized_files: Dict[str, str]):
        """Create the organized file structure on disk"""
        base_path = Path("apps/entities")

        # Create directories
        (base_path / "models").mkdir(parents=True, exist_ok=True)
        (base_path / "constants").mkdir(parents=True, exist_ok=True)

        # Write all files
        for file_path, content in organized_files.items():
            full_path = base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.stdout.write(f"Created: {full_path}")
