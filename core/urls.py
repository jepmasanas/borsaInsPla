from django.urls import path
from . import views

urlpatterns = [
    # Págines públiques
    path('', views.home, name='home'),

    # ===== REGISTRE I VERIFICACIÓ =====
    path('registre/', views.registro, name='registro'),
    path('verificar-email/', views.verificar_email, name='verificar_email'),
    path('reenviar-codi/', views.reenviar_codigo, name='reenviar_codigo'),

    # ===== RECUPERACIÓ DE CONTRASENYA =====
    path('oblidat-contrasenya/', views.olvidaste_contrasenya, name='olvidaste_contrasenya'),
    path('verificar-codi-recuperacio/', views.verificar_codigo_recuperacion, name='verificar_codigo_recuperacion'),
    path('reenviar-codi-recuperacio/', views.reenviar_codigo_recuperacion, name='reenviar_codigo_recuperacion'),
    path('canviar-contrasenya-recuperacio/', views.cambiar_contrasenya_recuperacion,
         name='cambiar_contrasenya_recuperacion'),

    # ===== LOGIN / LOGOUT =====
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard segons rol
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estadistiques/', views.estadisticas, name='estadisticas'),

    # Empresa
    path('empresa/perfil/', views.empresa_perfil, name='empresa_perfil'),
    path('empresa/ofertes/', views.empresa_ofertas, name='empresa_ofertas'),
    path('empresa/oferta/nova/', views.empresa_nueva_oferta, name='empresa_nueva_oferta'),
    path('empresa/oferta/<int:pk>/editar/', views.empresa_editar_oferta, name='empresa_editar_oferta'),
    path('empresa/oferta/<int:pk>/eliminar/', views.empresa_eliminar_oferta, name='empresa_eliminar_oferta'),
    path('empresa/oferta/<int:pk>/candidats/', views.empresa_ver_candidatos, name='empresa_ver_candidatos'),
    path('empresa/inscripcio/<int:pk>/canviar-estat/', views.empresa_cambiar_estado_inscripcion,
         name='empresa_cambiar_estado_inscripcion'),
    path('empresa/inscripcio/<int:inscripcion_id>/descarregar-cv/', views.empresa_descargar_cv,
         name='empresa_descargar_cv'),

    # Alumne
    path('alumne/perfil/', views.alumno_perfil, name='alumno_perfil'),
    path('alumne/ofertes/', views.alumno_ofertas, name='alumno_ofertas'),
    path('alumne/oferta/<int:pk>/', views.alumno_detalle_oferta, name='alumno_detalle_oferta'),
    path('alumne/inscriure-se/<int:pk>/', views.alumno_inscribirse, name='alumno_inscribirse'),
    path('alumne/les-meves-inscripcions/', views.alumno_inscripciones, name='alumno_inscripciones'),
    path('alumne/inscripcio/<int:pk>/cancellar/', views.alumno_cancelar_inscripcion,
         name='alumno_cancelar_inscripcion'),

    # Admin (validacions)
    path('admin-panel/validar-empreses/', views.admin_validar_empresas, name='admin_validar_empresas'),
    path('admin-panel/validar-ofertes/', views.admin_validar_ofertas, name='admin_validar_ofertas'),

    # Notificacions
    path('notificacions/', views.notificaciones_lista, name='notificaciones_lista'),
    path('notificacions/<int:pk>/marcar-llegida/', views.notificacion_marcar_leida, name='notificacion_marcar_leida'),
    path('notificacions/marcar-totes-llegides/', views.notificaciones_marcar_todas_leidas,
         name='notificaciones_marcar_todas_leidas'),
    path('notificacions/<int:pk>/eliminar/', views.notificacion_eliminar, name='notificacion_eliminar'),

    # Ajustos de la conta
    path('configuracio/', views.ajustes, name='ajustes'),
]