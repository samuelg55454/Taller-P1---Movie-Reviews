"""
Load movies from movies_initial.csv into the Movie model.
Run from project root: python manage.py load_movies_csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie


class Command(BaseCommand):
    help = 'Load movies from movies_initial.csv into the Movie model'

    def handle(self, *args, **kwargs):
        csv_path = os.path.join(settings.BASE_DIR, 'movies_initial.csv')
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(
                f'File not found: {csv_path}'
            ))
            return

        loaded = 0
        limit = 100

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                title = (row.get('title') or '').strip()
                if not title or Movie.objects.filter(title=title).exists():
                    continue

                year_val = row.get('year')
                if year_val and str(year_val).strip():
                    try:
                        year_val = int(float(year_val))
                    except (ValueError, TypeError):
                        year_val = None
                else:
                    year_val = None

                genre_val = row.get('genre') or ''
                if isinstance(genre_val, float) and str(genre_val) == 'nan':
                    genre_val = ''
                genre_val = str(genre_val).strip()[:100]

                plot_val = (row.get('plot') or row.get('fullplot') or '').strip()[:250]
                poster = (row.get('poster') or '').strip()
                url_val = poster if poster.startswith('http') else ''

                Movie.objects.create(
                    title=title,
                    description=plot_val or title,
                    image='movie/images/default.jpg',
                    url=url_val,
                    genre=genre_val,
                    year=year_val,
                )
                loaded += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully loaded {loaded} movies from CSV.'
        ))
