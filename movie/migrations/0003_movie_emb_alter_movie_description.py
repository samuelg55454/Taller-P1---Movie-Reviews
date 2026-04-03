# Generated manually for Taller IA P1

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0002_movie_genre_movie_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='emb',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='description',
            field=models.TextField(),
        ),
    ]
