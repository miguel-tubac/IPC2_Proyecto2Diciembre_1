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


@csrf_exempt
def eliminar_factura(request):
    template_name = "facturas/menu_facturas_eliminar.html"
    context = {}

    if request.method == 'POST':
        correlativo = request.POST.get('id')
        archivo_xml_path = os.path.join(
            settings.BASE_DIR, 'app', 'Factura', 'datos', 'facturas.xml')
        print(correlativo)
        try:
            tree = ET.parse(archivo_xml_path)
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element('Facturas')
            tree = ET.ElementTree(root)

        elemento_a_eliminar = root.find(f'.//factura[@correlativo="{correlativo}"]')
        print(elemento_a_eliminar)
        if elemento_a_eliminar is not None:
            root.remove(elemento_a_eliminar)
            tree = ET.ElementTree(root)
            tree_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
            formatted_xml = minidom_parse_string(tree_str)

            with open(archivo_xml_path, 'wb') as file:
                file.write(formatted_xml.encode('utf-8'))

            context['success'] = True
            context['message'] = 'Factura eliminada exitosamente'
        else:
            context['success'] = False
            context['message'] = 'Factura no encontrada'

    return render(request, template_name, context)

@csrf_exempt
def listar_facturas(request):
    # Cargar la plantilla
    template = loader.get_template("facturas/menu_facturas_listar.html")

    # Listas para almacenar datos de facturas y productos
    lst_facturas = []

    archivo_facturas_path = os.path.join(
        settings.BASE_DIR, 'app', 'Factura', 'datos', 'facturas.xml')

    try:
        # Cargar datos de facturas
        tree_facturas = ET.parse(archivo_facturas_path)
        root_facturas = tree_facturas.getroot()
        
        for factura in root_facturas.findall("factura"):
            # Extraer datos relevantes de la factura
            numero = factura.get("correlativo")
            fecha = factura.find("fecha").text
            cliente_nit = factura.find("cliente").get("nit")
            cliente_nombre = factura.find("cliente/nombre").text
            cliente_direccion = factura.find("cliente/direccion").text
            total_factura = factura.find("totalfactura").text

            # Extraer datos de productos dentro de la factura
            lst_productos = []
            for producto in factura.findall("producto"):
                producto_id = producto.get("id")
                producto_nombre = producto.find("nombre").text
                producto_descripcion = producto.find("descripcion").text
                producto_cantidad = producto.find("cantidad").text
                producto_stock = producto.find("stock").text
                producto_precio_unitario = producto.find("preciounitario").text
                producto_total = producto.find("total").text
                producto_data = {
                    "id": producto_id,
                    "nombre": producto_nombre,
                    "descripcion": producto_descripcion,
                    "cantidad": producto_cantidad,
                    "stock": producto_stock,
                    "precio_unitario": producto_precio_unitario,
                    "total": producto_total
                }
                lst_productos.append(producto_data)

            # Crear un diccionario para la factura y agregar la lista de productos
            factura_data = {
                "numero": numero,
                "fecha": fecha,
                "cliente_nit": cliente_nit,
                "cliente_nombre": cliente_nombre,
                "cliente_direccion": cliente_direccion,
                "total_factura": total_factura,
                "lst_productos": lst_productos  # Agregar la lista de productos a los datos de la factura
            }
            lst_facturas.append(factura_data)

    except FileNotFoundError:
        root_facturas = ET.Element('Facturas')
        tree_facturas = ET.ElementTree(root_facturas)

    # Renderizar la plantilla con los datos organizados
    context = {'lst_facturas': lst_facturas}
    return render(request, "facturas/menu_facturas_listar.html", context)