import csv
from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

TABLES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    help = 'Import CSV Data to DB.SQLite3'

    def handle(self, *args, **kwargs):
        for model, file_csv in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{file_csv}',
                newline='',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file, delimiter=',')
                if file_csv == 'titles.csv':
                    for data in reader:
                        category = Category.objects.get(
                            pk=data.pop('category')
                        )
                        obj = model(
                            category=category,
                            **data
                        )
                        obj.save()
                elif file_csv in ['review.csv', 'comments.csv']:
                    for data in reader:
                        user = User.objects.get(pk=data.pop('author'))
                        obj = model(
                            author=user,
                            **data
                        )
                        obj.save()
                else:
                    model.objects.bulk_create(
                        [model(**data) for data in reader])
        self.stdout.write(self.style.SUCCESS('___Import data csv complete___'))
