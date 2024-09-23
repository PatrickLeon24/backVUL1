from django.shortcuts import render
from django.http import *
# Create your views here.
def prueba(request):
    data = {
        'nombre': 'Juan'  # El nombre que quieras devolver
    }
    return JsonResponse(data)
