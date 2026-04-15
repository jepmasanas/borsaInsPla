from django.urls import path
from . import views

urlpatterns = [
    # Páginas públicas
    path('', views.home, name='home'),

    # ===== REGISTRO Y VERIFICACIÓN =====
    path('registro/', views.registro, name='registro'),
    path('verificar-email/', views.verificar_email, name='verificar_email'),
    path('reenviar-codigo/', views.reenviar_codigo, name='reenviar_codigo'),

    # ===== RECUPERACIÓN DE CONTRASEÑA =====
    path('olvide-contrasenya/', views.olvidaste_contrasenya, name='olvidaste_contrasenya'),
    path('verificar-codigo-recuperacion/', views.verificar_codigo_recuperacion, name='verificar_codigo_recuperacion'),
    path('reenviar-codigo-recuperacion/', views.reenviar_codigo_recuperacion, name='reenviar_codigo_recuperacion'),
    path('cambiar-contrasenya-recuperacion/', views.cambiar_contrasenya_recuperacion,
         name='cambiar_contrasenya_recuperacion'),

    # ===== LOGIN / LOGOUT =====
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard según rol
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),

    # Empresa
    path('empresa/ofertas/', views.empresa_ofertas, name='empresa_ofertas'),
    path('empresa/oferta/nueva/', views.empresa_nueva_oferta, name='empresa_nueva_oferta'),
    path('empresa/oferta/<int:pk>/editar/', views.empresa_editar_oferta, name='empresa_editar_oferta'),
    path('empresa/oferta/<int:pk>/eliminar/', views.empresa_eliminar_oferta, name='empresa_eliminar_oferta'),
    path('empresa/oferta/<int:pk>/candidatos/', views.empresa_ver_candidatos, name='empresa_ver_candidatos'),
    path('empresa/inscripcion/<int:pk>/cambiar-estado/', views.empresa_cambiar_estado_inscripcion,
         name='empresa_cambiar_estado_inscripcion'),
    path('empresa/inscripcion/<int:inscripcion_id>/descargar-cv/', views.empresa_descargar_cv,
         name='empresa_descargar_cv'),

    # Alumno
    path('alumno/perfil/', views.alumno_perfil, name='alumno_perfil'),
    path('alumno/ofertas/', views.alumno_ofertas, name='alumno_ofertas'),
    path('alumno/oferta/<int:pk>/', views.alumno_detalle_oferta, name='alumno_detalle_oferta'),
    path('alumno/inscribirse/<int:pk>/', views.alumno_inscribirse, name='alumno_inscribirse'),
    path('alumno/mis-inscripciones/', views.alumno_inscripciones, name='alumno_inscripciones'),
    path('alumno/inscripcion/<int:pk>/cancelar/', views.alumno_cancelar_inscripcion,
         name='alumno_cancelar_inscripcion'),

    # Admin (validaciones)
    path('admin-panel/validar-empresas/', views.admin_validar_empresas, name='admin_validar_empresas'),
    path('admin-panel/validar-ofertas/', views.admin_validar_ofertas, name='admin_validar_ofertas'),

    # Notificaciones
    path('notificaciones/', views.notificaciones_lista, name='notificaciones_lista'),
    path('notificaciones/<int:pk>/marcar-leida/', views.notificacion_marcar_leida, name='notificacion_marcar_leida'),
    path('notificaciones/marcar-todas-leidas/', views.notificaciones_marcar_todas_leidas,
         name='notificaciones_marcar_todas_leidas'),
    path('notificaciones/<int:pk>/eliminar/', views.notificacion_eliminar, name='notificacion_eliminar'),

    # Ajustes de cuenta
    path('ajustes/', views.ajustes, name='ajustes'),
]