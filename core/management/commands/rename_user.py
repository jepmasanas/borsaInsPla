from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Renombra un usuari existent'

    def add_arguments(self, parser):
        parser.add_argument('--old-username', type=str, help='Nom d\'usuari actual')
        parser.add_argument('--new-username', type=str, help='Nou nom d\'usuari')

    def handle(self, *args, **options):
        old_username = options.get('old_username')
        new_username = options.get('new_username')

        # Si no es passen arguments, demanar-los interactivament
        if not old_username:
            old_username = input('Nom d\'usuari actual: ').strip()
            if not old_username:
                self.stdout.write(self.style.ERROR('❌ El nom d\'usuari actual és obligatori'))
                return

        if not new_username:
            new_username = input('Nou nom d\'usuari: ').strip()
            if not new_username:
                self.stdout.write(self.style.ERROR('❌ El nou nom d\'usuari és obligatori'))
                return

        # Comprovar si l'usuari actual existeix
        try:
            user = User.objects.get(username=old_username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ L\'usuari "{old_username}" no existeix'))
            return

        # Comprovar si el nou nom ja està en ús
        if User.objects.filter(username=new_username).exists():
            self.stdout.write(self.style.ERROR(f'❌ El nom d\'usuari "{new_username}" ja està en ús'))
            return

        # Mostrar informació de l'usuari
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Informació de l\'usuari:'))
        self.stdout.write(f'  Nom actual: {user.username}')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Rol: {user.get_role_display()}')
        self.stdout.write(f'  Actiu: {user.is_active}')
        self.stdout.write('')

        # Confirmar el canvi
        confirm = input(f'Estàs segur que vols canviar el nom d\'usuari a "{new_username}"? (s/n): ').strip().lower()
        
        if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
            self.stdout.write(self.style.WARNING('❌ Operació cancel·lada'))
            return

        # Renombrar l'usuari
        try:
            with transaction.atomic():
                old_name = user.username
                user.username = new_username
                user.save()

                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS(f'✅ Usuari renombrat correctament!'))
                self.stdout.write(self.style.SUCCESS(f'   Nom anterior: {old_name}'))
                self.stdout.write(self.style.SUCCESS(f'   Nom nou: {new_username}'))
                self.stdout.write(self.style.SUCCESS(f'   Email: {user.email}'))
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS(f'L\'usuari ara pot fer login amb: {new_username}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error renombrant l\'usuari: {str(e)}'))
