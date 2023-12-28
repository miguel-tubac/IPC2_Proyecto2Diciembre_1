from django.shortcuts import render, redirect
from xml.dom import minidom
import os
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from collections import defaultdict

from django.views.decorators.csrf import csrf_exempt

# Create your views here.


@csrf_exempt
def inicio(request):
    # Procesar el XML y obtener datos para las gráficas
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'Factura', 'datos', 'facturas.xml')
    top_clientes, top_productos = process_xml(archivo_xml_path)

    # Renderizar el template con los datos de las gráficas
    return render(request, 'dashboard.html', {'top_clientes': top_clientes, 'top_productos': top_productos})


def process_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Diccionarios para almacenar datos de clientes y productos
    clientes_data = defaultdict(float)
    productos_data = defaultdict(int)

    # Procesar facturas
    for factura_element in root.findall('.//factura'):
        nit_cliente = factura_element.find('.//cliente').get('nit')
        total_factura = float(factura_element.find('totalfactura').text)

        # Actualizar datos de clientes
        clientes_data[nit_cliente] += total_factura

        # Actualizar datos de productos
        for producto_element in factura_element.findall('.//producto'):
            producto_id = producto_element.get('id')
            cantidad = int(producto_element.find('cantidad').text)
            productos_data[producto_id] += cantidad
    # Obtener los mejores clientes (top 5)
    top_clientes = dict(sorted(clientes_data.items(),
                        key=lambda item: item[1], reverse=True)[:5])

    # Obtener los productos más vendidos (top 5)
    top_productos = dict(sorted(productos_data.items(),
                         key=lambda item: item[1], reverse=True)[:5])
    return top_clientes, top_productos


def clientes(request):
    # cargamos el html en un template:
    objetoTemplate = loader.get_template("menu_clientes.html")
    html = objetoTemplate.render()
    return HttpResponse(html)


@csrf_exempt
def clientes_crear(request):
    template_name = "menu_clientes_crear.html"
    context = {}

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        nit_cliente = request.POST.get('nit')
        direccion = request.POST.get('direccion')

        archivo_xml_path = os.path.join(
            settings.BASE_DIR, 'app', 'PuntoDeVenta', 'datos', 'clientes.xml')
        try:
            tree = ET.parse(archivo_xml_path)
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element('Clientes')
            tree = ET.ElementTree(root)

        # Verificar si el NIT ya existe
        elemento_existente = root.find(f'.//cliente[@nit="{nit_cliente}"]')
        if elemento_existente is not None:
            context['success'] = False
            context['message'] = 'Error: El cliente con este NIT ya existe.'
        else:
            nuevo_elemento = ET.Element('cliente')
            nuevo_elemento.attrib['nit'] = nit_cliente
            ET.SubElement(nuevo_elemento, 'nombre').text = nombre
            ET.SubElement(nuevo_elemento, 'direccion').text = direccion
            root.append(nuevo_elemento)

            tree = ET.ElementTree(root)
            tree_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
            formatted_xml = minidom_parse_string(tree_str)

            with open(archivo_xml_path, 'wb') as file:
                file.write(formatted_xml.encode('utf-8'))

            context['success'] = True
            context['message'] = 'Cliente creado exitosamente'

    return render(request, template_name, context)


@csrf_exempt
def clientes_listar(request):
    # Cargar el template
    template = loader.get_template("menu_clientes_listar.html")

    lst_clientes = []
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'PuntoDeVenta', 'datos', 'clientes.xml')

    try:
        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()
        for cliente in root.findall("cliente"):
            nit_cliente = cliente.get("nit")
            nombre_cliente = cliente.find("nombre").text
            direccion = cliente.find("direccion").text
            cliente_listar = (nit_cliente, nombre_cliente, direccion)
            lst_clientes.append(cliente_listar)
    except FileNotFoundError:
        root = ET.Element('Clientes')
        tree = ET.ElementTree(root)

    # Usar render en lugar de HttpResponse para cargar el template y pasar el contexto
    context = {"lst_clientes": lst_clientes}
    return render(request, "menu_clientes_listar.html", context)


