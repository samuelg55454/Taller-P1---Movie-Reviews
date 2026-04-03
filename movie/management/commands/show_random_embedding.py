import random

import numpy as np
from django.core.management.base import BaseCommand

from movie.models import Movie


class Command(BaseCommand):
    help = (
        "Print the stored embedding vector for a random movie "
        "(run movie_embeddings first)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--preview",
            type=int,
            default=24,
            help="How many leading dimensions to print (default: 24)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Optional RNG seed for reproducible random movie choice",
        )

    def handle(self, *args, **kwargs):
        preview_n = kwargs["preview"]
        seed = kwargs["seed"]
        if seed is not None:
            random.seed(seed)

        qs = Movie.objects.exclude(emb__isnull=True).exclude(emb=b"")
        ids = list(qs.values_list("pk", flat=True))
        if not ids:
            self.stderr.write(
                self.style.ERROR(
                    "No movies with embeddings. Run: python manage.py movie_embeddings"
                )
            )
            return

        pk = random.choice(ids)
        movie = Movie.objects.get(pk=pk)
        arr = np.frombuffer(movie.emb, dtype=np.float32)

        self.stdout.write(f"Random movie: {movie.title}")
        self.stdout.write(f"Embedding shape: {arr.shape} (dtype=float32)")
        self.stdout.write(f"First {min(preview_n, len(arr))} values:")
        self.stdout.write(np.array2string(arr[:preview_n], precision=6, separator=", "))
