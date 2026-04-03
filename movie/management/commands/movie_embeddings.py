import os
from pathlib import Path

import numpy as np
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    help = "Generate and store embeddings for all movies in the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Max number of movies to process (default: all)",
        )

    def handle(self, *args, **kwargs):
        limit = kwargs["limit"]
        project_root = Path(__file__).resolve().parents[3]
        load_dotenv(project_root / ".env")
        load_dotenv(project_root / "openAI.env")
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("openai_apikey")
        if not api_key:
            self.stderr.write(
                self.style.ERROR(
                    "Missing OpenAI API key. Set OPENAI_API_KEY in .env or openAI.env."
                )
            )
            return
        client = OpenAI(api_key=api_key)

        movies = Movie.objects.all().order_by("pk")
        if limit is not None:
            movies = movies[:limit]
        self.stdout.write(f"Processing {len(movies)} movie(s) in the database")

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small",
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        for movie in movies:
            try:
                emb = get_embedding(movie.description)
                movie.emb = emb.tobytes()
                movie.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Embedding stored for: {movie.title}")
                )
            except Exception as e:
                self.stderr.write(
                    f"Failed to generate embedding for {movie.title}: {e}"
                )

        self.stdout.write(
            self.style.SUCCESS("Finished generating embeddings for all movies")
        )
