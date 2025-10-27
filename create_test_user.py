#!/usr/bin/env python
"""
Script para crear un usuario de prueba en la base de datos.
Ejecutar: python create_test_user.py
"""
import os
import django
import sys

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

# Credenciales del usuario de prueba
email = 'test@docente.uss.cl'
password = 'Test123456'
name = 'Usuario Prueba'

# Verificar si ya existe
if User.objects.filter(email=email).exists():
    print(f"⚠️  El usuario {email} ya existe")
    user = User.objects.get(email=email)
    # Actualizar contraseña
    user.password = make_password(password)
    user.save()
    print(f"✅ Contraseña actualizada para {email}")
else:
    # Crear usuario
    user = User.objects.create(
        username=email,
        email=email,
        password=make_password(password),
        first_name=name
    )
    print(f"✅ Usuario creado exitosamente:")
    print(f"   Email: {email}")
    print(f"   Contraseña: {password}")

print(f"\n📋 Detalles del usuario:")
print(f"   ID: {user.id}")
print(f"   Username: {user.username}")
print(f"   Email: {user.email}")
print(f"   Nombre: {user.first_name}")
