from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings

class Command(BaseCommand):
    help = 'Создает админа из переменных окружения'

    def handle(self, *args, **kwargs):
        username = settings.DJANGO_SUPERUSER_USERNAME
        email = settings.DJANGO_SUPERUSER_EMAIL
        password = settings.DJANGO_SUPERUSER_PASSWORD

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Админ {username} успешно создан!'))
        else:
            u = User.objects.get(username=username)
            u.set_password(password)
            u.is_superuser = True
            u.is_staff = True
            u.save()
            self.stdout.write(self.style.SUCCESS(f'Пароль для {username} обновлен!'))