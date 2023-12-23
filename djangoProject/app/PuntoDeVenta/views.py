from django.shortcuts import render
from xml.dom import minidom
import os
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.template import loader
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def incio(request):
    # cargamos el html en un template:
    objetoTemplate = loader.get_template("menu_template.html")
    html = objetoTemplate.render()
    return HttpResponse(html)


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
