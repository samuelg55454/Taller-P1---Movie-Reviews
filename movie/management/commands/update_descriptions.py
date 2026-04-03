import os
from pathlib import Path

from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    help = "Update movie descriptions using OpenAI API"

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

        def get_completion(prompt, model="gpt-3.5-turbo"):
            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content.strip()

        instruction = (
            "Vas a actuar como un aficionado del cine que sabe describir de forma clara, "
            "concisa y precisa cualquier película en menos de 200 palabras. La descripción "
            "debe incluir el género de la película y cualquier información adicional que sirva "
            "para crear un sistema de recomendación."
        )

        total = Movie.objects.count()
        self.stdout.write(f"Found {total} movies")

        movie = Movie.objects.order_by("pk").first()
        if not movie:
            self.stderr.write(self.style.ERROR("No movies in database."))
            return

        self.stdout.write(f"Processing (first movie by id): {movie.title}")
        try:
            prompt = (
                f"{instruction} "
                f"Vas a actualizar la descripción '{movie.description}' de la película '{movie.title}'."
            )

            print(f"Title: {movie.title}")
            print(f"Original Description: {movie.description}")

            updated_description = get_completion(prompt)

            print(f"Updated Description: {updated_description}")

            movie.description = updated_description
            movie.save()

            self.stdout.write(self.style.SUCCESS(f"Updated: {movie.title}"))

        except Exception as e:
            self.stderr.write(f"Failed for {movie.title}: {str(e)}")
