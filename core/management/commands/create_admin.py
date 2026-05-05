from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un usuari administrador amb tots els permisos'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nom d\'usuari')
        parser.add_argument('--email', type=str, help='Email')
        parser.add_argument('--password', type=str, help='Contrasenya')

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')

        # Si no es passen arguments, demanar-los interactivament
        if not username:
            username = input('Nom d\'usuari: ').strip()
            if not username:
                self.stdout.write(self.style.ERROR('❌ El nom d\'usuari és obligatori'))
                return

        if not email:
            email = input('Email: ').strip()
            if not email:
                self.stdout.write(self.style.ERROR('❌ L\'email és obligatori'))
                return

        if not password:
            from getpass import getpass
            password = getpass('Contrasenya: ')
            password2 = getpass('Confirma la contrasenya: ')
            
            if password != password2:
                self.stdout.write(self.style.ERROR('❌ Les contrasenyes no coincideixen'))
                return
            
            if not password:
                self.stdout.write(self.style.ERROR('❌ La contrasenya és obligatòria'))
                return

        # Comprovar si l'usuari ja existeix
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'❌ L\'usuari "{username}" ja existeix'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'❌ L\'email "{email}" ja està registrat'))
            return

        # Crear l'usuari administrador
        try:
            with transaction.atomic():
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Establir el rol d'administrador i verificar email
                user.role = 'admin'
                user.email_verified = True
                user.save()

                self.stdout.write(self.style.SUCCESS(f'✅ Usuari administrador "{username}" creat correctament!'))
                self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))
                self.stdout.write(self.style.SUCCESS(f'   Rol: Administrador'))
                self.stdout.write(self.style.SUCCESS(f'   is_superuser: True'))
                self.stdout.write(self.style.SUCCESS(f'   is_staff: True'))
                self.stdout.write(self.style.SUCCESS(f'   email_verified: True'))
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('Ja pots accedir a:'))
                self.stdout.write(self.style.SUCCESS(f'   - Django Admin: /admin/'))
                self.stdout.write(self.style.SUCCESS(f'   - Aplicació: /login/'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creant l\'usuari: {str(e)}'))
