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
        total_factura = 0  # Variable para almacenar el total de la factura
        for producto_data in array_productos:
            nuevo_producto = ET.Element('producto', id=producto_data[0])
            ET.SubElement(nuevo_producto, 'nombre').text = producto_data[1]
            ET.SubElement(nuevo_producto,
                          'descripcion').text = producto_data[2]
            ET.SubElement(nuevo_producto, 'cantidad').text = producto_data[3]
            ET.SubElement(nuevo_producto, 'stock').text = producto_data[4]
            ET.SubElement(nuevo_producto,
                          'preciounitario').text = producto_data[5]
            ET.SubElement(nuevo_producto, 'total').text = producto_data[6]
            nueva_factura.append(nuevo_producto)

            # Sumar al total de la factura
            total_factura += float(producto_data[6])

        # Agregar la etiqueta totalfactura al final
        ET.SubElement(nueva_factura, 'totalfactura').text = str(total_factura)

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

        elemento_a_eliminar = root.find(
            f'.//factura[@correlativo="{correlativo}"]')
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
                # Agregar la lista de productos a los datos de la factura
                "lst_productos": lst_productos
            }
            lst_facturas.append(factura_data)

    except FileNotFoundError:
        root_facturas = ET.Element('Facturas')
        tree_facturas = ET.ElementTree(root_facturas)

    # Renderizar la plantilla con los datos organizados
    context = {'lst_facturas': lst_facturas}
    return render(request, "facturas/menu_facturas_listar.html", context)


@csrf_exempt
def facturas_editar(request):
    # Cargar la plantilla
    template = loader.get_template("facturas/menu_facturas_editar.html")

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
                # Agregar la lista de productos a los datos de la factura
                "lst_productos": lst_productos
            }
            lst_facturas.append(factura_data)

    except FileNotFoundError:
        root_facturas = ET.Element('Facturas')
        tree_facturas = ET.ElementTree(root_facturas)

    # Renderizar la plantilla con los datos organizados
    context = {'lst_facturas': lst_facturas}
    return render(request, "facturas/menu_facturas_editar.html", context)


def editar_factura(request, correlativo):

    factura = obtener_factura_por_correlativo(correlativo)
    clientes = obtener_lista_clientes()

    if factura:
        # Renderizar el formulario de edición de la factura con los datos existentes
        context = {'factura': factura, 'clientes': clientes}
        return render(request, 'facturas/editar_factura.html', context)
    else:
        # Manejar el caso en el que la factura no se encuentra
        return render(request, 'facturas/menu_facturas_crear.html')


def guardar_cambios_factura(request, correlativo):
    if request.method == 'POST':
        total_factura = 0
        # Obtener los datos del formulario y guardar los cambios en el archivo XML
        nit_cliente = request.POST.get('nit_cliente')
        fecha = request.POST.get('fecha')
        # total_factura = request.POST.get('totalfactura')

        archivo_xml_path_clientes = os.path.join(
            settings.BASE_DIR, 'app', 'PuntoDeVenta', 'datos', 'clientes.xml')
        archivo_xml_path_facturas = os.path.join(
            settings.BASE_DIR, 'app', 'Factura', 'datos', 'facturas.xml')

        tree_clientes = ET.parse(archivo_xml_path_clientes)
        root_clientes = tree_clientes.getroot()

        # Buscar el elemento cliente con el NIT especificado y obtener nombre y dirección
        cliente_element = root_clientes.find(
            f'.//cliente[@nit="{nit_cliente}"]')
        if cliente_element is not None:
            nombre_cliente = cliente_element.find('nombre').text
            direccion_cliente = cliente_element.find('direccion').text
        else:
            # Manejar el caso en que el cliente no se encuentra
            nombre_cliente = "Cliente no encontrado"
            direccion_cliente = "Dirección no encontrada"

        # Actualizar la factura
        tree_facturas = ET.parse(archivo_xml_path_facturas)
        root_facturas = tree_facturas.getroot()

        # Buscar y actualizar el elemento con el correlativo especificado
        for factura_element in root_facturas.findall('.//factura'):
            if factura_element.get('correlativo') == correlativo:
                # Actualizar datos del cliente
                cliente_element_factura = factura_element.find('.//cliente')
                cliente_element_factura.set('nit', nit_cliente)
                cliente_element_factura.find('nombre').text = nombre_cliente
                cliente_element_factura.find(
                    'direccion').text = direccion_cliente

                # Actualizar fecha
                factura_element.find('fecha').text = fecha

                # Actualizar productos
                for producto_element in factura_element.findall('.//producto'):
                    producto_id = producto_element.get('id')
                    nueva_cantidad = request.POST.get(
                        f'nueva_cantidad_{producto_id}')
                    producto_element.find('cantidad').text = nueva_cantidad

                    # Recalcular el total como la multiplicación de la cantidad por el precio unitario
                    preciounitario = float(
                        producto_element.find('preciounitario').text)
                    total = float(nueva_cantidad) * preciounitario
                    producto_element.find('total').text = str(total)
                    total_factura += total

                # Recalcular el total de la factura sumando los totales de todos los productos
                factura_element.find('totalfactura').text = str(total_factura)

        # Guardar los cambios en el archivo XML
        try:
            tree_facturas.write(archivo_xml_path_facturas)
        except Exception as e:
            print(f"Error al escribir en el archivo XML: {e}")

    # Redirigir de nuevo a la página de listado de facturas
    return redirect('listar_facturas')


