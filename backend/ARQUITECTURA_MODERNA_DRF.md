# Guía de Arquitectura Moderna Django REST Framework

## 🎯 Principios

### 1. **Convención sobre Configuración** (como .NET)
- Django: `snake_case` en modelos/DB
- TypeScript: `camelCase` en frontend
- **Conversión automática** en la capa de API

### 2. **DRY (Don't Repeat Yourself)**
- Usar `ViewSets` en lugar de `APIView`
- Usar `'__all__'` en serializers cuando sea posible
- Reutilizar mixins y permisos

---

## 📐 Arquitectura Implementada

### **Capa de Conversión Automática**

```
Frontend (camelCase)  ←→  [Renderer/Parser]  ←→  Backend (snake_case)
{                                                   {
  firstName: "Juan"                                   first_name: "Juan"
  isActive: true          <conversión                is_active: True
  createdAt: "2025-..."    automática>               created_at: datetime(...)
}                                                   }
```

**Implementación:**
```python
# config/settings.py
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "utils.renderers.CamelCaseJSONRenderer",  # snake_case → camelCase
    ],
    "DEFAULT_PARSER_CLASSES": [
        "utils.renderers.CamelCaseJSONParser",  # camelCase → snake_case
    ],
}
```

---

## 🔧 Modernización de Código

### **ANTES (Manual, verboso):**

```python
# ❌ Serializer manual
class UserSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    isActive = serializers.BooleanField(source='is_active')
    fullName = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName', 'isActive', 'fullName']
        
# ❌ View manual
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=201)
```

### **DESPUÉS (Automático, limpio):**

```python
# ✅ Serializer automático
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()  # Conversión automática a fullName
    
    class Meta:
        model = User
        fields = '__all__'  # Todos los campos automáticamente
        # O especificar:
        # fields = ['id', 'first_name', 'last_name', 'is_active', 'full_name']
        
# ✅ ViewSet automático (CRUD completo)
class UserViewSet(viewsets.ModelViewSet):
    """
    Endpoints generados automáticamente:
    - GET    /api/users/          → list()
    - POST   /api/users/          → create()
    - GET    /api/users/{id}/     → retrieve()
    - PUT    /api/users/{id}/     → update()
    - PATCH  /api/users/{id}/     → partial_update()
    - DELETE /api/users/{id}/     → destroy()
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'email_confirmed']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']
```

---

## 🎨 Estructura de Archivos (Recomendada)

```
auth_app/
├── models.py           # Modelos (hereda de entities)
├── serializers.py      # Serializers minimalistas
├── viewsets.py         # ViewSets (en lugar de views.py)
├── permissions.py      # Permisos personalizados
├── filters.py          # Filtros personalizados
├── urls.py             # URLs con router
└── tests/
    ├── test_models.py
    ├── test_serializers.py
    └── test_viewsets.py
```

---

## 🚀 Eliminando views.py (Solo API)

### **Opción 1: ViewSets con Router (Recomendado)**

```python
# viewsets.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

# urls.py
from rest_framework.routers import DefaultRouter
from .viewsets import AuthViewSet

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = router.urls

# URLs generadas automáticamente:
# POST /api/auth/login/
# POST /api/auth/register/
```

### **Opción 2: Generic Views (Intermedio)**

```python
# views.py (sin APIView manual)
from rest_framework import generics

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# urls.py
urlpatterns = [
    path('users/', UserListCreateView.as_view()),
    path('users/<int:pk>/', UserDetailView.as_view()),
]
```

---

## 🔐 Manejo de Errores Centralizado

```python
# utils/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    """Manejador centralizado de excepciones"""
    response = exception_handler(exc, context)
    
    if response is not None:
        # Formato consistente de errores
        response.data = {
            'success': False,
            'error': response.data.get('detail', 'Error'),
            'code': getattr(exc, 'default_code', 'error'),
            'status_code': response.status_code
        }
    
    return response

# config/settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
}
```

---

## 📊 Comparación .NET vs Django

| Concepto .NET | Equivalente Django | Ventaja |
|---------------|-------------------|---------|
| `Controller` | `ViewSet` | ✅ Menos código |
| `Entity Framework` | `Django ORM` | ✅ Más simple |
| `DTO` | `Serializer` | ✅ Validación automática |
| `Attribute [Route]` | `router.register()` | ✅ URLs automáticas |
| `AutoMapper` | `CamelCaseRenderer` | ✅ Conversión automática |

---

## ✅ Checklist de Modernización

- [x] Renderer/Parser para conversión camelCase ↔ snake_case
- [ ] Migrar `APIView` → `ViewSet`
- [ ] Usar `'__all__'` en serializers simples
- [ ] Implementar `router` en `urls.py`
- [ ] Centralizar manejo de errores
- [ ] Agregar filtros y búsqueda con `django-filter`
- [ ] Documentación automática con `drf-spectacular`

---

## 🎯 Próximos Pasos

1. **Actualizar serializadores** para usar campos snake_case
2. **Migrar a ViewSets** para auth_app
3. **Eliminar código manual** redundante
4. **Agregar tests** unitarios

---

## 📚 Referencias

- [Django REST Framework ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [DRF Routers](https://www.django-rest-framework.org/api-guide/routers/)
- [DRF Best Practices](https://www.django-rest-framework.org/topics/best-practices/)
