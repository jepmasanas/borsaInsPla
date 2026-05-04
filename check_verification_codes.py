"""
Script de diagnòstic per comprovar els codis de verificació
Executa amb: python manage.py shell < check_verification_codes.py
"""
from core.models import User, EmailVerification
from django.utils import timezone

print("\n" + "="*60)
print("DIAGNÒSTIC DE CODIS DE VERIFICACIÓ")
print("="*60 + "\n")

# Usuaris no verificats
usuaris_no_verificats = User.objects.filter(is_active=False, email_verified=False)
print(f"📊 Usuaris pendents de verificar: {usuaris_no_verificats.count()}")

if usuaris_no_verificats.exists():
    print("\nDetall dels usuaris no verificats:")
    for user in usuaris_no_verificats:
        print(f"\n  👤 Usuari: {user.username}")
        print(f"     Email: {user.email}")
        print(f"     Rol: {user.role}")
        print(f"     Creat: {user.date_joined}")
        
        # Comprovar si té codi de verificació
        try:
            verification = EmailVerification.objects.get(user=user)
            print(f"     ✅ Té codi de verificació")
            print(f"     Codi: {verification.code}")
            print(f"     Creat: {verification.created_at}")
            print(f"     Expira: {verification.expires_at}")
            print(f"     És vàlid: {'✅ Sí' if verification.is_valid() else '❌ No (expirat)'}")
            
            if not verification.is_valid():
                temps_expiracio = timezone.now() - verification.expires_at
                print(f"     Expirat fa: {temps_expiracio}")
        except EmailVerification.DoesNotExist:
            print(f"     ❌ NO té codi de verificació")

# Codis de verificació orfes (sense usuari o amb usuari ja verificat)
print("\n" + "-"*60)
print("Comprovant codis de verificació orfes...")
print("-"*60 + "\n")

tots_els_codis = EmailVerification.objects.all()
print(f"📊 Total de codis a la base de dades: {tots_els_codis.count()}")

if tots_els_codis.exists():
    for verification in tots_els_codis:
        if verification.user.is_active or verification.user.email_verified:
            print(f"⚠️  Codi orfe trobat:")
            print(f"   Usuari: {verification.user.username} (ja verificat)")
            print(f"   Codi: {verification.code}")
            print(f"   Recomanació: Eliminar aquest codi")

print("\n" + "="*60)
print("FI DEL DIAGNÒSTIC")
print("="*60 + "\n")
