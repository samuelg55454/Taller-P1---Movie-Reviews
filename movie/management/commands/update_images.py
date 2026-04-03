import os
import re
from pathlib import Path

import requests
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    help = "Generate images with OpenAI and update movie image field"

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
        images_folder = "media/movie/images/"
        os.makedirs(images_folder, exist_ok=True)

        total = Movie.objects.count()
        self.stdout.write(f"Found {total} movies")

        movie = Movie.objects.order_by("pk").first()
        if not movie:
            self.stderr.write(self.style.ERROR("No movies in database."))
            return

        try:
            image_relative_path = self.generate_and_download_image(
                client, movie.title, images_folder
            )
            movie.image = image_relative_path
            movie.save()
            self.stdout.write(
                self.style.SUCCESS(f"Saved and updated image for: {movie.title}")
            )

        except Exception as e:
            self.stderr.write(f"Failed for {movie.title}: {e}")

        self.stdout.write(
            self.style.SUCCESS("Process finished (only first movie updated).")
        )

    def generate_and_download_image(self, client, movie_title, save_folder):
        prompt = f"Movie poster of {movie_title}"

        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="256x256",
            n=1,
        )
        image_url = response.data[0].url

        safe_stem = re.sub(r"[^\w\-]+", "_", movie_title, flags=re.UNICODE)[:80]
        image_filename = f"m_{safe_stem}.png"
        image_path_full = os.path.join(save_folder, image_filename)

        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        with open(image_path_full, "wb") as f:
            f.write(image_response.content)

        return os.path.join("movie/images", image_filename)
