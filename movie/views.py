from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie

# Create your views here.

def home(request):
    # código HTML en views :(
    # return HttpResponse('<h1>Welcome to Home Page</h1>')
    
    #uso de plantilla sin parámetros
    #return render(request, 'home.html')

    # uso de plantilla con parámetros
    #return render(request, 'home.html', {'name':'Paola Vallejo'})

    # TODO: Obtener el término de búsqueda desde request.GET (parámetro 'searchMovie')
    # TODO: Si hay término de búsqueda, filtrar películas por título (title__icontains)
    # TODO: Si no hay búsqueda, listar todas las películas con Movie.objects.all()
    # TODO: Pasar searchTerm y movies al template en el return
    movies = Movie.objects.all()  # temporal: quitar y usar la lógica anterior
    return render(request, 'home.html', {'movies': movies})



 # Función para 'About'
def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
   
    #uso de plantilla sin parámetros
    return render(request, 'about.html')