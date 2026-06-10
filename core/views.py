from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta, date
from .models import (
    User, PerfilEmpresa, PerfilAlumno, Oferta, Inscripcion,
    EmailVerification, PasswordRecovery, Notificacion
)
from .utils import send_verification_email, send_password_recovery_email, send_welcome_email, send_nueva_inscripcion_email, send_notificacio_empresa_email
import json


def home(request):
    """Pàgina d'inici pública"""
    ofertas_recientes = Oferta.objects.filter(validada=True, activa=True)[:6]
    context = {
        'ofertas_recientes': ofertas_recientes
    }
    return render(request, 'core/home.html', context)


# ==================== REGISTRO Y VERIFICACIÓN ====================

def registro(request):
    """Registre de nous usuaris amb verificació de correu electrònic"""
    current_year = date.today().year

    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        def render_error(msg):
            messages.error(request, msg)
            return render(request, 'core/registro.html', {
                'form_data': request.POST,
                'current_year': current_year,
            })

        # Validaciones bàsiques
        if not username or not email or not password:
            return render_error('Tots els camps obligatoris són necessaris.')

        if password != password2:
            return render_error('Les contrasenyes no coincideixen.')

        if User.objects.filter(username__iexact=username).exists():
            return render_error('Aquest nom d\'usuari ja existeix.')

        if User.objects.filter(email=email).exists():
            return render_error('Aquest email ja està registrat.')

        # Validar contrasenya segura
        try:
            validate_password(password, user=None)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'core/registro.html', {
                'form_data': request.POST,
                'current_year': current_year,
            })

        # Validacions específiques per rol
        if role == 'empresa':
            nombre_empresa = request.POST.get('nombre_empresa', '').strip()
            cif = request.POST.get('cif', '').strip()

            if not nombre_empresa or not cif:
                return render_error('Nom d\'empresa i CIF són obligatoris.')

            if PerfilEmpresa.objects.filter(cif=cif).exists():
                return render_error('Aquest CIF ja està registrat.')

        elif role == 'alumno':
            nom_complet = request.POST.get('nom_complet', '').strip()
            cicle = request.POST.get('cicle', '')
            any_graduacio = request.POST.get('any_graduacio', '')

            if not nom_complet or not cicle or not any_graduacio:
                return render_error('Tots els camps d\'alumne són obligatoris.')

            try:
                any_graduacio = int(any_graduacio)
                if any_graduacio < 2020 or any_graduacio > current_year:
                    return render_error('Any de graduació no vàlid.')
            except ValueError:
                return render_error('Any de graduació ha de ser un número.')

        # Crear usuari, perfil i codi de verificació en una transacció atòmica
        try:
            with transaction.atomic():
                # Crear usuari (INACTIU fins a verificar email)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    is_active=False
                )

                # Crear perfil segons el  rol
                if role == 'empresa':
                    PerfilEmpresa.objects.create(
                        user=user,
                        nombre_empresa=request.POST.get('nombre_empresa', '').strip(),
                        cif=request.POST.get('cif', '').strip()
                    )
                elif role == 'alumno':
                    PerfilAlumno.objects.create(
                        user=user,
                        nom_complet=request.POST.get('nom_complet', '').strip(),
                        cicle=request.POST.get('cicle', 'DAM'),
                        any_graduacio=int(request.POST.get('any_graduacio', current_year))
                    )

                # Crear código de verificación
                EmailVerification.objects.filter(user=user).delete()
                verification = EmailVerification.objects.create(user=user)

                # Guardar l'user_id en la sessió ABANS d'enviar el mail
                request.session['pending_user_id'] = user.id
                request.session.save()

            # Enviar email (fora de la transacció)
            if send_verification_email(user, verification.code):
                messages.success(
                    request,
                    f'✅ Registre creat! Revisa el teu email ({email}) per verificar el compte.'
                )
                return redirect('verificar_email')
            else:
                messages.error(request, '❌ Error enviant l\'email. Contacta amb l\'administrador.')
                user.delete()
                return render(request, 'core/registro.html', {
                    'form_data': request.POST,
                    'current_year': current_year,
                })
        except Exception as e:
            messages.error(request, f'❌ Error durant el registre: {str(e)}')
            return render(request, 'core/registro.html', {
                'form_data': request.POST,
                'current_year': current_year,
            })

    return render(request, 'core/registro.html', {'current_year': current_year})


