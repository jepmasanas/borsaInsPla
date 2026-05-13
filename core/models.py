from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import random


class User(AbstractUser):
    """Usuari extés amb rols"""
    ROLE_CHOICES = [
        ('admin', _('Administrador')),
        ('empresa', _('Empresa')),
        ('alumno', _('Alumno/Exalumne')),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='alumno',
        verbose_name=_('Rol')
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('Telèfon')
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email verificat')
    )

    class Meta:
        verbose_name = _('Usuari')
        verbose_name_plural = _('Usuaris')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class EmailVerification(models.Model):
    """Codis de verificació d'email"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification',
        verbose_name=_('Usuari')
    )
    code = models.CharField(
        max_length=6,
        verbose_name=_('Codi')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creat el')
    )
    expires_at = models.DateTimeField(
        verbose_name=_('Expira el')
    )

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at

    class Meta:
        verbose_name = _('Verificació Email')
        verbose_name_plural = _('Verificacions Email')

    def __str__(self):
        return f"Code for {self.user.username}: {self.code}"


class PasswordRecovery(models.Model):
    """Códis de recuperació de contrasenya"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='password_recovery',
        verbose_name=_('Usuari')
    )
    code = models.CharField(
        max_length=6,
        verbose_name=_('Codi')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creat el')
    )
    expires_at = models.DateTimeField(
        verbose_name=_('Expira el')
    )

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at

    class Meta:
        verbose_name = _('Recuperació Contrasenya')
        verbose_name_plural = _('Recuperacions Contrasenya')

    def __str__(self):
        return f"Recovery code for {self.user.username}: {self.code}"


