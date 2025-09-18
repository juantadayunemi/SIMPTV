# Traffic Analysis System

Sistema completo de análisis de tráfico con detección de placas y predicción usando Machine Learning.

## 🚀 Descripción del Proyecto

Este sistema permite analizar videos de tráfico para:
- Detectar y contar vehículos
- Identificar placas de matrícula usando YOLO
- Generar predicciones de tráfico con scikit-learn
- Gestionar usuarios con múltiples roles
- Enviar notificaciones por email y WhatsApp

## 🏗️ Arquitectura

El proyecto está dividido en 3 módulos independientes:

```
Urbia/
├── shared/          # Tipos y esquemas compartidos (TypeScript)
├── backend/         # API REST con FastAPI (Python)
├── frontend/        # Dashboard web con React (TypeScript)
├── README.md        # Este archivo
├── .gitignore       # Archivos a ignorar en Git
└── package.json     # Scripts de workspace
```

### 📦 Módulos

#### Shared (TypeScript)
- **Propósito**: Tipos, esquemas y constantes compartidas
- **Tecnologías**: TypeScript, Zod para validación
- **Exports**: Interfaces de User, TrafficAnalysis, PlateDetection, etc.

#### Backend (Python/FastAPI)
- **Propósito**: API REST con análisis ML y procesamiento de video
- **Tecnologías**: FastAPI, Prisma ORM, SQL Server, OpenCV, YOLO, scikit-learn
- **Features**: Autenticación JWT, análisis de video, detección de placas, predicciones

#### Frontend (React/TypeScript)
- **Propósito**: Dashboard web para gestión y visualización
- **Tecnologías**: React 18, TypeScript, Vite, Tailwind CSS
- **Features**: Autenticación, dashboard, gestión de usuarios, visualización de datos

## 🛠️ Configuración de la Base de Datos

### SQL Server (Local)
```bash
# Configuración en backend/.env
DATABASE_URL="sqlserver://localhost;database=UrbiaDb;integratedSecurity=true;trustServerCertificate=true;"
```

### Usuario Administrador
```
Email: jtadaym@unemi.edu.ec
Password: hola123..
Roles: ADMIN
```

## 🚀 Instalación y Ejecución

### 1. Instalar Dependencias

```bash
# Instalar dependencias de todos los proyectos
npm install

# O instalar individualmente:
cd shared && npm install
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### 2. Configurar Base de Datos

```bash
# Generar y aplicar migraciones
cd backend
npx prisma generate
npx prisma db push

# Ejecutar seed para datos iniciales
python seed.py
```

### 3. Ejecutar Proyectos

```bash
# Backend (Puerto 8000)
cd backend
uvicorn main:app --reload

# Frontend (Puerto 5173)
cd frontend
npm run dev

