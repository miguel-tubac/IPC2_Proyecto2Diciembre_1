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
        print('Datos de la tabla:', datos_tabla)
        context = {}

        # Obtener datos generales
        nombre = datos_tabla['nombre']
        nit_cliente = datos_tabla['nit']
        direccion = datos_tabla['direccion']
        fecha = datos_tabla['fecha']
        array_productos = datos_tabla['array']

        archivo_xml_path = os.path.join(
            settings.BASE_DIR, 'app', 'Factura', 'datos', 'facturas.xml')

        try:
            tree = ET.parse(archivo_xml_path)
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element('Facturas')
            tree = ET.ElementTree(root)

        # Crear el elemento factura con correlativo
        correlativo = str(len(root.findall('.//factura')) + 1).zfill(2)
        nueva_factura = ET.Element('factura', correlativo=correlativo)

        # Crear el elemento cliente
        nuevo_cliente = ET.Element('cliente', nit=nit_cliente)
        ET.SubElement(nuevo_cliente, 'nombre').text = nombre
        ET.SubElement(nuevo_cliente, 'direccion').text = direccion
        nueva_factura.append(nuevo_cliente)

        # Crear el elemento fecha
        ET.SubElement(nueva_factura, 'fecha').text = fecha

        # Crear elementos de productos
    total_factura = 0
    for producto_data in array_productos:
        nuevo_producto = ET.Element('producto', id=producto_data[0])
        ET.SubElement(nuevo_producto, 'nombre').text = producto_data[1]
        ET.SubElement(nuevo_producto, 'descripcion').text = producto_data[2]
        ET.SubElement(nuevo_producto, 'cantidad').text = producto_data[3]
        ET.SubElement(nuevo_producto, 'stock').text = producto_data[4]
        ET.SubElement(nuevo_producto, 'preciounitario').text = producto_data[5]
        ET.SubElement(nuevo_producto, 'total').text = producto_data[6]
        nueva_factura.append(nuevo_producto)

        # Sumar el total del producto al total de la factura
        total_factura += float(producto_data[6])

        # Crear el elemento totalfactura y asignarle el total calculado
        ET.SubElement(nueva_factura, 'totalfactura').text = "{:.2f}".format(
            total_factura)

        root.append(nueva_factura)

        # Guardar el árbol XML de nuevo
        tree = ET.ElementTree(root)
        tree_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
        formatted_xml = minidom_parse_string(tree_str)

        with open(archivo_xml_path, 'wb') as file:
            file.write(formatted_xml.encode('utf-8'))

        context['success'] = True
        context['message'] = 'Factura creada exitosamente'

        return JsonResponse(context)
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
