from django.shortcuts import render

from django.http import HttpResponse
from django.template import  loader

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

def clientes_crear(request):
    # cargamos el html en un template:
    objetoTemplate = loader.get_template("menu_clientes_crear.html")
    html = objetoTemplate.render()
    return HttpResponse(html)

@csrf_exempt
def crear_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        nit = request.POST.get('nit')
        direccion = request.POST.get('direccion')

        # Imprimir los datos en la consola
        print("Nombre:", nombre)
        print("NIT:", nit)
        print("Dirección:", direccion)

        # Aquí puedes hacer lo que necesites con los datos, como guardarlos en la base de datos

    return render(request, 'menu_clientes_crear.html', context={})