def verificar_email(request):
    """Vista per introduir el codi de verificació (registre nou o canvi de correu)"""
    user_id = request.session.get('pending_user_id')
    canvi_email = request.session.get('canvi_email', False)

    if not user_id:
        messages.error(request, 'Sessió expirada. Si us plau, torna a registrar-te.')
        return redirect('registro')

    try:
        user = User.objects.get(id=user_id)

        # Si l'usuari ja està verificat i no és un canvi de correu, redirigir al login
        if user.email_verified and user.is_active and not canvi_email:
            if 'pending_user_id' in request.session:
                del request.session['pending_user_id']
            messages.info(request, 'El teu email ja està verificat. Pots iniciar sessió.')
            return redirect('login')

    except User.DoesNotExist:
        messages.error(request, 'Usuari no trobat.')
        return redirect('registro')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()

        try:
            verification = EmailVerification.objects.get(user=user)

            if not verification.is_valid():
                messages.error(request, 'El codi ha expirat. Sol·licita un nou codi.')
                return redirect('verificar_email')

            if verification.code == code:
                # ✅ VERIFICAR QUE EL PERFIL EXISTE
                if user.role == 'empresa':
                    if not hasattr(user, 'perfil_empresa'):
                        messages.error(request, 'Error: perfil d\'empresa no trobat. Contacta amb l\'administrador.')
                        return redirect('verificar_email')
                elif user.role == 'alumno':
                    if not hasattr(user, 'perfil_alumno'):
                        messages.error(request, 'Error: perfil d\'alumne no trobat. Contacta amb l\'administrador.')
                        return redirect('verificar_email')

                # Activar usuario i verificar email
                user.is_active = True
                user.email_verified = True
                user.save()

                # Eliminar codi usat
                verification.delete()

                # Netejar la sessió
                canvi_email = request.session.pop('canvi_email', False)
                if 'pending_user_id' in request.session:
                    del request.session['pending_user_id']
                    request.session.modified = True

                # Si era un canvi de correu, redirigir al perfil
                if canvi_email:
                    messages.success(request, '✅ Correu electrònic verificat i actualitzat correctament.')
                    if user.role == 'alumno':
                        return redirect('alumno_perfil')
                    elif user.role == 'empresa':
                        return redirect('empresa_perfil')
                    return redirect('home')

                # Notificar admins del nou registre
                admins = User.objects.filter(role='admin')
                if user.role == 'empresa':
                    perfil_empresa = getattr(user, 'perfil_empresa', None)
                    nom = perfil_empresa.nombre_empresa if perfil_empresa else user.username
                    for admin in admins:
                        crear_notificacion(
                            user=admin,
                            mensaje=f"Nova empresa pendent de validació: {nom}.",
                            tipo='nova_empresa_pendent',
                            url='/admin-panel/validar-empreses/',
                        )
                elif user.role == 'alumno':
                    if settings.NOTIFY_ADMIN_NEW_STUDENTS:
                        perfil_alumno = getattr(user, 'perfil_alumno', None)
                        nom = perfil_alumno.nom_complet if perfil_alumno else user.username
                        for admin in admins:
                            crear_notificacion(
                                user=admin,
                                mensaje=f"Nou alumne registrat: {nom}.",
                                tipo='nou_alumno_registrat',
                                url='/estadistiques/',
                            )

                # Enviar email de bienvinguda (després de netejar sessió)
                send_welcome_email(user)

                messages.success(request, '✅ Email verificat correctament! Ja pots iniciar sessió.')
                return redirect('login')
            else:
                messages.error(request, '❌ Codi incorrecte. Torna-ho a provar.')
                return redirect('verificar_email')
        except EmailVerification.DoesNotExist:
            messages.error(request, 'No s\'ha trobat cap codi de verificació. Prova de reenviar el codi.')
            return redirect('verificar_email')

    context = {'user_email': user.email}
    return render(request, 'core/verificar_email.html', context)


def reenviar_codigo(request):
    """Reenviar codi de verificació"""
    user_id = request.session.get('pending_user_id')

    if not user_id:
        messages.error(request, 'Sessió expirada. Si us plau, torna a registrar-te.')
        return redirect('registro')

    try:
        user = User.objects.get(id=user_id, is_active=False)

        # Verificar que no sigui molt freqüent (màxim cada 60 segons)
        try:
            verification = EmailVerification.objects.get(user=user)
            time_since_creation = timezone.now() - verification.created_at

            if time_since_creation.total_seconds() < 60:
                messages.warning(request, '⏳ Espera 60 segons abans de reenviar un altre codi.')
                return redirect('verificar_email')
        except EmailVerification.DoesNotExist:
            pass

        # Eliminar codi anterior i crear-ne un de nou
        with transaction.atomic():
            EmailVerification.objects.filter(user=user).delete()
            verification = EmailVerification.objects.create(user=user)

        # Enviar email
        if send_verification_email(user, verification.code):
            messages.success(request, '✅ S\'ha enviat un nou codi al teu email.')
        else:
            messages.error(request, '❌ Error enviant l\'email. Torna-ho a provar.')
    except User.DoesNotExist:
        messages.error(request, 'Usuari no trobat o ja està activat.')
        return redirect('registro')

    return redirect('verificar_email')


# ==================== RECUPERACIÓ DE CONTRASENYA ====================

def olvidaste_contrasenya(request):
    """Solicitar recuperación de contraseña - Paso 1"""
    if request.method == 'POST':
        email_or_username = request.POST.get('email_or_username', '').strip()

        if not email_or_username:
            messages.error(request, 'Si us plau, introdueix un email o nom d\'usuari.')
            return render(request, 'core/olvidaste_contrasenya.html', {'form_value': email_or_username})

        # ✅ Buscar usuari amb Q objects (simplificat)
        try:
            user = User.objects.get(
                Q(email__iexact=email_or_username) | Q(username__iexact=email_or_username)
            )
        except User.DoesNotExist:
            # Por Seguretat, no revelar si existeix o no
            messages.info(
                request,
                '✉️ Si aquest compte existeix, rebràs un email amb les instruccions de recuperació.'
            )
            return render(request, 'core/olvidaste_contrasenya.html')
        except User.MultipleObjectsReturned:
            user = User.objects.filter(
                Q(email__iexact=email_or_username) | Q(username__iexact=email_or_username)
            ).first()

        # Crear codi de recuperació
        PasswordRecovery.objects.filter(user=user).delete()
        recovery = PasswordRecovery.objects.create(user=user)

        # Enviar email
        if send_password_recovery_email(user, recovery.code):
            messages.success(
                request,
                f'✅ Email de recuperació enviat a {user.email}. Revisa-ho en els pròxims 30 minuts.'
            )
            request.session['recovery_user_id'] = user.id
            return redirect('verificar_codigo_recuperacion')
        else:
            messages.error(request, '❌ Error enviant l\'email. Torna-ho a provar.')

    return render(request, 'core/olvidaste_contrasenya.html')