class PerfilEmpresa(models.Model):
    """Perfil específic per empreses"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_empresa',
        verbose_name=_('Usuari')
    )
    nombre_empresa = models.CharField(
        max_length=200,
        verbose_name=_('Nom de l\'empresa')
    )
    cif = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('CIF/NIF')
    )
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Direcció')
    )
    sector = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Sector')
    )
    web = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Pàgina web')
    )
    logo = models.ImageField(
        upload_to='logos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        verbose_name=_('Logo')
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Descripció de l\'empresa')
    )
    validado = models.BooleanField(
        default=False,
        verbose_name=_('Empresa validada')
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de registre')
    )

    class Meta:
        verbose_name = _('Perfil Empresa')
        verbose_name_plural = _('Perfils Empreses')

    def __str__(self):
        return self.nombre_empresa


class PerfilAlumno(models.Model):
    """Perfil específic per alumnes/exalumnes"""
    CICLO_CHOICES = [
        ('DAM', _('CFGS Desenvolupament d\'Aplicacions Multiplataforma (DAM)')),
        ('SMX', _('CFGM Sistemes microinformàtics i xarxes (SMX)')),
        ('APD', _('CFGM Atenció a la dependència (APD) en Dual')),
        ('CAI', _('CFGM Cures Auxiliars d\'Infermeria')),
        ('ESO', _('ESO')),
        ('BATX', _('Batxillerat')),
        ('altres', _('Altres')),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_alumno',
        verbose_name=_('Usuari')
    )
    nom_complet = models.CharField(
        max_length=200,
        verbose_name=_('Nom complet')
    )
    cicle = models.CharField(
        max_length=10,
        choices=CICLO_CHOICES,
        verbose_name=_('Cicle formatiu')
    )
    any_graduacio = models.IntegerField(
        verbose_name=_('Any de graduació')
    )
    cv = models.FileField(
        upload_to='cvs/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])],
        verbose_name=_('Curriculum Vitae')
    )
    foto_perfil = models.ImageField(
        upload_to='fotos_perfil/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        verbose_name=_('Foto de perfil')
    )
    linkedin = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Perfil LinkedIn')
    )
    github = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Perfil GitHub')
    )
    competencies = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Competències i habilitats')
    )
    idiomes = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Idiomes')
    )
    disponibilitat = models.BooleanField(
        default=True,
        verbose_name=_('Disponible per treballar')
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de registre')
    )

    class Meta:
        verbose_name = _('Perfil Alumne')
        verbose_name_plural = _('Perfils Alumnes')

    def __str__(self):
        return self.nom_complet


class Oferta(models.Model):
    """Ofertas de trabajo publicadas por empresas"""
    MODALIDAD_CHOICES = [
        ('presencial', _('Presencial')),
        ('remot', _('Remot')),
        ('hibrid', _('Híbrid')),
    ]

    TIPO_CONTRATO_CHOICES = [
        ('indefinit', _('Indefinit')),
        ('temporal', _('Temporal')),
        ('practiques', _('Pràctiques')),
        ('freelance', _('Freelance')),
    ]

    empresa = models.ForeignKey(
        PerfilEmpresa,
        on_delete=models.CASCADE,
        related_name='ofertas',
        verbose_name=_('Empresa')
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name=_('Títol de l\'oferta')
    )
    descripcion = models.TextField(
        verbose_name=_('Descripció')
    )
    requisitos = models.TextField(
        verbose_name=_('Requisits')
    )
    modalidad = models.CharField(
        max_length=15,
        choices=MODALIDAD_CHOICES,
        default='presencial',
        verbose_name=_('Modalitat')
    )
    tipo_contrato = models.CharField(
        max_length=15,
        choices=TIPO_CONTRATO_CHOICES,
        default='indefinit',
        verbose_name=_('Tipus de contracte')
    )
    ubicacion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Ubicació')
    )
    salario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Salari')
    )
    fecha_publicacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de publicació')
    )
    fecha_cierre = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Data de tancament')
    )
    activa = models.BooleanField(
        default=True,
        verbose_name=_('Activa')
    )
    validada = models.BooleanField(
        default=False,
        verbose_name=_('Oferta validada per l\'administrador')
    )

    class Meta:
        verbose_name = _('Oferta')
        verbose_name_plural = _('Ofertes')
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return f"{self.titulo} - {self.empresa.nombre_empresa}"


class Inscripcion(models.Model):
    """Inscripciones de alumnos a ofertas"""
    ESTADO_CHOICES = [
        ('pendent', _('Pendent')),
        ('revisat', _('Revisat')),
        ('acceptat', _('Acceptat')),
        ('rebutjat', _('Rebutjat')),
    ]

    alumno = models.ForeignKey(
        PerfilAlumno,
        on_delete=models.CASCADE,
        related_name='inscripciones',
        verbose_name=_('Alumne')
    )
    oferta = models.ForeignKey(
        Oferta,
        on_delete=models.CASCADE,
        related_name='inscripciones',
        verbose_name=_('Oferta')
    )
    fecha_inscripcion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data d\'inscripció')
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='pendent',
        verbose_name=_('Estat')
    )
    carta_presentacion = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Carta de presentació')
    )

    class Meta:
        verbose_name = _('Inscripció')
        verbose_name_plural = _('Inscripcions')
        unique_together = ['alumno', 'oferta']
        ordering = ['-fecha_inscripcion']

    def __str__(self):
        return f"{self.alumno.nom_complet} -> {self.oferta.titulo}"


class Notificacion(models.Model):
    """Notificaciones del sistema"""
    TIPO_CHOICES = [
        ('inscripcion', _('Nova inscripció')),
        ('estado_cambio', _('Canvi d\'estat')),
        ('oferta_validada', _('Oferta validada')),
        ('empresa_validada', _('Empresa validada')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name=_('Usuari')
    )
    mensaje = models.TextField(
        verbose_name=_('Missatge')
    )
    leida = models.BooleanField(
        default=False,
        verbose_name=_('Llegida')
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data')
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name=_('Tipus')
    )
    url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Enllaç')
    )

    # Campos opcionales para contexto
    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Inscripció')
    )
    oferta = models.ForeignKey(
        Oferta,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Oferta')
    )

    class Meta:
        verbose_name = _('Notificació')
        verbose_name_plural = _('Notificacions')
        ordering = ['-fecha']

    def __str__(self):
        leida_text = _('Llegida') if self.leida else _('No llegida')
        return f"{self.user.username} - {self.get_tipo_display()} - {leida_text}"