# Builds de producción
npm run build:all
```

## 📋 Funcionalidades Principales

### 🔐 Autenticación y Usuarios
- Sistema multi-rol (ADMIN, OPERATOR, VIEWER)
- JWT con refresh tokens
- Gestión de permisos granulares

### 🚗 Análisis de Tráfico
- Carga y procesamiento de videos
- Detección de vehículos con OpenCV
- Conteo automático y clasificación
- Análisis de patrones de tráfico

### 🔍 Detección de Placas
- Detección con YOLO (You Only Look Once)
- OCR para lectura de caracteres
- Búsqueda y filtrado de placas
- Historial de detecciones

### 📊 Predicciones ML
- Modelos con scikit-learn
- Predicción de densidad de tráfico
- Análisis de patrones temporales
- Alertas automáticas

### 📱 Notificaciones
- Email con SendGrid
- WhatsApp con Twilio
- Notificaciones web en tiempo real
- Templates personalizables

## 🔌 API Endpoints

### Autenticación
```
POST /api/auth/login          # Login
POST /api/auth/register       # Registro
GET  /api/auth/profile        # Perfil actual
POST /api/auth/logout         # Logout
```

### Análisis de Tráfico
```
GET    /api/traffic/analysis           # Listar análisis
POST   /api/traffic/analysis           # Crear análisis
GET    /api/traffic/analysis/{id}      # Obtener análisis
POST   /api/traffic/upload-video/{id}  # Subir video
POST   /api/traffic/analyze/{id}       # Iniciar análisis
GET    /api/traffic/predictions        # Predicciones
GET    /api/traffic/statistics         # Estadísticas
```

### Detección de Placas
```
GET    /api/plates/detections          # Listar detecciones
GET    /api/plates/search              # Buscar placas
GET    /api/plates/history/{plate}     # Historial de placa
POST   /api/plates/verify/{id}         # Verificar detección
```

### Gestión de Usuarios
```
GET    /api/users                      # Listar usuarios
POST   /api/users                      # Crear usuario
PUT    /api/users/{id}                 # Actualizar usuario
GET    /api/users/roles                # Listar roles
```

## 💾 Estructura de Base de Datos

### Tablas Principales
- **User**: Usuarios del sistema
- **UserRole**: Roles de usuarios (ADMIN, OPERATOR, VIEWER)
- **TrafficAnalysis**: Análisis de tráfico realizados
- **PlateDetection**: Detecciones de placas
- **Notification**: Sistema de notificaciones

### Relaciones
- Usuario puede tener múltiples roles (N:M)
- Análisis tiene múltiples detecciones (1:N)
- Usuario crea múltiples análisis (1:N)

## 🔧 Configuración del Entorno

### Variables de Entorno (Backend)
```env
DATABASE_URL=sqlserver://localhost;database=UrbiaDb;integratedSecurity=true;trustServerCertificate=true;
SECRET_KEY=your-secret-key
SENDGRID_API_KEY=your-sendgrid-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

### Scripts Disponibles
```bash
npm run build:shared     # Build shared library
npm run build:frontend   # Build frontend
npm run build:all        # Build todo
npm run dev:frontend     # Dev frontend
npm run dev:backend      # Dev backend (Python)
```

## 📸 Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno para Python
- **Prisma**: ORM type-safe para base de datos
- **OpenCV**: Procesamiento de imágenes y video
- **YOLO**: Detección de objetos en tiempo real
- **scikit-learn**: Machine Learning y predicciones
- **Celery + Redis**: Tareas asíncronas
- **SendGrid**: Envío de emails
- **Twilio**: Mensajería WhatsApp

### Frontend
- **React 18**: Librería UI con hooks modernos
- **TypeScript**: Tipado estático para JavaScript
- **Vite**: Build tool rápido y moderno
- **Tailwind CSS**: Framework CSS utility-first
- **React Router**: Routing client-side
- **Axios**: Cliente HTTP con interceptores

### Shared
- **TypeScript**: Tipos compartidos entre proyectos
- **Zod**: Validación de esquemas type-safe
- **tsup**: Bundle para librerías TypeScript

## 🎯 Flujo de Trabajo

1. **Usuario se autentica** en el dashboard web
2. **Sube un video** de tráfico para análisis
3. **Sistema procesa** el video con OpenCV y YOLO
4. **Detecta vehículos y placas** automáticamente
5. **Genera estadísticas** y métricas de tráfico
6. **Crea predicciones** usando modelos ML
7. **Envía notificaciones** según configuración

## 🔒 Seguridad

- Autenticación JWT con refresh tokens
- Validación de datos con Zod schemas
- Sanitización de inputs
- Rate limiting en API
- CORS configurado correctamente
- Roles y permisos granulares

## 📈 Escalabilidad

- Arquitectura modular y desacoplada
- Procesamiento asíncrono con Celery
- Cache con Redis
- API RESTful stateless
- Frontend SPA optimizado

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es privado y está destinado para uso interno de la organización.

## 📞 Contacto

Para dudas o soporte técnico, contactar al equipo de desarrollo.

---

⚡ **Desarrollado con**: FastAPI + React + TypeScript + Machine Learning