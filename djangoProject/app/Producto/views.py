from django.shortcuts import render, redirect
from xml.dom import minidom
import os
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def productos(request):
    # cargamos el html en un template:
    objetoTemplate = loader.get_template("productos/menu_productos.html")
    html = objetoTemplate.render()
    return HttpResponse(html)


@csrf_exempt
def productos_crear(request):
    template_name = "productos/menu_productos_crear.html"
    context = {}
# Nombre, Descripción, Precio, Stock
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        id = request.POST.get('id')

        archivo_xml_path = os.path.join(
            settings.BASE_DIR, 'app', 'Producto', 'datos', 'productos.xml')
        try:
            tree = ET.parse(archivo_xml_path)
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element('Productos')
            tree = ET.ElementTree(root)

        # Verificar si el NIT ya existe
        elemento_existente = root.find(f'.//producto[@id="{id}"]')
        if elemento_existente is not None:
            context['success'] = False
            context['message'] = 'Error: El Producto con este Id ya existe.'
        else:
            nuevo_elemento = ET.Element('producto')
            nuevo_elemento.attrib['id'] = id
            ET.SubElement(nuevo_elemento, 'nombre').text = nombre
            ET.SubElement(nuevo_elemento, 'descripcion').text = descripcion
            ET.SubElement(nuevo_elemento, 'precio').text = precio
            ET.SubElement(nuevo_elemento, 'stock').text = stock
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
def productos_eliminar(request):
    template_name = "productos/menu_productos_eliminar.html"
    context = {}

    if request.method == 'POST':
        id = request.POST.get('id')
        archivo_xml_path = os.path.join(
            settings.BASE_DIR, 'app', 'Producto', 'datos', 'productos.xml')
        try:
            tree = ET.parse(archivo_xml_path)
            root = tree.getroot()
        except FileNotFoundError:
            root = ET.Element('Producto')
            tree = ET.ElementTree(root)

        elemento_a_eliminar = root.find(f'.//producto[@id="{id}"]')

        if elemento_a_eliminar is not None:
            root.remove(elemento_a_eliminar)
            tree = ET.ElementTree(root)
            tree_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
            formatted_xml = minidom_parse_string(tree_str)

            with open(archivo_xml_path, 'wb') as file:
                file.write(formatted_xml.encode('utf-8'))

            context['success'] = True
            context['message'] = 'Producto eliminado exitosamente'
        else:
            context['success'] = False
            context['message'] = 'Producto no encontrado'

    return render(request, template_name, context)

@csrf_exempt
def productos_listar(request):
    # Cargar el template
    template = loader.get_template("productos/menu_productos_listar.html")

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
            producto_listar = (id, nombre,descripcion, precio, stock)
            lst_productos.append(producto_listar)
    except FileNotFoundError:
        root = ET.Element('Clientes')
        tree = ET.ElementTree(root)

    # Usar render en lugar de HttpResponse para cargar el template y pasar el contexto
    context = {"lst_productos": lst_productos}
    return render(request, "productos/menu_productos_listar.html", context)


def minidom_parse_string(string):
    """Evita la adición de espacios innecesarios por minidom."""
    dom = minidom.parseString(string)
    # Eliminar espacios en blanco adicionales
    xml_string = dom.toprettyxml(indent="    ")
    cleaned_xml_string = '\n'.join(
        [line for line in xml_string.split('\n') if line.strip()])
    return cleaned_xml_string


@csrf_exempt
def productos_editar(request):
    # Cargar el template
    template = loader.get_template("productos/menu_productos_editar.html")

    lst_productos = []
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'Producto', 'datos', 'productos.xml')

    try:
        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()
        for producto in root.findall("producto"):
            id_producto = producto.get("id")
            nombre_producto = producto.find("nombre").text
            descripcion = producto.find("descripcion").text
            precio = producto.find("precio").text
            stock = producto.find("stock").text
            producto_listar = (id_producto, nombre_producto, descripcion, precio, stock)
            lst_productos.append(producto_listar)
    except FileNotFoundError:
        root = ET.Element('Productos')
        tree = ET.ElementTree(root)

    # Usar render en lugar de HttpResponse para cargar el template y pasar el contexto
    context = {"lst_productos": lst_productos}
    return render(request, "productos/menu_productos_editar.html", context)


def obtener_producto_por_id(producto_id):
    
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'Producto', 'datos', 'productos.xml')

    try:
        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()
    except FileNotFoundError:
        # Si el archivo no existe, retorna None
        return None

    # Buscar el elemento con el ID especificado
    producto_element = root.find(f'.//producto[@id="{producto_id}"]')
    print("product", producto_element)

    if producto_element is not None:
        # Obtener los datos del producto
        nombre = producto_element.find('nombre').text
        descripcion = producto_element.find('descripcion').text
        precio = producto_element.find('precio').text
        stock = producto_element.find('stock').text

        # Crear y retornar un diccionario con los datos del producto
        producto = {'id': producto_id, 'nombre': nombre, 'descripcion': descripcion, 'precio': precio, 'stock': stock}
        return producto
    else:
        # Si no se encuentra el producto, retorna None
        return None


def editar_producto(request, producto_id):

    producto = obtener_producto_por_id(producto_id)

    if producto:
        # Renderizar el formulario de edición del producto con los datos existentes
        context = {'producto': producto}
        return render(request, 'productos/editar_producto.html', context)
    else:
        # Manejar el caso en el que el producto no se encuentra
        return render(request, 'productos/menu_productos_crear.html')


def guardar_cambios_producto(request, producto_id):
    
    if request.method == 'POST':
        # Obtener los datos del formulario y guardar los cambios en el archivo XML
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')

        archivo_xml_path = os.path.join(
            settings.BASE_DIR, 'app', 'Producto', 'datos', 'productos.xml')

        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()

        # Buscar y actualizar el elemento con el ID especificado
        for producto_element in root.findall('.//producto'):
            if producto_element.get('id') == producto_id:
                
                producto_element.find('nombre').text = nombre
                producto_element.find('descripcion').text = descripcion
                producto_element.find('precio').text = precio
                producto_element.find('stock').text = stock
                break

        # Guardar los cambios en el archivo XML
        tree.write(archivo_xml_path)

    # Redirigir de nuevo a la página de listado de productos
    return redirect('productos_listar')