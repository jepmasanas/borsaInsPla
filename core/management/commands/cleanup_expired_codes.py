from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import EmailVerification, PasswordRecovery


class Command(BaseCommand):
    help = 'Neteja els codis de verificació i recuperació de contrasenya expirats'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra els codis a eliminar sense eliminar-los realment',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()

        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🧹 NETEJA DE CODIS EXPIRATS"))
        self.stdout.write("="*60 + "\n")

        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️  MODE DRY-RUN: No s'eliminarà res"))
            self.stdout.write("")

        # Netejar EmailVerification expirats
        email_verifications = EmailVerification.objects.filter(expires_at__lt=now)
        count_email = email_verifications.count()

        if count_email > 0:
            self.stdout.write(f"📧 Codis de verificació d'email expirats: {count_email}")
            for verification in email_verifications:
                time_expired = now - verification.expires_at
                hours = int(time_expired.total_seconds() / 3600)
                self.stdout.write(
                    f"   - Usuari: {verification.user.username} | "
                    f"Expirat fa: {hours}h | Codi: {verification.code}"
                )
            
            if not dry_run:
                email_verifications.delete()
                self.stdout.write(self.style.SUCCESS(f"✅ {count_email} codis d'email eliminats"))
        else:
            self.stdout.write("✅ No hi ha codis de verificació d'email expirats")

        self.stdout.write("")

        # Netejar PasswordRecovery expirats
        password_recoveries = PasswordRecovery.objects.filter(expires_at__lt=now)
        count_password = password_recoveries.count()

        if count_password > 0:
            self.stdout.write(f"🔐 Codis de recuperació de contrasenya expirats: {count_password}")
            for recovery in password_recoveries:
                time_expired = now - recovery.expires_at
                hours = int(time_expired.total_seconds() / 3600)
                self.stdout.write(
                    f"   - Usuari: {recovery.user.username} | "
                    f"Expirat fa: {hours}h | Codi: {recovery.code}"
                )
            
            if not dry_run:
                password_recoveries.delete()
                self.stdout.write(self.style.SUCCESS(f"✅ {count_password} codis de recuperació eliminats"))
        else:
            self.stdout.write("✅ No hi ha codis de recuperació de contrasenya expirats")

        # Netejar codis orfes (usuaris ja verificats)
        self.stdout.write("")
        orphan_verifications = EmailVerification.objects.filter(
            user__is_active=True,
            user__email_verified=True
        )
        count_orphan = orphan_verifications.count()

        if count_orphan > 0:
            self.stdout.write(self.style.WARNING(f"⚠️  Codis orfes (usuaris ja verificats): {count_orphan}"))
            for verification in orphan_verifications:
                self.stdout.write(f"   - Usuari: {verification.user.username}")
            
            if not dry_run:
                orphan_verifications.delete()
                self.stdout.write(self.style.SUCCESS(f"✅ {count_orphan} codis orfes eliminats"))
        else:
            self.stdout.write("✅ No hi ha codis orfes")

        self.stdout.write("\n" + "="*60)
        if dry_run:
            self.stdout.write(self.style.WARNING("ℹ️  MODE DRY-RUN: Cap canvi s'ha aplicat"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ NETEJA COMPLETADA"))
        self.stdout.write("="*60 + "\n")
