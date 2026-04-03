import re
import unicodedata
from pathlib import Path

from django.core.management.base import BaseCommand

from movie.models import Movie


class Command(BaseCommand):
    help = (
        "Update Movie.image from local files in media/movies/images "
        "(fallback: media/movie/images)."
    )

    def handle(self, *args, **kwargs):
        project_root = Path(__file__).resolve().parents[3]
        media_root = project_root / "media"
        candidate_dirs = [
            media_root / "movies" / "images",
            media_root / "movie" / "images",
        ]

        image_dir = next((d for d in candidate_dirs if d.exists()), None)
        if not image_dir:
            self.stderr.write(
                self.style.ERROR(
                    "Image folder not found. Expected one of: "
                    f"{candidate_dirs[0]} or {candidate_dirs[1]}"
                )
            )
            return

        allowed_ext = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        image_files = [
            p
            for p in image_dir.iterdir()
            if p.is_file() and p.suffix.lower() in allowed_ext
        ]
        if not image_files:
            self.stderr.write(self.style.ERROR(f"No image files found in: {image_dir}"))
            return

        index = {}
        for img in image_files:
            stem = img.stem
            variants = [stem]
            if stem.startswith("m_"):
                variants.append(stem[2:])
            for v in variants:
                key = self._normalize(v)
                if key and key not in index:
                    index[key] = img

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        updated = 0
        not_found = 0

        for movie in movies:
            key = self._normalize(movie.title)
            matched = index.get(key)

            if not matched:
                not_found += 1
                self.stderr.write(f"No image found for: {movie.title}")
                continue

            relative_to_media = matched.relative_to(media_root).as_posix()
            movie.image = relative_to_media
            movie.save(update_fields=["image"])
            updated += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated image for: {movie.title} -> {relative_to_media}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Updated: {updated} | Not found: {not_found} | Source folder: {image_dir}"
            )
        )

    def _normalize(self, value: str) -> str:
        text = unicodedata.normalize("NFKD", value)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.replace("_", " ").replace("-", " ").lower().strip()
        text = re.sub(r"[^a-z0-9 ]+", "", text)
        text = re.sub(r"\s+", " ", text)
        return text
