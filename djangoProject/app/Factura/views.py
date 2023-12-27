import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from xml.dom import minidom
import os
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def facturas(request):
    # cargamos el html en un template:
    objetoTemplate = loader.get_template("facturas/menu_facturas.html")
    html = objetoTemplate.render()
    return HttpResponse(html)


@csrf_exempt
def facturas_crear(request):
    template_name = "facturas/menu_facturas_crear.html"
    # Cargar el template
    lst_productos = []
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'Producto', 'datos', 'productos.xml')

    try:
        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()
        for producto in root.findall("producto"):
            id = producto.get("id")
            nombre = producto.find("nombre").text
            descripcion = producto.find("descripcion").text
            precio = producto.find("precio").text
            stock = producto.find("stock").text
            producto_listar = (id, nombre, descripcion, precio, stock)
            lst_productos.append(producto_listar)
    except FileNotFoundError:
        root = ET.Element('Clientes')
        tree = ET.ElementTree(root)

    # Usar render en lugar de HttpResponse para cargar el template y pasar el contexto
    context = {"lst_productos": lst_productos}

    return render(request, template_name, context)


@csrf_exempt
def procesar_pedido(request):
    if request.method == 'POST':
        datos_tabla = json.loads(request.body.decode('utf-8'))
        # Realizar operaciones con los datos, por ejemplo, imprimir en la consola
        print('Datos de la tabla:', datos_tabla)

        # Puedes realizar más operaciones aquí según tus necesidades

        # Devolver una respuesta JSON, por ejemplo, un mensaje de éxito
        return JsonResponse({'mensaje': 'Pedido procesado exitosamente'})
    else:
        return JsonResponse({'error': 'Método no permitido'})


def minidom_parse_string(string):
    """Evita la adición de espacios innecesarios por minidom."""
    dom = minidom.parseString(string)
    # Eliminar espacios en blanco adicionales
    xml_string = dom.toprettyxml(indent="    ")
    cleaned_xml_string = '\n'.join(
        [line for line in xml_string.split('\n') if line.strip()])
    return cleaned_xml_string