def verificar_codigo_recuperacion(request):
    """Verificar código de recuperación - Paso 2"""
    user_id = request.session.get('recovery_user_id')

    if not user_id:
        messages.error(request, 'Sessió expirada.')
        return redirect('olvidaste_contrasenya')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Usuari no trobat.')
        return redirect('olvidaste_contrasenya')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()

        try:
            recovery = PasswordRecovery.objects.get(user=user)

            if not recovery.is_valid():
                messages.error(request, 'El codi ha expirat. Sol·licita un altre.')
                return redirect('olvidaste_contrasenya')

            if recovery.code == code:
                request.session['recovery_verified'] = True
                messages.success(request, '✅ Codi verificat. Ara crea una nova contrasenya.')
                return redirect('cambiar_contrasenya_recuperacion')
            else:
                messages.error(request, '❌ Codi incorrecte.')
        except PasswordRecovery.DoesNotExist:
            messages.error(request, 'No s\'ha trobat cap codi de recuperació.')

    context = {'user_email': user.email}
    return render(request, 'core/verificar_codigo_recuperacion.html', context)


def reenviar_codigo_recuperacion(request):
    """Reenviar código de recuperación"""
    user_id = request.session.get('recovery_user_id')

    if not user_id:
        messages.error(request, 'Sessió expirada.')
        return redirect('olvidaste_contrasenya')

    try:
        user = User.objects.get(id=user_id)

        try:
            recovery = PasswordRecovery.objects.get(user=user)
            time_since_creation = timezone.now() - recovery.created_at

            if time_since_creation.total_seconds() < 60:
                messages.warning(request, '⏳ Espera 60 segons abans de reenviar un altre codi.')
                return redirect('verificar_codigo_recuperacion')
        except PasswordRecovery.DoesNotExist:
            pass

        PasswordRecovery.objects.filter(user=user).delete()
        recovery = PasswordRecovery.objects.create(user=user)

        if send_password_recovery_email(user, recovery.code):
            messages.success(request, '✅ S\'ha enviat un nou codi.')
        else:
            messages.error(request, '❌ Error enviant l\'email.')
    except User.DoesNotExist:
        messages.error(request, 'Usuari no trobat.')
        return redirect('olvidaste_contrasenya')

    return redirect('verificar_codigo_recuperacion')


def cambiar_contrasenya_recuperacion(request):
    """Cambiar contrasenya - Paso 3"""
    user_id = request.session.get('recovery_user_id')
    recovery_verified = request.session.get('recovery_verified')

    if not user_id or not recovery_verified:
        messages.error(request, 'Procés no vàlid. Si us plau, comença de nou.')
        return redirect('olvidaste_contrasenya')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Usuari no trobat.')
        return redirect('olvidaste_contrasenya')

    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not password or not password2:
            messages.error(request, 'Tots els camps són obligatoris.')
            return render(request, 'core/cambiar_contrasenya_recuperacion.html', context)

        if password != password2:
            messages.error(request, 'Les contrasenyes no coincideixen.')
            return render(request, 'core/cambiar_contrasenya_recuperacion.html', context)

        try:
            validate_password(password, user=user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'core/cambiar_contrasenya_recuperacion.html', context)

        # Cambiar contrasenya i activar conta
        user.set_password(password)
        user.is_active = True
        user.email_verified = True
        user.save()

        # Netejar tokens i sesions
        EmailVerification.objects.filter(user=user).delete()
        PasswordRecovery.objects.filter(user=user).delete()

        del request.session['recovery_user_id']
        del request.session['recovery_verified']

        if 'pending_user_id' in request.session:
            del request.session['pending_user_id']

        messages.success(request, '✅ Contrasenya canviada i compte verificat correctament. Ja pots iniciar sessió.')
        return redirect('login')

    context = {'user_email': user.email}
    return render(request, 'core/cambiar_contrasenya_recuperacion.html', context)


# ==================== LOGIN / LOGOUT ====================

def login_view(request):
    """Login de usuarios"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Aquesta compte està desactivada.')
                return render(request, 'core/login.html', {'form_username': username})

            if not user.email_verified:
                messages.warning(request, 'Si us plau, verifica el teu email primer.')
                request.session['pending_user_id'] = user.id
                return redirect('verificar_email')

            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credencials incorrectes.')

    return render(request, 'core/login.html', {'form_username': request.POST.get('username', '') if request.method == 'POST' else ''})


@login_required
def logout_view(request):
    """Logout d'usuaris"""
    logout(request)
    messages.success(request, 'Sessió tancada correctament.')
    return redirect('home')


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    """Dashboard principal que redirige según el rol"""
    user = request.user

    # ✅ Verificar que el perfil existeix abans de redirigir
    if user.role == 'admin':
        return redirect('estadisticas')
    elif user.role == 'empresa':
        if not hasattr(user, 'perfil_empresa'):
            messages.error(request, '❌ El teu perfil d\'empresa no existeix. Contacta amb l\'administrador.')
            logout(request)
            return redirect('home')
        return redirect('empresa_ofertas')
    elif user.role == 'alumno':
        if not hasattr(user, 'perfil_alumno'):
            messages.error(request, '❌ El teu perfil d\'alumne no existeix. Contacta amb l\'administrador.')
            logout(request)
            return redirect('home')
        return redirect('alumno_ofertas')
    else:
        return redirect('home')


