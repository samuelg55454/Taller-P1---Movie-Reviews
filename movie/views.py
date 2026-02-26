import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count

from .models import Movie

NEWS_ITEMS = [
    {'title': 'Cannes Film Festival 2025 lineup announced', 'date': '2025-04', 'summary': 'The official selection includes 21 films in competition. New works from Coppola, Larraín and several first-time directors will premiere on the Croisette.'},
    {'title': 'Oscar eligibility rules updated for streaming releases', 'date': '2025-02', 'summary': 'The Academy has revised theatrical release requirements. Films with shorter exclusive cinema runs may still qualify if they meet new criteria.'},
    {'title': 'Restored silent classics to tour US cinemas', 'date': '2025-03', 'summary': 'A series of newly restored early cinema titles, with live orchestral accompaniment, will screen in over 50 cities starting next month.'},
    {'title': 'European film funds report record production levels', 'date': '2025-01', 'summary': 'Co-production and regional incentives have driven a new high in feature films greenlit across France, Germany and Italy.'},
    {'title': 'Documentary about film preservation wins audience award', 'date': '2025-02', 'summary': 'Sundance audience favourite highlights the work of archives saving nitrate and deteriorating film stock worldwide.'},
]

def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {
        'searchTerm': searchTerm,
        'movies': movies,
    })


def statistics(request):
    total_movies = Movie.objects.count()
    by_year = list(
        Movie.objects.filter(year__isnull=False)
        .values('year')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    by_genre = list(
        Movie.objects.exclude(genre='')
        .values('genre')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    return render(request, 'statistics.html', {
        'total_movies': total_movies,
        'by_year': by_year,
        'by_genre': by_genre,
        'by_year_json': json.dumps([{'year': r['year'], 'count': r['count']} for r in by_year]),
        'by_genre_json': json.dumps([{'genre': r['genre'][:30], 'count': r['count']} for r in by_genre]),
    })


def news(request):
    return render(request, 'news.html', {'news_items': NEWS_ITEMS})


def movie_detail(request, pk):
    """Vista de detalle de una película."""
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'movie_detail.html', {'movie': movie})


 # Función para 'About'
def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
   
    #uso de plantilla sin parámetros
    return render(request, 'about.html')