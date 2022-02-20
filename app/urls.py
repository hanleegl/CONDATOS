from django.contrib.auth import views as auth_view
from django.urls import path
from .views import *

urlpatterns = [

# INICIO ========================================================================================================================================================================
    path('', IndexView.as_view(), name='inicio'),

# OSDE ==========================================================================================================================================================================
    path('listar_osde/', OsdeListView.as_view(), name="listar_osde"),
    path('crear_osde/', OsdeCreateView.as_view(), name="crear_osde"),
    path('editar_osde/<int:pk>/', OsdeUpdateView.as_view(), name="editar_osde"),
    path('eliminar_osde/<int:pk>/', OsdeDeleteView.as_view(), name="eliminar_osde"),
    path('listado_osde_csv', reporte_csv_osde, name='listado_osde_csv'),

# ENTIDAD =======================================================================================================================================================================
    path('listar_entidad/', EntidadListView.as_view(), name="listar_entidad"),
    path('crear_entidad/', EntidadCreateView.as_view(), name="crear_entidad"),
    path('editar_entidad/<int:pk>/', EntidadUpdateView.as_view(), name="editar_entidad"),
    path('eliminar_entidad/<int:pk>/', EntidadDeleteView.as_view(), name="eliminar_entidad"),
    path('listado_entidad_csv', reporte_csv_entidad, name='listado_entidad_csv'),

# SOFTWARE ======================================================================================================================================================================
    path('listar_software/', SoftListView.as_view(), name="listar_software"),
    path('crear_software/', SoftCreateView.as_view(), name="crear_software"),
    path('editar_software/<int:pk>/', SoftUpdateView.as_view(), name="editar_software"),
    path('eliminar_software/<int:pk>/', SoftDeleteView.as_view(), name="eliminar_software"),
    path('listado_software_csv', reporte_csv_software, name='listado_software_csv'),

#SERVICIO========================================================================================================================================================================
    path('listar_servicio/', ServicioListView.as_view(), name='listar_servicio'),
    path('crear_servicio/', ServicioCreateView.as_view(), name='crear_servicio'),
    path('editar_servicio/<int:pk>/', ServicioUpdateView.as_view(), name="editar_servicio"),
    path('eliminar_servicio/<int:pk>/', ServicioDeleteView.as_view(), name="eliminar_servicio"),
    path('listado_servicio_csv', reporte_csv_servicio, name='listado_servicio_csv'),

# CONTRATOS =====================================================================================================================================================================
    path('listar_contrato/', ContratoListView.as_view(), name="listar_contrato"),
    path('crear_contrato/', ContratoCreateView.as_view(), name="crear_contrato"),
    path('editar_contrato/<int:pk>/', ContratoUpdateView.as_view(), name="editar_contrato"),
    path('eliminar_contrato/<int:pk>/', ContratoDeleteView.as_view(), name="eliminar_contrato"),
    path('listado_contrato_csv', reporte_csv_contrato, name='listado_contrato_csv'),
    # REPORTE ===================================================================================================================================================================
    path('reporte_licencias/', ReporteLicenciaView.as_view(), name='reporte_licencias'),

#TRABAJO =========================================================================================================================================================================
    # IMPLANTACION ===============================================================================================================================================================
    path('listar_trabajo_imp/', TrabImpListView.as_view(), name='listar_trabajo_imp'),
    path('crear_trabajo_imp/', TrabImpCreateView.as_view(), name='crear_trabajo_imp'),
    path('editar_trabajo_imp/<int:pk>/', TrabImpUpdateView.as_view(), name='editar_trabajo_imp'),
    path('eliminar_trabajo_imp/<int:pk>/', TrabImpDeleteView.as_view(), name='eliminar_trabajo_imp'),
    path('listado_trabajo_imp_csv', reporte_csv_trabajo_implantacion, name='listado_trabajo_imp_csv'),
    path('reporte_trabajo_imp/', ReporteTrabImpView.as_view(), name='reporte_trabajo_imp'),
    # OFIMATICA ==================================================================================================================================================================
    path('listar_trabajo_ofi/', TrabOfiListView.as_view(), name='listar_trabajo_ofi'),
    path('crear_trabajo_ofi/', TrabOfiCreateView.as_view(), name='crear_trabajo_ofi'),
    path('editar_trabajo_ofi/<int:pk>/', TrabOfiUpdateView.as_view(), name='editar_trabajo_ofi'),
    path('eliminar_trabajo_ofi/<int:pk>/', TrabOfiDeleteView.as_view(), name='eliminar_trabajo_ofi'),
    path('listado_trabajo_ofi_csv', reporte_csv_trabajo_ofimatica, name='listado_trabajo_ofi_csv'),
    path('reporte_trabajo_ofi/', ReporteTrabOfiView.as_view(), name='reporte_trabajo_ofi'),

# USUARIO =======================================================================================================================================================================
    path('listar_usuario/', UserListView.as_view(), name="listar_usuario"),
    path('crear_usuario/', UserCreateView.as_view(), name="crear_usuario"),
    path('<int:pk>/editar_usuario/', UserUpdateView.as_view(), name="editar_usuario"),
    path('<int:pk>/eliminar_usuario/', UserDeleteView.as_view(), name="eliminar_usuario"),
    
    path('editar_perfil/', UserProfileView.as_view(), name="editar_perfil"),
    path('password/', PasswordsChangeView.as_view(template_name='registration/password_change.html')),

    path('password_reset/', PasswordsResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_view.PasswordResetDoneView.as_view(template_name='password_reset/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordsResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_view.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'), name='password_reset_complete'),
]