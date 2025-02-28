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

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd project_management
Crear un entorno virtual:
bash
Ajuste
Copiar
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Instalar dependencias:
bash
Ajuste
Copiar
pip install -r requirements.txt
Configurar variables de entorno: Crea un archivo .env en la raíz del proyecto con el siguiente contenido:
text
Ajuste
Copiar
DB_NAME=project_management_db
DB_USER=postgres
DB_PASSWORD=postgresql
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=<TU_CLAVE_SECRETA>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
Genera una SECRET_KEY segura con:
python
Ajuste
Copiar
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
Configurar la base de datos: Asegúrate de que PostgreSQL esté corriendo y que el usuario y la base de datos especificados en .env existan. El archivo manage.py creará la base de datos automáticamente si no existe.
Aplicar migraciones:
bash
Ajuste
Copiar
python manage.py migrate
Crear un superusuario:
bash
Ajuste
Copiar
python manage.py createsuperuser
Iniciar el servidor:
bash
Ajuste
Copiar
python manage.py runserver
Accede a la aplicación en http://127.0.0.1:8000/.
Uso
Inicio de sesión: Usa las credenciales del superusuario o crea usuarios desde /usuarios/crear/ (requiere permisos de administrador).
Proyectos: Gestiona proyectos desde / (lista de proyectos).
Grupos: Crea y asigna usuarios a grupos desde /grupos/crear/ o /grupos/gestionar/.
Tareas: Añade y edita tareas dentro de cada proyecto.
Chat: Usa la pestaña en la esquina inferior derecha para mensajes privados.
Notificaciones: Revisa alertas en /notificaciones/.
Estructura del proyecto
manage.py: Punto de entrada para comandos Django, incluye creación automática de la base de datos PostgreSQL.
core/: Aplicación principal:
migrations/: Historial de cambios en la base de datos.
templates/core/: Plantillas HTML para cada funcionalidad.
base.html: Plantilla base con barra de navegación y chat emergente.
admin.py: Registro de modelos en el admin.
context_processors.py: Proporciona is_admin y notificaciones_no_leidas.
forms.py: Formularios personalizados para proyectos, tareas, grupos, etc.
models.py: Modelos de la base de datos (Proyecto, Grupo, PerfilProyecto, etc.).
views.py: Lógica de las vistas con mensajería, permisos y gestión.
urls.py: Rutas de la aplicación.
project_management/: Configuración del proyecto (settings, URLs).
Créditos
Desarrollado con la asistencia de Grok, creado por xAI, quien proporcionó orientación técnica, optimizaciones y soluciones a lo largo del proyecto.
