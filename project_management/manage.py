#!/usr/bin/env python
import os
import sys
import psycopg2
from psycopg2 import OperationalError
from decouple import config
from django.core.management import execute_from_command_line

def create_database_if_not_exists():
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }
    db_name = DATABASES['default']['NAME']
    db_user = DATABASES['default']['USER']
    db_password = DATABASES['default']['PASSWORD']
    db_host = DATABASES['default']['HOST']
    db_port = DATABASES['default']['PORT']

    try:
        connection = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database='postgres'
        )
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        if not exists:
            print(f"Creando la base de datos '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Base de datos '{db_name}' creada exitosamente.")
        else:
            print(f"La base de datos '{db_name}' ya existe.")
        cursor.close()
        connection.close()
    except OperationalError as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        sys.exit(1)

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_management.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    create_database_if_not_exists()
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()