def obtener_lista_clientes():
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'PuntoDeVenta', 'datos', 'clientes.xml')

    lista_clientes = []

    try:
        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()

        for cliente_element in root.findall('.//cliente'):
            nit = cliente_element.get('nit')
            nombre = cliente_element.find('nombre').text
            direccion = cliente_element.find('direccion').text

            cliente_info = {'nit': nit,
                            'nombre': nombre, 'direccion': direccion}
            lista_clientes.append(cliente_info)

    except FileNotFoundError:
        # Si el archivo no existe, puedes manejarlo de alguna manera, como devolver una lista vacía.
        pass

    return lista_clientes


def obtener_factura_por_correlativo(correlativo):
    archivo_xml_path = os.path.join(
        settings.BASE_DIR, 'app', 'Factura', 'datos', 'facturas.xml')

    try:
        tree = ET.parse(archivo_xml_path)
        root = tree.getroot()
    except FileNotFoundError:
        # Si el archivo no existe, retorna None
        return None

    # Buscar el elemento con el correlativo especificado
    factura_element = root.find(f'.//factura[@correlativo="{correlativo}"]')

    if factura_element is not None:
        # Obtener los datos de la factura
        nit_cliente = factura_element.find('.//cliente').get('nit')
        nombre_cliente = factura_element.find('.//cliente/nombre').text
        direccion_cliente = factura_element.find('.//cliente/direccion').text
        fecha = factura_element.find('fecha').text
        productos = []

        for producto_element in factura_element.findall('.//producto'):
            id_producto = producto_element.get('id')
            nombre_producto = producto_element.find('nombre').text
            descripcion_producto = producto_element.find('descripcion').text
            cantidad_producto = producto_element.find('cantidad').text
            stock_producto = producto_element.find('stock').text
            precio_unitario_producto = producto_element.find(
                'preciounitario').text
            total_producto = producto_element.find('total').text

            producto = {
                'id': id_producto,
                'nombre': nombre_producto,
                'descripcion': descripcion_producto,
                'cantidad': cantidad_producto,
                'stock': stock_producto,
                'precio_unitario': precio_unitario_producto,
                'total': total_producto
            }

            productos.append(producto)

        total_factura = factura_element.find('totalfactura').text

        # Crear y retornar un diccionario con los datos de la factura
        factura = {
            'correlativo': correlativo,
            'nit_cliente': nit_cliente,
            'nombre_cliente': nombre_cliente,
            'direccion_cliente': direccion_cliente,
            'fecha': fecha,
            'productos': productos,
            'total_factura': total_factura
        }

        return factura
    else:
        # Si no se encuentra la factura, retorna None
        return None