def estadisticas(request):
    """Pàgina d'estadístiques del sistema"""
    total_usuarios = User.objects.count()
    total_alumnos = User.objects.filter(role='alumno').count()
    total_empresas = User.objects.filter(role='empresa').count()
    total_ofertas = Oferta.objects.count()
    ofertas_activas = Oferta.objects.filter(activa=True, validada=True).count()
    total_inscripciones = Inscripcion.objects.count()

    tasa_actividad = round((ofertas_activas * 100) / total_ofertas) if total_ofertas > 0 else 0

    inscripciones_por_tipo = {}
    for tipo_key, tipo_label in Oferta.TIPO_CONTRATO_CHOICES:
        count = Oferta.objects.filter(tipo_contrato=tipo_key, validada=True, activa=True).count()
        inscripciones_por_tipo[str(tipo_label)] = count

    por_modalidad = {}
    for modal_key, modal_label in Oferta.MODALIDAD_CHOICES:
        count = Oferta.objects.filter(modalidad=modal_key, validada=True, activa=True).count()
        por_modalidad[str(modal_label)] = count

    por_ciclo = {}
    for ciclo_key, ciclo_label in PerfilAlumno.CICLO_CHOICES:
        count = PerfilAlumno.objects.filter(cicle=ciclo_key).count()
        if count > 0:
            por_ciclo[str(ciclo_label)] = count

    estado_inscripciones = {}
    for estado_key, estado_label in Inscripcion.ESTADO_CHOICES:
        count = Inscripcion.objects.filter(estado=estado_key).count()
        estado_inscripciones[str(estado_label)] = count

    context = {
        'total_usuarios': total_usuarios,
        'total_alumnos': total_alumnos,
        'total_empresas': total_empresas,
        'total_ofertas': total_ofertas,
        'ofertas_activas': ofertas_activas,
        'total_inscripciones': total_inscripciones,
        'tasa_actividad': tasa_actividad,
        'inscripciones_por_tipo_labels': json.dumps(list(inscripciones_por_tipo.keys())),
        'inscripciones_por_tipo_values': json.dumps(list(inscripciones_por_tipo.values())),
        'por_modalidad_labels': json.dumps(list(por_modalidad.keys())),
        'por_modalidad_values': json.dumps(list(por_modalidad.values())),
        'por_ciclo_labels': json.dumps(list(por_ciclo.keys())),
        'por_ciclo_values': json.dumps(list(por_ciclo.values())),
        'estado_inscripciones_labels': json.dumps(list(estado_inscripciones.keys())),
        'estado_inscripciones_values': json.dumps(list(estado_inscripciones.values())),
        'por_ciclo': por_ciclo,
    }

    return render(request, 'core/estadisticas.html', context)


# ==================== VISTES EMPRESA ====================

