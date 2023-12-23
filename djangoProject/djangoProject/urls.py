"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.PuntoDeVenta.views import incio, clientes, clientes_crear, clientes_eliminar, clientes_listar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', incio),
    path('clientes/', clientes, name='clientes'),
    path('clientes/crear/', clientes_crear, name='clientes_crear'),
    path('clientes/elimnar/', clientes_eliminar, name='clientes_eliminar'),
    path('clientes/listar/', clientes_listar, name='clientes_listar')
]
