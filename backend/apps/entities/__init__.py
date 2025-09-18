"""
ENTITIES LIBRARY - SHARED MODELS DLL

This app functions as a shared models library (DLL) for the Django project.
Models are automatically generated from TypeScript entities located in:
../shared/src/entities/

USAGE IN OTHER APPS:
    from apps.entities.models import UserEntity, TrafficAnalysisEntity

    # Use the models directly - no inheritance needed
    user = UserEntity.objects.create(email="test@example.com")

REGENERATE MODELS:
    python manage.py generate_entities
    python manage.py makemigrations apps.entities
    python manage.py migrate

STRUCTURE:
    - BaseModel: Abstract base with common fields (created_at, updated_at, is_active)
    - Generated Models: Concrete models from TypeScript interfaces
"""