@login_required
def canviar_email(request):
    """Canviar el correu electrònic de l'usuari amb re-verificació"""
    if request.method == 'POST':
        nou_email = request.POST.get('nou_email', '').strip()

        if not nou_email:
            messages.error(request, 'Has d\'introduir un correu electrònic.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        if nou_email == request.user.email:
            messages.warning(request, 'El correu introduït és el mateix que l\'actual.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        if User.objects.filter(email=nou_email).exclude(pk=request.user.pk).exists():
            messages.error(request, 'Aquest correu ja està registrat per un altre usuari.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        try:
            with transaction.atomic():
                user = request.user
                user.email = nou_email
                user.email_verified = False
                user.is_active = False
                user.save()

                EmailVerification.objects.filter(user=user).delete()
                verification = EmailVerification.objects.create(user=user)

            request.session['pending_user_id'] = user.id
            request.session['canvi_email'] = True
            request.session.save()

            if send_verification_email(user, verification.code):
                messages.success(request, f'✅ S\'ha enviat un codi de verificació a {nou_email}. Revisa el teu correu.')
                return redirect('verificar_email')
            else:
                user.is_active = True
                user.email_verified = True
                user.save()
                messages.error(request, '❌ Error enviant l\'email. El correu no s\'ha canviat.')
                return redirect(request.META.get('HTTP_REFERER', 'home'))

        except Exception as e:
            messages.error(request, f'❌ Error canviant el correu: {str(e)}')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

    return redirect('home')


@login_required
def empresa_perfil(request):
    """Perfil de l'empresa"""
    if request.user.role != 'empresa':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    try:
        perfil = request.user.perfil_empresa
    except PerfilEmpresa.DoesNotExist:
        messages.error(request, '❌ El teu perfil d\'empresa no existeix.')
        return redirect('home')

    if request.method == 'POST':
        perfil.nombre_empresa = request.POST.get('nombre_empresa', perfil.nombre_empresa).strip()
        perfil.sector = request.POST.get('sector', '') or None
        perfil.direccion = request.POST.get('direccion', '') or None
        perfil.web = request.POST.get('web', '') or None
        perfil.descripcion = request.POST.get('descripcion', '') or None

        if 'logo' in request.FILES:
            perfil.logo = request.FILES['logo']

        perfil.save()
        messages.success(request, 'Perfil actualitzat correctament.')
        return redirect('empresa_perfil')

    context = {'perfil': perfil}
    return render(request, 'core/empresa/perfil.html', context)


@login_required
def empresa_ofertas(request):
    """Dashboard empresa - Llista d'ofertes propies"""
    if request.user.role != 'empresa':
        messages.error(request, 'No tens permisos per accedir a aquesta pàgina.')
        return redirect('home')

    # ✅ Verificar que el perfil existe
    try:
        perfil = request.user.perfil_empresa
    except PerfilEmpresa.DoesNotExist:
        messages.error(request, '❌ El teu perfil d\'empresa no existeix. Contacta amb l\'administrador.')
        logout(request)
        return redirect('home')

    ofertas = perfil.ofertas.all()

    context = {
        'perfil': perfil,
        'ofertas': ofertas
    }
    return render(request, 'core/empresa/ofertas.html', context)


@login_required
def empresa_nueva_oferta(request):
    """Crear nueva oferta"""
    if request.user.role != 'empresa':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    try:
        perfil = request.user.perfil_empresa
    except PerfilEmpresa.DoesNotExist:
        messages.error(request, '❌ El teu perfil d\'empresa no existeix.')
        return redirect('home')

    if request.method == 'POST':
        oferta = Oferta.objects.create(
            empresa=perfil,
            titulo=request.POST.get('titulo'),
            descripcion=request.POST.get('descripcion'),
            requisitos=request.POST.get('requisitos'),
            modalidad=request.POST.get('modalidad'),
            tipo_contrato=request.POST.get('tipo_contrato'),
            ubicacion=request.POST.get('ubicacion', ''),
            salario=request.POST.get('salario', ''),
        )

        # Notificar a tots els admins
        admins = User.objects.filter(role='admin')
        for admin in admins:
            crear_notificacion(
                user=admin,
                mensaje=f"Nova oferta pendent de validació: «{oferta.titulo}» de {perfil.nombre_empresa}.",
                tipo='nova_oferta_pendent',
                url='/admin-panel/validar-ofertes/',
                oferta=oferta,
            )

        messages.success(request, 'Oferta creada correctament. Pendent de validació.')
        return redirect('empresa_ofertas')

    return render(request, 'core/empresa/nueva_oferta.html')


@login_required
def empresa_editar_oferta(request, pk):
    """Editar oferta existent"""
    oferta = get_object_or_404(Oferta, pk=pk, empresa__user=request.user)

    if request.method == 'POST':
        oferta.titulo = request.POST.get('titulo')
        oferta.descripcion = request.POST.get('descripcion')
        oferta.requisitos = request.POST.get('requisitos')
        oferta.modalidad = request.POST.get('modalidad')
        oferta.tipo_contrato = request.POST.get('tipo_contrato')
        oferta.ubicacion = request.POST.get('ubicacion', '')
        oferta.salario = request.POST.get('salario', '')
        oferta.save()

        messages.success(request, 'Oferta actualitzada correctament.')
        return redirect('empresa_ofertas')

    context = {'oferta': oferta}
    return render(request, 'core/empresa/editar_oferta.html', context)


@login_required
def empresa_eliminar_oferta(request, pk):
    """Eliminar oferta"""
    oferta = get_object_or_404(Oferta, pk=pk, empresa__user=request.user)

    if request.method == 'POST':
        oferta.delete()
        messages.success(request, 'Oferta eliminada correctament.')

    return redirect('empresa_ofertas')


@login_required
def empresa_ver_candidatos(request, pk):
    """Veure tots els candidats inscrits en una oferta"""
    if request.user.role != 'empresa':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    oferta = get_object_or_404(Oferta, pk=pk, empresa__user=request.user)
    inscripciones = oferta.inscripciones.all().select_related('alumno', 'alumno__user')

    estado_filter = request.GET.get('estado', '')
    if estado_filter:
        inscripciones = inscripciones.filter(estado=estado_filter)

    context = {
        'oferta': oferta,
        'inscripciones': inscripciones,
        'estado_filter': estado_filter,
    }
    return render(request, 'core/empresa/ver_candidatos.html', context)


@login_required
def empresa_cambiar_estado_inscripcion(request, pk):
    """Cambiar l'estat d'una inscripció"""
    if request.user.role != 'empresa':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    if request.method == 'POST':
        inscripcion = get_object_or_404(
            Inscripcion,
            pk=pk,
            oferta__empresa__user=request.user
        )

        nuevo_estado = request.POST.get('estado')

        if nuevo_estado in dict(Inscripcion.ESTADO_CHOICES):
            inscripcion.estado = nuevo_estado
            inscripcion.save()

            estado_label = dict(Inscripcion.ESTADO_CHOICES)[nuevo_estado]

            emoji_map = {
                'pendent': '⏳',
                'revisat': '👀',
                'acceptat': '✅',
                'rebutjat': '❌'
            }

            crear_notificacion(
                user=inscripcion.alumno.user,
                mensaje=f"{emoji_map.get(nuevo_estado, '📬')} L'estat de la teva inscripció a '{inscripcion.oferta.titulo}' ha canviat a: {estado_label}",
                tipo='estado_cambio',
                url='/alumne/les-meves-inscripcions/',
                inscripcion=inscripcion,
                oferta=inscripcion.oferta
            )

            send_notificacio_empresa_email(
                inscripcion.alumno.user,
                assumpte=f'Actualització de la teva inscripció a "{inscripcion.oferta.titulo}" - BorsaInsPla',
                cos_html=(
                    f'<p>{emoji_map.get(nuevo_estado, "📬")} L\'estat de la teva inscripció a l\'oferta '
                    f'<strong>"{inscripcion.oferta.titulo}"</strong> '
                    f'({inscripcion.oferta.empresa.nombre_empresa}) '
                    f'ha canviat a: <strong>{estado_label}</strong>.</p>'
                )
            )

            messages.success(request, f'Estat canviat a "{estado_label}" correctament.')
        else:
            messages.error(request, 'Estat no vàlid.')

        return redirect('empresa_ver_candidatos', pk=inscripcion.oferta.pk)

    return redirect('empresa_ofertas')


@login_required
def empresa_descargar_cv(request, inscripcion_id):
    """Descargar el CV de un candidato"""
    if request.user.role != 'empresa':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    inscripcion = get_object_or_404(
        Inscripcion,
        pk=inscripcion_id,
        oferta__empresa__user=request.user
    )

    alumno = inscripcion.alumno

    if not alumno.cv:
        messages.error(request, 'Aquest alumne no té CV pujat.')
        return redirect('empresa_ver_candidatos', pk=inscripcion.oferta.pk)

    from django.http import FileResponse
    import os

    cv_file = alumno.cv
    file_extension = os.path.splitext(cv_file.name)[1]
    download_name = f"CV_{alumno.nom_complet.replace(' ', '_')}{file_extension}"

    response = FileResponse(cv_file.open('rb'))
    response['Content-Disposition'] = f'attachment; filename="{download_name}"'

    return response


# ==================== VISTES ALUMNE ====================

@login_required
def alumno_perfil(request):
    """Perfil de l'alumne"""
    if request.user.role != 'alumno':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    try:
        perfil = request.user.perfil_alumno
    except PerfilAlumno.DoesNotExist:
        messages.error(request, '❌ El teu perfil d\'alumne no existeix.')
        return redirect('home')

    if request.method == 'POST':
        perfil.nom_complet = request.POST.get('nom_complet')
        perfil.cicle = request.POST.get('cicle')
        perfil.any_graduacio = request.POST.get('any_graduacio')
        perfil.linkedin = request.POST.get('linkedin') or None
        perfil.github = request.POST.get('github', '')
        perfil.competencies = request.POST.get('competencies', '')
        perfil.idiomes = request.POST.get('idiomes', '')

        if 'cv' in request.FILES:
            perfil.cv = request.FILES['cv']

        perfil.save()
        messages.success(request, 'Perfil actualitzat correctament.')
        return redirect('alumno_perfil')

    context = {'perfil': perfil}
    return render(request, 'core/alumno/perfil.html', context)


@login_required
def alumno_ofertas(request):
    """Llista d'ofertes per a alumnes amb cerca avançada"""
    if request.user.role != 'alumno':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    ofertas = Oferta.objects.filter(validada=True, activa=True)

    search = request.GET.get('search', '')
    modalidad = request.GET.get('modalidad', '')
    tipo = request.GET.get('tipo', '')
    ubicacion = request.GET.get('ubicacion', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    orden = request.GET.get('orden', '-fecha_publicacion')

    if search:
        ofertas = ofertas.filter(
            Q(titulo__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(empresa__nombre_empresa__icontains=search) |
            Q(requisitos__icontains=search)
        )

    if modalidad:
        ofertas = ofertas.filter(modalidad=modalidad)

    if tipo:
        ofertas = ofertas.filter(tipo_contrato=tipo)

    if ubicacion:
        ofertas = ofertas.filter(ubicacion__icontains=ubicacion)

    if fecha_desde:
        ofertas = ofertas.filter(fecha_publicacion__gte=fecha_desde)

    ofertas = ofertas.order_by(orden)

    context = {'ofertas': ofertas}
    return render(request, 'core/alumno/ofertas.html', context)


@login_required
def alumno_detalle_oferta(request, pk):
    """Detall d'una oferta"""
    oferta = get_object_or_404(Oferta, pk=pk, validada=True, activa=True)

    inscrito = False
    if request.user.role == 'alumno':
        try:
            inscrito = Inscripcion.objects.filter(
                alumno=request.user.perfil_alumno,
                oferta=oferta
            ).exists()
        except PerfilAlumno.DoesNotExist:
            pass

    context = {
        'oferta': oferta,
        'inscrito': inscrito
    }
    return render(request, 'core/alumno/detalle_oferta.html', context)


@login_required
def alumno_inscribirse(request, pk):
    """Inscribir-se a una oferta"""
    if request.user.role != 'alumno':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    oferta = get_object_or_404(Oferta, pk=pk, validada=True, activa=True)

    try:
        perfil = request.user.perfil_alumno
    except PerfilAlumno.DoesNotExist:
        messages.error(request, '❌ El teu perfil d\'alumne no existeix.')
        return redirect('home')

    if Inscripcion.objects.filter(alumno=perfil, oferta=oferta).exists():
        messages.warning(request, 'Ja estàs inscrit a aquesta oferta.')
        return redirect('alumno_detalle_oferta', pk=pk)

    if request.method == 'POST':
        inscripcion = Inscripcion.objects.create(
            alumno=perfil,
            oferta=oferta,
            carta_presentacion=request.POST.get('carta_presentacion', '')
        )

        crear_notificacion(
            user=oferta.empresa.user,
            mensaje=f"🎓 {perfil.nom_complet} s'ha inscrit a la teva oferta '{oferta.titulo}'",
            tipo='inscripcion',
            url=f'/empresa/oferta/{oferta.pk}/candidats/',
            inscripcion=inscripcion,
            oferta=oferta
        )

        send_nueva_inscripcion_email(oferta.empresa.user, perfil, oferta)

        messages.success(request, 'Inscripció realitzada correctament!')
        return redirect('alumno_inscripciones')

    context = {'oferta': oferta}
    return render(request, 'core/alumno/inscribirse.html', context)


@login_required
def alumno_inscripciones(request):
    """Les meves inscripcions"""
    if request.user.role != 'alumno':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    try:
        inscripciones = Inscripcion.objects.filter(alumno=request.user.perfil_alumno)
    except PerfilAlumno.DoesNotExist:
        messages.error(request, '❌ El teu perfil d\'alumne no existeix.')
        return redirect('home')

    context = {'inscripciones': inscripciones}
    return render(request, 'core/alumno/inscripciones.html', context)


@login_required
def alumno_cancelar_inscripcion(request, pk):
    """Cancel·lar un inscripció"""
    if request.user.role != 'alumno':
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    try:
        inscripcion = get_object_or_404(
            Inscripcion,
            pk=pk,
            alumno=request.user.perfil_alumno
        )
    except PerfilAlumno.DoesNotExist:
        messages.error(request, '❌ El teu perfil d\'alumne no existeix.')
        return redirect('home')

    if request.method == 'POST':
        oferta_titulo = inscripcion.oferta.titulo
        empresa_user = inscripcion.oferta.empresa.user

        crear_notificacion(
            user=empresa_user,
            mensaje=f"❌ {request.user.perfil_alumno.nom_complet} ha cancel·lat la seva inscripció a '{oferta_titulo}'",
            tipo='inscripcion',
            url=f'/empresa/oferta/{inscripcion.oferta.pk}/candidats/',
            oferta=inscripcion.oferta
        )

        alumne_nom = request.user.perfil_alumno.nom_complet
        send_notificacio_empresa_email(
            empresa_user,
            assumpte=f'Un candidat ha cancel·lat la seva inscripció - BorsaInsPla',
            cos_html=f'<p>❌ <strong>{alumne_nom}</strong> ha cancel·lat la seva inscripció a l\'oferta <strong>"{oferta_titulo}"</strong>.</p>'
        )

        inscripcion.delete()

        messages.success(request, f'Inscripció a "{oferta_titulo}" cancel·lada correctament.')
        return redirect('alumno_inscripciones')

    context = {'inscripcion': inscripcion}
    return render(request, 'core/alumno/cancelar_inscripcion.html', context)


# ==================== VISTES ADMIN ====================

@login_required
def admin_enviar_correu(request):
    """Vista per enviar un correu personalitzat a una empresa"""
    if not request.user.is_staff:
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    # Buscador AJAX d'empreses
    if request.GET.get('format') == 'json':
        q = request.GET.get('q', '').strip()
        empreses = PerfilEmpresa.objects.filter(
            nombre_empresa__icontains=q
        ).select_related('user').values(
            'id', 'nombre_empresa', 'user__email', 'user__username'
        )[:10]
        return JsonResponse({'results': list(empreses)})

    if request.method == 'POST':
        empresa_id = request.POST.get('empresa_id')
        assumpte = request.POST.get('assumpte', '').strip()
        cos = request.POST.get('cos', '').strip()

        if not empresa_id or not assumpte or not cos:
            messages.error(request, 'Tots els camps són obligatoris.')
            return render(request, 'core/admin/enviar_correu.html', {'form_data': request.POST})

        try:
            empresa = PerfilEmpresa.objects.select_related('user').get(id=empresa_id)
        except PerfilEmpresa.DoesNotExist:
            messages.error(request, 'Empresa no trobada.')
            return render(request, 'core/admin/enviar_correu.html', {'form_data': request.POST})

        cos_html = f'<div style="white-space:pre-line">{cos}</div>'
        ok = send_notificacio_empresa_email(empresa.user, assumpte=assumpte, cos_html=cos_html)

        if ok:
            messages.success(request, f'✅ Correu enviat correctament a {empresa.nombre_empresa} ({empresa.user.email}).')
            return redirect('admin_enviar_correu')
        else:
            messages.error(request, '❌ Error enviant el correu. Comprova la configuració SMTP.')
            return render(request, 'core/admin/enviar_correu.html', {'form_data': request.POST})

    return render(request, 'core/admin/enviar_correu.html')


@login_required
def admin_validar_empresas(request):
    """Vista personalizada para validar empreses"""
    if not request.user.is_staff:
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    if request.method == 'POST':
        empresa_id = request.POST.get('empresa_id')
        action = request.POST.get('action')

        try:
            empresa = PerfilEmpresa.objects.get(id=empresa_id)

            if action == 'validar':
                empresa.validado = True
                empresa.save()
                messages.success(request, f'Empresa {empresa.nombre_empresa} validada correctament.')
            elif action == 'rechazar':
                empresa.user.is_active = False
                empresa.user.save()
                messages.warning(request, f'Empresa {empresa.nombre_empresa} rebutjada. Usuari desactivat.')
        except PerfilEmpresa.DoesNotExist:
            messages.error(request, 'Empresa no trobada.')

        return redirect('admin_validar_empresas')

    empresas_pendientes = PerfilEmpresa.objects.filter(validado=False)

    context = {'empresas': empresas_pendientes}
    return render(request, 'core/admin/validar_empresas.html', context)


@login_required
def admin_validar_ofertas(request):
    """Vista personalitzada para validar ofertas"""
    if not request.user.is_staff:
        messages.error(request, 'No tens permisos.')
        return redirect('home')

    if request.method == 'POST':
        oferta_id = request.POST.get('oferta_id')
        action = request.POST.get('action')

        try:
            oferta = Oferta.objects.get(id=oferta_id)

            if action == 'validar':
                oferta.validada = True
                oferta.save()

                # Notificació de validació exitosa
                crear_notificacion(
                    user=oferta.empresa.user,
                    mensaje=f"✅ La teva oferta '{oferta.titulo}' ha estat validada i ara és visible per als alumnes",
                    tipo='validacion',
                    url=f'/empresa/ofertes/',
                    oferta=oferta
                )

                send_notificacio_empresa_email(
                    oferta.empresa.user,
                    assumpte=f'L\'oferta "{oferta.titulo}" ha estat validada - BorsaInsPla',
                    cos_html=f'<p>✅ La teva oferta <strong>"{oferta.titulo}"</strong> ha estat validada i ara és visible per als alumnes a la plataforma.</p>'
                )

                messages.success(request, f'Oferta "{oferta.titulo}" validada correctament.')

            elif action == 'rechazar':
                oferta.activa = False
                oferta.save()

                # Notificació de rebuig
                crear_notificacion(
                    user=oferta.empresa.user,
                    mensaje=f"❌ La teva oferta '{oferta.titulo}' ha estat rebutjada. Si us plau, revisa el contingut i torna-la a publicar si escau",
                    tipo='validacion',
                    url=f'/empresa/oferta/{oferta.id}/editar/',
                    oferta=oferta
                )

                send_notificacio_empresa_email(
                    oferta.empresa.user,
                    assumpte=f'L\'oferta "{oferta.titulo}" ha estat rebutjada - BorsaInsPla',
                    cos_html=f'<p>❌ La teva oferta <strong>"{oferta.titulo}"</strong> ha estat rebutjada. Si us plau, revisa el contingut i torna-la a publicar si escau.</p>'
                )

                messages.warning(request, f'Oferta "{oferta.titulo}" rebutjada i desactivada.')

        except Oferta.DoesNotExist:
            messages.error(request, 'Oferta no trobada.')

        return redirect('admin_validar_ofertas')

    ofertas_pendientes = Oferta.objects.filter(validada=False)

    context = {'ofertas': ofertas_pendientes}
    return render(request, 'core/admin/validar_ofertas.html', context)


# ==================== VISTES NOTIFICACIONS ====================

# Tipus de notificació que no es marquen com llegides automàticament
TIPOS_PERSISTENTS = {'nova_empresa_pendent', 'nova_oferta_pendent'}


@login_required
def notificaciones_lista(request):
    """Lista de notificacions de l'usuario"""
    notificaciones = Notificacion.objects.filter(user=request.user)
    notificaciones.filter(leida=False).exclude(tipo__in=TIPOS_PERSISTENTS).update(leida=True)

    context = {'notificaciones': notificaciones}
    return render(request, 'core/notificaciones/lista.html', context)


@login_required
def notificacion_marcar_leida(request, pk):
    """Marcar una notificació com a llegida"""
    notificacion = get_object_or_404(Notificacion, pk=pk, user=request.user)

    if notificacion.tipo not in TIPOS_PERSISTENTS:
        notificacion.leida = True
        notificacion.save()

    if notificacion.url:
        return redirect(notificacion.url)

    return redirect('notificaciones_lista')


@login_required
def notificaciones_marcar_todas_leidas(request):
    """Marcar todas las notificacions com a llegides (excepte les persistents)"""
    Notificacion.objects.filter(user=request.user, leida=False).exclude(tipo__in=TIPOS_PERSISTENTS).update(leida=True)
    messages.success(request, 'Totes les notificacions marcades com llegides.')
    return redirect('notificaciones_lista')


@login_required
def notificacion_eliminar(request, pk):
    """Eliminar una notificació"""
    if request.method == 'POST':
        notificacion = get_object_or_404(Notificacion, pk=pk, user=request.user)
        notificacion.delete()
        messages.success(request, 'Notificació eliminada.')

    return redirect('notificaciones_lista')


# ==================== HELPER PARA CREAR NOTIFICACIONS ====================

def crear_notificacion(user, mensaje, tipo, url='', inscripcion=None, oferta=None):
    """Funció helper para crear notificacions"""
    Notificacion.objects.create(
        user=user,
        mensaje=mensaje,
        tipo=tipo,
        url=url,
        inscripcion=inscripcion,
        oferta=oferta
    )


def ajustes(request):
    """Vista de configuració/ajustos de l'usuari"""
    context = {
        'current_language': request.LANGUAGE_CODE,
    }
    return render(request, 'core/ajustes.html', context)