@csrf_exempt
def clientes_eliminar(request):
    template_name = "menu_clientes_eliminar.html"
    context = {}

    if request.method == 'POST':
        nit_cliente = request.POST.get('nit')
        archivo_xml_path = os.path.join(
            settings.BASE_DIR, 'app', 'PuntoDeVenta', 'datos', 'clientes.xml')
        try:
            tree = ET.parse(archivo_xml_path)
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element('Clientes')
            tree = ET.ElementTree(root)

        elemento_a_eliminar = root.find(f'.//cliente[@nit="{nit_cliente}"]')

        if elemento_a_eliminar is not None:
            root.remove(elemento_a_eliminar)
            tree = ET.ElementTree(root)
            tree_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
            formatted_xml = minidom_parse_string(tree_str)

            with open(archivo_xml_path, 'wb') as file:
                file.write(formatted_xml.encode('utf-8'))

            context['success'] = True
            context['message'] = 'Cliente eliminado exitosamente'
        else:
            context['success'] = False
            context['message'] = 'Cliente no encontrado'

    return render(request, template_name, context)


def minidom_parse_string(string):
    """Evita la adición de espacios innecesarios por minidom."""
    dom = minidom.parseString(string)
    # Eliminar espacios en blanco adicionales
    xml_string = dom.toprettyxml(indent="    ")
    cleaned_xml_string = '\n'.join(
        [line for line in xml_string.split('\n') if line.strip()])
    return cleaned_xml_string


@csrf_exempt
def clientes_editar(request):
    # Cargar el template
    template = loader.get_template("menu_clientes_editar.html")

    lst_clientes = []
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'PuntoDeVenta', 'datos', 'clientes.xml')

    try:
        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()
        for cliente in root.findall("cliente"):
            nit_cliente = cliente.get("nit")
            nombre_cliente = cliente.find("nombre").text
            direccion = cliente.find("direccion").text
            cliente_listar = (nit_cliente, nombre_cliente, direccion)
            lst_clientes.append(cliente_listar)
    except FileNotFoundError:
        root = ET.Element('Clientes')
        tree = ET.ElementTree(root)

    # Usar render en lugar de HttpResponse para cargar el template y pasar el contexto
    context = {"lst_clientes": lst_clientes}
    return render(request, "menu_clientes_editar.html", context)


def obtener_cliente_por_nit(nit):
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'PuntoDeVenta', 'datos', 'clientes.xml')

    try:
        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()
    except FileNotFoundError:
        # Si el archivo no existe, retorna None
        return None

    # Buscar el elemento con el NIT especificado
    cliente_element = root.find(f'.//cliente[@nit="{nit}"]')

    if cliente_element is not None:
        # Obtener los datos del cliente
        nombre = cliente_element.find('nombre').text
        direccion = cliente_element.find('direccion').text

        # Crear y retornar un diccionario con los datos del cliente
        cliente = {'nit': nit, 'nombre': nombre, 'direccion': direccion}
        return cliente
    else:
        # Si no se encuentra el cliente, retorna None
        return None


def editar_cliente(request, nit):

    cliente = obtener_cliente_por_nit(nit)

    if cliente:
        # Renderizar el formulario de edición del cliente con los datos existentes
        context = {'cliente': cliente}
        return render(request, 'editar_cliente.html', context)
    else:
        # Manejar el caso en el que el cliente no se encuentra
        return render(request, 'menu_clientes_crear.html')


def guardar_cambios_cliente(request, nit):
    if request.method == 'POST':
        # Obtener los datos del formulario y guardar los cambios en el archivo XML
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')

        archivo_xml_path = os.path.join(
            settings.BASE_DIR, 'app', 'PuntoDeVenta', 'datos', 'clientes.xml')

        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()

        # Buscar y actualizar el elemento con el NIT especificado
        for cliente_element in root.findall('.//cliente'):
            if cliente_element.get('nit') == nit:
                cliente_element.find('nombre').text = nombre
                cliente_element.find('direccion').text = direccion
                break

        # Guardar los cambios en el archivo XML
        tree.write(archivo_xml_path)

    # Redirigir de nuevo a la página de listado de clientes
    return redirect('clientes_listar')
