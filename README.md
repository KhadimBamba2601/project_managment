README.md

# Gestión Empresarial - Project Management

**Gestión Empresarial** es una aplicación web desarrollada con Django para la gestión de proyectos, tareas, grupos de usuarios y mensajería privada dentro de una empresa. Permite a los usuarios crear proyectos, asignar tareas, organizar equipos en grupos, comunicarse mediante un chat integrado y recibir notificaciones en tiempo real, todo con una interfaz amigable basada en Bootstrap.

## Características principales
- **Gestión de proyectos:** Crear, editar y eliminar proyectos con fechas de inicio y fin.
- **Tareas:** Asignar tareas a usuarios dentro de proyectos, con estados (pendiente, en progreso, completada).
- **Grupos:** Organizar usuarios en grupos asociados a proyectos, con roles (administrador, miembro, invitado).
- **Mensajería privada:** Chat emergente en la esquina inferior derecha para comunicación entre usuarios, con soporte para mensajes sin proyecto asociado.
- **Notificaciones:** Alertas en tiempo real para tareas asignadas, mensajes recibidos y cambios en proyectos.
- **Seguridad:** Protección contra ataques de fuerza bruta con `django-axes`, variables de entorno para configuraciones sensibles y permisos basados en roles.
- **Interfaz:** Diseño responsive con Bootstrap y Font Awesome para una experiencia visual atractiva.

## Requisitos
- Python 3.8+
- PostgreSQL
- Dependencias listadas en `requirements.txt`

## Instalación

**Clonar el repositorio:**
   
   -git clone <URL_DEL_REPOSITORIO>
   -cd project_management
**Crear un entorno virtual:** <br>

   -python -m venv venv<br>
source venv/bin/activate  # En Windows: venv\Scripts\activate<br>
**Instalar dependencias:**<br>
   -pip install -r requirements.txt<br>
**Configurar variables de entorno:** Crea un archivo .env en la raíz del proyecto con el siguiente contenido:<br>

DB_NAME=project_management_db<br>
DB_USER=postgres (por defecto)<br>
DB_PASSWORD= (crea una contraseña)<br>
DB_HOST=localhost<br>
DB_PORT=5432<br>
SECRET_KEY=<TU_CLAVE_SECRETA><br>
DEBUG=True (en entorno de producción)<br>
ALLOWED_HOSTS=localhost,127.0.0.1<br>
**Genera una SECRET_KEY segura con:**<br>

   -from django.core.management.utils import get_random_secret_key<br>
   -print(get_random_secret_key())<br>
**Configurar la base de datos:**
Asegúrate de que PostgreSQL esté corriendo y que el usuario y la base de datos especificados en .env existan. El archivo manage.py creará la base de datos automáticamente si no existe.<br>
**Aplicar migraciones:**<br>
   -python manage.py migrate
**Crear un superusuario:**
   -python manage.py createsuperuser
**Iniciar el servidor:**
   -python manage.py runserver<br>
**Accede a la aplicación en http://127.0.0.1:8000/.**
## Uso
Inicio de sesión: Usa las credenciales del superusuario o crea usuarios desde /usuarios/crear/ (requiere permisos de administrador).<br>
Proyectos: Gestiona proyectos desde / (lista de proyectos).<br>
Grupos: Crea y asigna usuarios a grupos desde /grupos/crear/ o /grupos/gestionar/.<br>
Tareas: Añade y edita tareas dentro de cada proyecto.<br>
Chat: Usa la pestaña en la esquina inferior derecha para mensajes privados.<br>
Notificaciones: Revisa alertas en /notificaciones/.<br>
## Estructura del proyecto
manage.py: Punto de entrada para comandos Django, incluye creación automática de la base de datos PostgreSQL.<br>
core/: Aplicación principal:<br>
migrations/: Historial de cambios en la base de datos.<br>
templates/core/: Plantillas HTML para cada funcionalidad.<br>
base.html: Plantilla base con barra de navegación y chat emergente.<br>
admin.py: Registro de modelos en el admin.<br>
context_processors.py: Proporciona is_admin y notificaciones_no_leidas.<br>
forms.py: Formularios personalizados para proyectos, tareas, grupos, etc.<br>
models.py: Modelos de la base de datos (Proyecto, Grupo, PerfilProyecto, etc.).<br>
views.py: Lógica de las vistas con mensajería, permisos y gestión.<br>
urls.py: Rutas de la aplicación.<br>
project_management/: Configuración del proyecto (settings, URLs).<br>
**Créditos**
Desarrollado con la asistencia de Grok, creado por xAI, quien proporcionó orientación técnica, optimizaciones y soluciones a lo largo del proyecto.<br>
