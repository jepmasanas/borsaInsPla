from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PerfilEmpresa, PerfilAlumno, Oferta, Inscripcion, EmailVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administración de usuarios"""
    list_display = ['username', 'email', 'role', 'email_verified', 'first_name', 'last_name', 'is_active']
    list_filter = ['role', 'email_verified', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informació addicional', {
            'fields': ('role', 'telefono', 'email_verified')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informació addicional', {
            'fields': ('role', 'telefono', 'email_verified')
        }),
    )


@admin.register(PerfilEmpresa)
class PerfilEmpresaAdmin(admin.ModelAdmin):
    """Administración de perfiles de empresa"""
    list_display = ['nombre_empresa', 'cif', 'sector', 'validado', 'fecha_registro']
    list_filter = ['validado', 'sector', 'fecha_registro']
    search_fields = ['nombre_empresa', 'cif']
    readonly_fields = ['fecha_registro']

    fieldsets = (
        ('Informació bàsica', {
            'fields': ('user', 'nombre_empresa', 'cif', 'sector')
        }),
        ('Contacte i ubicació', {
            'fields': ('direccion', 'web', 'logo')
        }),
        ('Descripció', {
            'fields': ('descripcion',)
        }),
        ('Estat', {
            'fields': ('validado', 'fecha_registro')
        }),
    )

    actions = ['validar_empresas', 'invalidar_empresas']

    def validar_empresas(self, request, queryset):
        queryset.update(validado=True)
        self.message_user(request, f"{queryset.count()} empreses validades correctament.")

    validar_empresas.short_description = "Validar empreses seleccionades"

    def invalidar_empresas(self, request, queryset):
        queryset.update(validado=False)
        self.message_user(request, f"{queryset.count()} empreses invalidades.")

    invalidar_empresas.short_description = "Invalidar empreses seleccionades"


@admin.register(PerfilAlumno)
class PerfilAlumnoAdmin(admin.ModelAdmin):
    """Administración de perfiles de alumno"""
    list_display = ['nom_complet', 'cicle', 'any_graduacio', 'disponibilitat', 'fecha_registro']
    list_filter = ['cicle', 'any_graduacio', 'disponibilitat', 'fecha_registro']
    search_fields = ['nom_complet', 'user__email']
    readonly_fields = ['fecha_registro']

    fieldsets = (
        ('Informació bàsica', {
            'fields': ('user', 'nom_complet', 'foto_perfil')
        }),
        ('Formació', {
            'fields': ('cicle', 'any_graduacio')
        }),
        ('Curriculum i enllaços', {
            'fields': ('cv', 'linkedin', 'github')
        }),
        ('Competències', {
            'fields': ('competencies', 'idiomes', 'disponibilitat')
        }),
        ('Registre', {
            'fields': ('fecha_registro',)
        }),
    )


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    """Administración de ofertas de trabajo"""
    list_display = ['titulo', 'empresa', 'modalidad', 'tipo_contrato', 'validada', 'activa', 'fecha_publicacion']
    list_filter = ['validada', 'activa', 'modalidad', 'tipo_contrato', 'fecha_publicacion']
    search_fields = ['titulo', 'descripcion', 'empresa__nombre_empresa']
    readonly_fields = ['fecha_publicacion']
    date_hierarchy = 'fecha_publicacion'

    fieldsets = (
        ('Informació bàsica', {
            'fields': ('empresa', 'titulo', 'descripcion', 'requisitos')
        }),
        ('Detalls del treball', {
            'fields': ('modalidad', 'tipo_contrato', 'ubicacion', 'salario')
        }),
        ('Dates', {
            'fields': ('fecha_publicacion', 'fecha_cierre')
        }),
        ('Estat', {
            'fields': ('activa', 'validada')
        }),
    )

    actions = ['validar_ofertas', 'invalidar_ofertas', 'desactivar_ofertas']

    def validar_ofertas(self, request, queryset):
        queryset.update(validada=True)
        self.message_user(request, f"{queryset.count()} ofertes validades correctament.")

    validar_ofertas.short_description = "Validar ofertes seleccionades"

    def invalidar_ofertas(self, request, queryset):
        queryset.update(validada=False)
        self.message_user(request, f"{queryset.count()} ofertes invalidades.")

    invalidar_ofertas.short_description = "Invalidar ofertes seleccionades"

    def desactivar_ofertas(self, request, queryset):
        queryset.update(activa=False)
        self.message_user(request, f"{queryset.count()} ofertes desactivades.")

    desactivar_ofertas.short_description = "Desactivar ofertes seleccionades"


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    """Administración de inscripciones"""
    list_display = ['alumno', 'oferta', 'estado', 'fecha_inscripcion']
    list_filter = ['estado', 'fecha_inscripcion']
    search_fields = ['alumno__nom_complet', 'oferta__titulo']
    readonly_fields = ['fecha_inscripcion']
    date_hierarchy = 'fecha_inscripcion'

    fieldsets = (
        ('Inscripció', {
            'fields': ('alumno', 'oferta', 'fecha_inscripcion')
        }),
        ('Estat i carta', {
            'fields': ('estado', 'carta_presentacion')
        }),
    )


# Configuración del sitio admin
admin.site.site_header = "Borsa de Treball - Institut Pla de l'Estany"
admin.site.site_title = "Borsa Admin"
admin.site.index_title = "Panell d'administració"   