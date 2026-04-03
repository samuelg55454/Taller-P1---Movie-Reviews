import os
from pathlib import Path

import numpy as np
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    help = "Compare two movies and optionally a prompt using OpenAI embeddings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--movie1",
            type=str,
            default="Carmencita",
            help="Title of first movie",
        )
        parser.add_argument(
            "--movie2",
            type=str,
            default="Pauvre Pierrot",
            help="Title of second movie",
        )
        parser.add_argument(
            "--prompt",
            type=str,
            default="película sobre la Segunda Guerra Mundial",
            help="Search prompt text to compare against movie descriptions",
        )

    def handle(self, *args, **kwargs):
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

        movie1_title = kwargs["movie1"]
        movie2_title = kwargs["movie2"]
        prompt = kwargs["prompt"]

        try:
            movie1 = Movie.objects.get(title=movie1_title)
            movie2 = Movie.objects.get(title=movie2_title)
        except Movie.DoesNotExist as e:
            self.stderr.write(self.style.ERROR(f"Movie not found: {e}"))
            return

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small",
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        emb1 = get_embedding(movie1.description)
        emb2 = get_embedding(movie2.description)

        similarity = cosine_similarity(emb1, emb2)
        self.stdout.write("=== Selected movies and generated search prompt ===")
        self.stdout.write(f"Movie 1: {movie1.title}")
        self.stdout.write(f"Movie 2: {movie2.title}")
        self.stdout.write(f"Generated prompt: {prompt}")
        self.stdout.write("")
        self.stdout.write("=== Cosine similarity results ===")
        self.stdout.write(
            f"Similarity between '{movie1.title}' and '{movie2.title}': {similarity:.4f}"
        )

        prompt_emb = get_embedding(prompt)

        sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
        sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

        self.stdout.write(
            f"Similarity prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}"
        )
        self.stdout.write(
            f"Similarity prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}"
        )
