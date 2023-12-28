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
from app.PuntoDeVenta.views import incio, clientes, clientes_crear, clientes_eliminar, clientes_listar, clientes_editar, editar_cliente, guardar_cambios_cliente
from app.Producto.views import productos, productos_crear, productos_eliminar, productos_listar, productos_editar, editar_producto, guardar_cambios_producto
from app.Factura.views import facturas, facturas_crear, procesar_pedido, eliminar_factura, listar_facturas, facturas_editar, editar_factura, guardar_cambios_factura

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', incio, name='inicio'),
    path('clientes/', clientes, name='clientes'),
    path('clientes/crear/', clientes_crear, name='clientes_crear'),
    path('clientes/elimnar/', clientes_eliminar, name='clientes_eliminar'),
    path('clientes/listar/', clientes_listar, name='clientes_listar'),
    path('clientes/editar_cliente/', clientes_editar, name='clientes_editar'),
    path('clientes/editar_cliente/<str:nit>/',
         editar_cliente, name='editar_cliente'),
    path('guardar_cambios_cliente/<str:nit>/',
         guardar_cambios_cliente, name='guardar_cambios_cliente'),
    path('productos/', productos, name='productos'),
    path('productos/crear', productos_crear, name='productos_crear'),
    path('productos/eliminar', productos_eliminar, name='productos_eliminar'),
    path('productos/listar', productos_listar, name='productos_listar'),
    path('productos/editar_producto/', productos_editar, name='productos_editar'),
    path('productos/editar_producto/<str:producto_id>/',
         editar_producto, name='editar_producto'),
    path('guardar_cambios_producto/<str:producto_id>/',
         guardar_cambios_producto, name='guardar_cambios_producto'),
    path('facturas/', facturas, name='facturas'),
    path('facturas/crear', facturas_crear, name='facturas_crear'),
    path('procesar_pedido/', procesar_pedido, name='procesar_pedido'),
    path('facturas/eliminar/', eliminar_factura, name='eliminar_factura'),
    path('facturas/listar/', listar_facturas, name='listar_facturas'),
    path('facturas/editar/', facturas_editar, name='editar_facturas'),
    path('facturas/editar_producto/<str:correlativo>/',
         editar_factura, name='editar_factura'),
    path('guardar_cambios_factura/<str:correlativo>/',
         guardar_cambios_factura, name='guardar_cambios_factura'),
]
