from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea els usuaris de prova: alumne, empresa i admin'

    def handle(self, *args, **options):
        with transaction.atomic():
            self._create_alumne()
            self._create_empresa()
            self._create_admin()
        self.stdout.write(self.style.SUCCESS('✅ Usuaris de prova creats correctament'))

    def _create_alumne(self):
        from core.models import PerfilAlumno
        username = 'alumne'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'⚠️  L\'usuari "{username}" ja existeix, s\'omet'))
            return
        user = User.objects.create_user(
            username=username,
            email='alumne@test.com',
            password='Patata1234#',
            role='alumno',
            email_verified=True,
        )
        PerfilAlumno.objects.create(
            user=user,
            nom_complet='Alumne de Prova',
            cicle='DAM',
            any_graduacio=2025,
        )
        self.stdout.write(f'  ✓ Alumne creat: {username}')

    def _create_empresa(self):
        from core.models import PerfilEmpresa
        username = 'empresa'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'⚠️  L\'usuari "{username}" ja existeix, s\'omet'))
            return
        user = User.objects.create_user(
            username=username,
            email='empresa@test.com',
            password='Patata1234#',
            role='empresa',
            email_verified=True,
        )
        PerfilEmpresa.objects.create(
            user=user,
            nombre_empresa='Empresa de Prova',
            cif='B12345678',
            validado=True,
        )
        self.stdout.write(f'  ✓ Empresa creada: {username}')

    def _create_admin(self):
        username = 'admin'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'⚠️  L\'usuari "{username}" ja existeix, s\'omet'))
            return
        User.objects.create_user(
            username=username,
            email='admin@test.com',
            password='Patata1234#',
            role='admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
        )
        self.stdout.write(f'  ✓ Admin creat: {username}')
