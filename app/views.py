from .forms import OsdeForm, EntidadForm, SoftwareForm, ContratoForm, ServicioForm, TrabImpForm, TrabajoOfiForm, UserCreateForm, UserUpdateForm, UserProfileForm, PasswordsResetForm, SetPasswordsForm, PasswordsChangeForm 
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from .models import Osde, Entidad, Software, Contrato, Servicio, Trabajo_Imp, Trabajo_Ofi
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models.functions import Coalesce
from django.db.models.fields import FloatField
from django.shortcuts import redirect, render
from .mixin import PermissionsRequiredMixin
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
import csv

# Create your views here.
# LOGIN =======================================================================================================================================
class LogView(LoginView):
    template_name = 'registration/login.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('inicio')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        context ['titulo'] = 'CONDATOS | Login'

        return context

# INICIO ======================================================================================================================================
class IndexView(TemplateView):
    template_name = 'index.html'

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = []
        try:
            action = request.POST['action']
            if action == 'get_software_osde_chart':
                data = {
                    'name': 'Software contratados',
                    'colorByPoint': True,
                    'data': self.get_software_osde_chart()
                }

            elif action == 'get_contrato_software_chart':
                data = {
                    'name': 'Total',
                    'colorByPoint': True,
                    'data': self.get_contrato_software_chart()
                }    

            elif action == 'get_ingresos_mes_implantacion_chart':
                data = {
                    'name': 'Ingreso Mensual',
                    'data': self.get_ingresos_mes_implantacion_chart()
                }

            elif action == 'get_ingresos_mensual_implantador_chart':
                data = self.get_ingresos_mensual_implantador_chart()
            
            elif action == 'get_ingresos_mes_ofimatica_chart':
                data = {
                    'name': 'Ingreso Mensual',
                    'data': self.get_ingresos_mes_ofimatica_chart()
                }

            elif action == 'get_ingresos_mensual_ofimatico_chart':
                data = self.get_ingresos_mensual_ofimatico_chart()

            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse (data, safe=False)
    
    def get_software_osde_chart(self):
        data = []        
        for n_o in Osde.objects.all():
            c_o = Contrato.objects.filter(osde=n_o.id).count()
            data.append({
                'name': n_o.siglas_osde,
                'y': c_o,
            })
        return data
    
    def get_contrato_software_chart(self):
        data = []        
        for n_s in Software.objects.all():
            c_s = Contrato.objects.filter(software=n_s.id).count()
            data.append({
                'name': n_s.nombre_software,
                'y': c_s,
            })
        return data

    def get_ingresos_mes_implantacion_chart(self):
        data = []
        año = datetime.now().year
        for meses in range(1,13):
            total = Trabajo_Imp.objects.filter(fecha__year=año, fecha__month=meses).aggregate(r=Coalesce(Sum('total'), 0, output_field=FloatField())).get('r')
            data.append(float(total))
        return data

    def get_ingresos_mensual_implantador_chart(self):
        data = []
        año = datetime.now().year
        for n_i in User.objects.filter(email__startswith='implantacion'):
            for meses in range(1,13):
                total = Trabajo_Imp.objects.filter(fecha__year=año, fecha__month=meses, implantador=n_i.id).aggregate(r=Coalesce(Sum('total'), 0, output_field=FloatField())).get('r')
                data.append({
                    'name': n_i.first_name,
                    'data': float(total),
                })        
        return data
    
    def get_ingresos_mes_ofimatica_chart(self):
        data = []
        año = datetime.now().year
        for meses in range(1,13):
            total = Trabajo_Ofi.objects.filter(fecha__year=año, fecha__month=meses).aggregate(r=Coalesce(Sum('total'), 0, output_field=FloatField())).get('r')
            data.append(float(total))
        return data

    def get_ingresos_mensual_ofimatico_chart(self):
        data = []
        año = datetime.now().year
        for n_i in User.objects.filter(email__startswith='ofimatico'):
            for meses in range(1,13):
                total = Trabajo_Ofi.objects.filter(fecha__year=año, fecha__month=meses, ofimatico=n_i.id).aggregate(r=Coalesce(Sum('total'), 0, output_field=FloatField())).get('r')
                data.append({
                    'name': n_i.first_name,
                    'data': float(total),
                })        
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'CONDATOS | Inicio'
        context ['breadcrumb1'] = 'Dashboard'

        context ['contar_osde'] = Osde.objects.count()
        context ['contar_entidad'] = Entidad.objects.count()
        context ['contar_software'] = Software.objects.count()
        context ['contar_servicios'] = Servicio.objects.count()

        año = datetime.now().year
        context ['total_ingresos_implantacion'] = Trabajo_Imp.objects.filter(fecha__year=año).aggregate(r=Coalesce(Sum('total'), 0, output_field=FloatField())).get('r')
        context ['total_ingresos_ofimatica'] = Trabajo_Ofi.objects.filter(fecha__year=año).aggregate(r=Coalesce(Sum('total'), 0, output_field=FloatField())).get('r')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)[:5]

        return context

# OSDE ========================================================================================================================================
# Listar Osde =================================================================================================================================
class OsdeListView(PermissionsRequiredMixin, ListView):
    permission_required = 'app.view_osde'
    model = Osde
    template_name = 'configuracion/osde/listar_osde.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'OSDE | Listar'
        context ['breadcrumb1'] = 'Osde'
        context ['actualizar'] = reverse_lazy('listar_osde')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Cear Osde ===================================================================================================================================
class OsdeCreateView(PermissionsRequiredMixin, CreateView):
    permission_required = 'app.add_osde'
    model = Osde
    form_class = OsdeForm
    template_name = 'configuracion/osde/crear_osde.html'
    success_url = reverse_lazy('listar_osde')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El OSDE ha sido creado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'OSDE | Crear'
        context ['breadcrumb1'] = 'Osde'
        context ['breadcrumb2'] = 'Crear'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Editar Osde =================================================================================================================================
class OsdeUpdateView(PermissionsRequiredMixin, UpdateView):
    permission_required = 'app.change_osde'
    model = Osde
    form_class = OsdeForm
    template_name = 'configuracion/osde/editar_osde.html'
    success_url = reverse_lazy('listar_osde')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El OSDE ha sido editado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'OSDE | Editar'
        context ['breadcrumb1'] = 'Osde'
        context ['breadcrumb2'] = 'Editar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Eliminar Osde ===============================================================================================================================
class OsdeDeleteView(PermissionsRequiredMixin, DeleteView):
    permission_required = 'app.delete_osde'
    model = Osde
    template_name = 'configuracion/osde/eliminar_osde.html'
    success_url = reverse_lazy('listar_osde')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.object.delete():
            messages.success(request, 'El OSDE ha sido eliminado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'OSDE | Eliminar'
        context ['breadcrumb1'] = 'Osde'
        context ['breadcrumb2'] = 'Eliminar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Reporte_CSV_Osde ============================================================================================================================
def reporte_csv_osde(request):        
    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename="osde.csv"'

    writer = csv.writer(response)

    osde = Osde.objects.all()

    writer.writerow(['No', 'Siglas', 'Osde'])

    for osdes in osde:
        writer.writerow([
            osdes.pk, 
            osdes.siglas_osde, 
            osdes.nombre_osde
            ])

    return response

# ENTIDAD =====================================================================================================================================
# Listar Entidad ==============================================================================================================================
class EntidadListView(PermissionsRequiredMixin, ListView):
    permission_required = 'app.view_entidad'
    model = Entidad
    template_name = 'configuracion/entidad/listar_entidad.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'ENTIDAD | Listar'
        context ['breadcrumb1'] = 'Entidad'
        context ['actualizar'] = reverse_lazy('listar_entidad')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Cear Entidad ================================================================================================================================
class EntidadCreateView(PermissionsRequiredMixin, CreateView):
    permission_required = 'app.add_entidad'
    model = Entidad
    form_class = EntidadForm
    template_name = 'configuracion/entidad/crear_entidad.html'
    success_url = reverse_lazy('listar_entidad')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'La ENTIDAD ha sido creada correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'ENTIDAD | Crear'
        context ['breadcrumb1'] = 'Entidad'
        context ['breadcrumb2'] = 'Crear'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Editar Entidad ==============================================================================================================================
class EntidadUpdateView(PermissionsRequiredMixin, UpdateView):
    permission_required = 'app.change_entidad'
    model = Entidad
    form_class = EntidadForm
    template_name = 'configuracion/entidad/editar_entidad.html'
    success_url = reverse_lazy('listar_entidad')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'La ENTIDAD ha sido editada correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'ENTIDAD | Editar'
        context ['breadcrumb1'] = 'Entidad'
        context ['breadcrumb2'] = 'Editar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Eliminar Entidad ============================================================================================================================
class EntidadDeleteView(PermissionsRequiredMixin, DeleteView):
    permission_required = 'app.delete_entidad'
    model = Entidad
    template_name = 'configuracion/entidad/eliminar_entidad.html'
    success_url = reverse_lazy('listar_entidad')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.object.delete():
            messages.success(request, 'La ENTIDAD ha sido eliminada correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'ENTIDAD | Eliminar'
        context ['breadcrumb1'] = 'Entidad'
        context ['breadcrumb2'] = 'Eliminar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Reporte_CSV_Entidad =========================================================================================================================
def reporte_csv_entidad(request):        
    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename="entidad.csv"'

    writer = csv.writer(response)

    entidad = Entidad.objects.all()

    writer.writerow(['No', 'Nombre'])

    for entidades in entidad:
        writer.writerow([
            entidades.pk, 
            entidades.nombre_entidad
            ])

    return response

# SOFTWARE ====================================================================================================================================
# Listar Software =============================================================================================================================
class SoftListView(PermissionsRequiredMixin, ListView):
    permission_required = 'app.view_software'
    model = Software
    template_name = 'configuracion/software/listar_soft.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'SOFTWARE | Listar'
        context ['breadcrumb1'] = 'Software'
        context ['actualizar'] = reverse_lazy('listar_software')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Cear Software ===============================================================================================================================
class SoftCreateView(PermissionsRequiredMixin, CreateView):
    permission_required = 'app.add_software'
    model = Software
    form_class = SoftwareForm
    template_name = 'configuracion/software/crear_soft.html'
    success_url = reverse_lazy('listar_software')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El SOFTWARE ha sido creado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'SOFTWARE | Crear'
        context ['breadcrumb1'] = 'Software'
        context ['breadcrumb2'] = 'Crear'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Editar Software =============================================================================================================================
class SoftUpdateView(PermissionsRequiredMixin, UpdateView):
    permission_required = 'app.change_software'
    model = Software
    form_class = SoftwareForm
    template_name = 'configuracion/software/editar_soft.html'
    success_url = reverse_lazy('listar_software')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El SOFTWARE ha sido editado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'SOFTWARE | Editar'
        context ['breadcrumb1'] = 'Software'
        context ['breadcrumb2'] = 'Editar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Eliminar Software ===========================================================================================================================
class SoftDeleteView(PermissionsRequiredMixin, DeleteView):
    permission_required = 'app.delete_software'
    model = Software
    template_name = 'configuracion/software/eliminar_soft.html'
    success_url = reverse_lazy('listar_software')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.object.delete():
            messages.success(request, 'La SOFTWARE ha sido eliminado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'SOFTWARE | Eliminar'
        context ['breadcrumb1'] = 'Software'
        context ['breadcrumb2'] = 'Eliminar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Reporte_CSV_Software ========================================================================================================================
def reporte_csv_software(request):        
    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename="software.csv"'

    writer = csv.writer(response)

    software = Software.objects.all()

    writer.writerow(['No', 'Software'])

    for softwares in software:
        writer.writerow([
            softwares.pk, 
            softwares.nombre_software
            ])

    return response

# SERVICIO ====================================================================================================================================
# Listar Servicio =============================================================================================================================
class ServicioListView(PermissionsRequiredMixin, ListView):
    permission_required = 'app.view_servicio'
    model = Servicio
    template_name = 'configuracion/servicio/listar_servicio.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'SERVICIO | Listar'
        context ['breadcrumb1'] = 'Servicio'
        context ['actualizar'] = reverse_lazy('listar_servicio')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Crear Servicio ==============================================================================================================================
class ServicioCreateView(PermissionsRequiredMixin, CreateView):
    permission_required = 'app.add_servicio'
    model = Servicio
    form_class = ServicioForm
    template_name = 'configuracion/servicio/crear_servicio.html'
    success_url = reverse_lazy('listar_servicio')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El SERVICIO ha sido creado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'SERVICIO | Crear'
        context ['breadcrumb1'] = 'Servicio'
        context ['breadcrumb2'] = 'Crear'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Editar Servicio =============================================================================================================================
class ServicioUpdateView(PermissionsRequiredMixin, UpdateView):
    permission_required = 'app.change_servicio'
    model = Servicio
    form_class = ServicioForm
    template_name = 'configuracion/servicio/editar_servicio.html'
    success_url = reverse_lazy('listar_servicio')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El SERVICIO ha sido editado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'SERVICIO | Editar'
        context ['breadcrumb1'] = 'Servicio'
        context ['breadcrumb2'] = 'Editar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Eliminar Servicio ===========================================================================================================================
class ServicioDeleteView(PermissionsRequiredMixin, DeleteView):
    permission_required = 'app.delete_servicio'
    model = Servicio
    template_name = 'configuracion/servicio/eliminar_servicio.html'
    success_url = reverse_lazy('listar_servicio')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.object.delete():
            messages.success(request, 'El SERVICIO ha sido eliminado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'SERVICIO | Eliminar'
        context ['breadcrumb1'] = 'Servicio'
        context ['breadcrumb2'] = 'Eliminar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Reporte_CSV_Servicio ========================================================================================================================
def reporte_csv_servicio(request):        
    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename="servicios.csv"'

    writer = csv.writer(response)

    servicio = Servicio.objects.all()

    writer.writerow(['No', 'Servicios', 'Costo'])

    for servicios in servicio:
        writer.writerow([
            servicios.pk, 
            servicios.servicio, 
            servicios.costo
            ])

    return response

# IMPLANTACION ================================================================================================================================
# Listar Contratos ============================================================================================================================
class ContratoListView(PermissionsRequiredMixin, ListView):
    permission_required = 'app.view_contrato'
    model = Contrato
    template_name = 'implantacion/contrato/listar_contrato.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'CONTRATO | Listar'
        context ['breadcrumb1'] = 'Contrato'
        context ['actualizar'] = reverse_lazy('listar_contrato')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Cear Contratos ==============================================================================================================================
class ContratoCreateView(PermissionsRequiredMixin, CreateView):
    permission_required = 'app.add_contrato'
    model = Contrato
    form_class = ContratoForm
    template_name = 'implantacion/contrato/crear_contrato.html'
    success_url = reverse_lazy('listar_contrato')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El CONTRATO ha sido creado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == '':
                pass
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse (data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'CONTRATO | Crear'
        context ['breadcrumb1'] = 'Contrato'
        context ['breadcrumb2'] = 'Crear'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Editar Contratos ============================================================================================================================
class ContratoUpdateView(PermissionsRequiredMixin, UpdateView):
    permission_required = 'app.change_contrato'
    model = Contrato
    form_class = ContratoForm
    template_name = 'implantacion/contrato/editar_contrato.html'
    success_url = reverse_lazy('listar_contrato')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El CONTRATO ha sido editado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'CONTRATO | Editar'
        context ['breadcrumb1'] = 'Contrato'
        context ['breadcrumb2'] = 'Editar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Eliminar Contratos ==========================================================================================================================
class ContratoDeleteView(PermissionsRequiredMixin, DeleteView):
    permission_required = 'app.delete_contrato'
    model = Contrato
    template_name = 'implantacion/contrato/eliminar_contrato.html'
    success_url = reverse_lazy('listar_contrato')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.object.delete():
            messages.success(request, 'El CONTRATO ha sido eliminado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'CONTRATO | Eliminar'
        context ['breadcrumb1'] = 'Contrato'
        context ['breadcrumb2'] = 'Eliminar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Reporte_CSV_Contrato ========================================================================================================================
def reporte_csv_contrato(request):
    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename="contrato.csv"'

    writer = csv.writer(response)

    contratos = Contrato.objects.all()

    writer.writerow(['No', 'Osde', 'Entidad', 'Software', 'Convenio', 'Concepto', 'Tipo BD', 'Cantidad BD'])

    for contrato in contratos:
        writer.writerow([
                contrato.pk, 
                contrato.osde, 
                contrato.entidad, 
                contrato.software, 
                contrato.convenio, 
                contrato.concepto, 
                contrato.tipo_base_datos, 
                contrato.cantidad_base_datos
                ])

    return response
# Reporte_CSV_Licencia_Filtro =================================================================================================================
class ReporteLicenciaView(TemplateView):
    template_name = 'implantacion/reporte/reporte_licencia.html'

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs): 
        data = []
        if request.method=="POST":
            start_date = request.POST.get('start_date', '')
            end_date = request.POST.get('end_date', '')
        data = self.get_context_data(**kwargs)
        data ['data'] = Contrato.objects.filter(vencimiento_licencia__range = [start_date, end_date])
        return render(request, self.template_name, data)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'CONTRATO | Reporte'
        context ['breadcrumb1'] = 'Reporte de Licencia'
        context ['actualizar'] = reverse_lazy('reporte_licencias')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context

# TRABAJO =====================================================================================================================================
# Listar Trabajo Implantacion =================================================================================================================
class TrabImpListView(PermissionsRequiredMixin, ListView):
    permission_required = 'app.view_trabajo_imp'
    model = Trabajo_Imp
    template_name = 'implantacion/trabajo/listar_trabajo_imp.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_IMP | Listar'
        context ['breadcrumb1'] = 'Trabajo'
        context ['actualizar'] = reverse_lazy('listar_trabajo_imp')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Crear Trabajo Implantacion ==================================================================================================================
class TrabImpCreateView(PermissionsRequiredMixin, CreateView):
    permission_required = 'app.add_trabajo_imp'
    model = Trabajo_Imp
    form_class = TrabImpForm
    template_name = 'implantacion/trabajo/crear_trabajo_imp.html'
    success_url = reverse_lazy('listar_trabajo_imp')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()           
            messages.success(request, 'El TRABAJO ha sido creado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_IMP | Crear'
        context ['breadcrumb1'] = 'Trabajo'
        context ['breadcrumb2'] = 'Crear'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Editar Trabajo Implantacion =================================================================================================================
class TrabImpUpdateView(PermissionsRequiredMixin, UpdateView):
    permission_required = 'app.change_trabajo_imp'
    model = Trabajo_Imp
    form_class = TrabImpForm
    template_name = 'implantacion/trabajo/editar_trabajo_imp.html'
    success_url = reverse_lazy('listar_trabajo_imp')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El TRABAJO ha sido editado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_IMP | Editar'
        context ['breadcrumb1'] = 'Trabajo'
        context ['breadcrumb2'] = 'Editar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Eliminar Trabajo Implantacion ===============================================================================================================
class TrabImpDeleteView(PermissionsRequiredMixin, DeleteView):
    permission_required = 'app.delete_trabajo_imp'
    model = Trabajo_Imp
    template_name = 'implantacion/trabajo/eliminar_trabajo_imp.html'
    success_url = reverse_lazy('listar_trabajo_imp')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.object.delete():
            messages.success(request, 'El TRABAJO ha sido eliminado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_IMP | Eliminar'
        context ['breadcrumb1'] = 'Trabajo'
        context ['breadcrumb2'] = 'Eliminar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Reporte_CSV_Trabajo Implantacion ============================================================================================================
def reporte_csv_trabajo_implantacion(request):        
    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename="trabajo_implantacion.csv"'

    writer = csv.writer(response)

    trabajo = Trabajo_Imp.objects.all()

    writer.writerow(['No', 'Fecha', 'Entidad', 'Servicio', 'Implantador', 'U/M', 'Cantidad', 'Total'])

    for trabajos in trabajo:
        writer.writerow([
            trabajos.pk, 
            trabajos.fecha, 
            trabajos.entidad, 
            trabajos.servicio, 
            trabajos.implantador, 
            trabajos.unidad_medida, 
            trabajos.cantidad, 
            trabajos.total
            ])

    return response
# Reporte_CSV_Trabajo_Filtro Implantacion =====================================================================================================
class ReporteTrabImpView(TemplateView):
    template_name = 'implantacion/reporte/reporte_implantacion.html'

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs): 
        data = []
        if request.method=="POST":
            start_date = request.POST.get('start_date', '')
            end_date = request.POST.get('end_date', '')
        data = self.get_context_data(**kwargs)
        data ['data'] = Trabajo_Imp.objects.filter(fecha__range = [start_date, end_date])
        return render(request, self.template_name, data)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_IMP | Reporte'
        context ['breadcrumb1'] = 'Reporte de Implantacion'
        context ['actualizar'] = reverse_lazy('reporte_trabajo_imp')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context

# Listar Trabajo Ofimatica ====================================================================================================================
class TrabOfiListView(PermissionsRequiredMixin, ListView):
    permission_required = 'app.view_trabajo_ofi'
    model = Trabajo_Ofi
    template_name = 'ofimatica/trabajo/listar_trabajo_ofi.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_OFI | Listar'
        context ['breadcrumb1'] = 'Trabajo'
        context ['actualizar'] = reverse_lazy('listar_trabajo_ofi')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Crear Trabajo Ofimatica =====================================================================================================================
class TrabOfiCreateView(PermissionsRequiredMixin, CreateView):
    permission_required = 'app.add_trabajo_ofi'
    model = Trabajo_Ofi
    form_class = TrabajoOfiForm
    template_name = 'ofimatica/trabajo/crear_trabajo_ofi.html'
    success_url = reverse_lazy('listar_trabajo_ofi')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()           
            messages.success(request, 'El TRABAJO ha sido creado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_OFI | Crear'
        context ['breadcrumb1'] = 'Trabajo'
        context ['breadcrumb2'] = 'Crear'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Editar Trabajo Ofimatica ====================================================================================================================
class TrabOfiUpdateView(PermissionsRequiredMixin, UpdateView):
    permission_required = 'app.change_trabajo_ofi'
    model = Trabajo_Ofi
    form_class = TrabajoOfiForm
    template_name = 'ofimatica/trabajo/editar_trabajo_ofi.html'
    success_url = reverse_lazy('listar_trabajo_ofi')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El TRABAJO ha sido editado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_OFI | Editar'
        context ['breadcrumb1'] = 'Trabajo'
        context ['breadcrumb2'] = 'Editar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Eliminar Trabajo Ofimatica ==================================================================================================================
class TrabOfiDeleteView(PermissionsRequiredMixin, DeleteView):
    permission_required = 'app.delete_trabajo_ofi'
    model = Trabajo_Ofi
    template_name = 'ofimatica/trabajo/eliminar_trabajo_ofi.html'
    success_url = reverse_lazy('listar_trabajo_ofi')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.object.delete():
            messages.success(request, 'El TRABAJO ha sido eliminado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_OFI | Eliminar'
        context ['breadcrumb1'] = 'Trabajo'
        context ['breadcrumb2'] = 'Eliminar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Reporte_CSV_Trabajo =========================================================================================================================
def reporte_csv_trabajo_ofimatica(request):        
    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename="trabajo_ofimatica.csv"'

    writer = csv.writer(response)

    trabajo = Trabajo_Imp.objects.all()

    writer.writerow(['No', 'Fecha', 'Entidad', 'Servicio', 'Ofimatico', 'U/M', 'Cantidad', 'Total'])

    for trabajos in trabajo:
        writer.writerow([
            trabajos.pk, 
            trabajos.fecha, 
            trabajos.entidad, 
            trabajos.servicio, 
            trabajos.ofimatico, 
            trabajos.unidad_medida, 
            trabajos.cantidad, 
            trabajos.total
            ])

    return response
# Reporte_CSV_Trabajo_Filtro ==================================================================================================================
class ReporteTrabOfiView(TemplateView):
    template_name = 'ofimatica/reporte/reporte_ofimatica.html'

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs): 
        data = []
        if request.method=="POST":
            start_date = request.POST.get('start_date', '')
            end_date = request.POST.get('end_date', '')
        data = self.get_context_data(**kwargs)
        data ['data'] = Trabajo_Ofi.objects.filter(fecha__range = [start_date, end_date])
        return render(request, self.template_name, data)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'TRABAJO_OFI | Reporte'
        context ['breadcrumb1'] = 'Reporte de Ofimatica'
        context ['actualizar'] = reverse_lazy('reporte_trabajo_ofi')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context

# USUARIO =====================================================================================================================================
# Listar Usuarios =============================================================================================================================
class UserListView(PermissionsRequiredMixin, ListView):
    permission_required = 'auth.user.view_user'
    model = User
    template_name = 'registration/usuario/listar_usuario.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'USUARIO | Listar'
        context ['contar_usuarios'] = User.objects.count()
        context ['breadcrumb1'] = 'Usuario'
        context ['actualizar'] = reverse_lazy('listar_usuario')

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Cear Usuarios ===============================================================================================================================
class UserCreateView(PermissionsRequiredMixin, CreateView):
    permission_required = 'auth.user.add_user'
    model = User
    form_class = UserCreateForm
    template_name = 'registration/usuario/crear_usuario.html'
    success_url = reverse_lazy('listar_usuario')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El USUARIO ha sido creado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'USUARIO | Crear'
        context ['contar_usuarios'] = User.objects.count()
        context ['breadcrumb1'] = 'Usuario'
        context ['breadcrumb2'] = 'Crear'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Editar Usuarios =============================================================================================================================
class UserUpdateView(PermissionsRequiredMixin, UpdateView):
    permission_required = 'auth.user.change_user'
    model = User
    form_class = UserUpdateForm
    template_name = 'registration/usuario/editar_usuario.html'
    success_url = reverse_lazy('listar_usuario')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'El USUARIO ha sido editado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'USUARIO | Editar'
        context ['contar_usuarios'] = User.objects.count()
        context ['breadcrumb1'] = 'Usuario'
        context ['breadcrumb2'] = 'Editar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context
# Eliminar Usuarios ===========================================================================================================================
class UserDeleteView(PermissionsRequiredMixin, DeleteView):
    permission_required = 'auth.user.delete_user'
    model = User
    template_name = 'registration/usuario/eliminar_usuario.html'
    success_url = reverse_lazy('listar_usuario')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.object.delete():
            messages.success(request, 'El USUARIO ha sido eliminado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'USUARIO | Eliminar'
        context ['contar_usuarios'] = User.objects.count()
        context ['breadcrumb1'] = 'Usuario'
        context ['breadcrumb2'] = 'Eliminar'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context

# Editar Perfil ===============================================================================================================================
class UserProfileView(UpdateView):
    form_class = UserProfileForm
    template_name = 'registration/profile_edit.html'
    success_url = reverse_lazy('inicio')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'Su PERFIL ha sido editado correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'USUARIO | Perfil'
        context ['contar_usuarios'] = User.objects.count()
        context ['breadcrumb1'] = 'Usuario'
        context ['breadcrumb2'] = 'Perfil'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context

    def get_object(self):
        return self.request.user
# Cambiar Contraseña Perfil ===================================================================================================================
class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordsChangeForm
    success_url = reverse_lazy('login')

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, 'Su CONTRASEÑA ha sido cambiada correctamente.')
            return HttpResponseRedirect(self.success_url)
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context ['titulo'] = 'USUARIO | Contraseña'
        context ['contar_usuarios'] = User.objects.count()
        context ['breadcrumb1'] = 'Usuario'
        context ['breadcrumb2'] = 'Contraseña'

        licencia_vencida = timezone.now() - timedelta(days=1)
        context ['contar_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida).count()
        context ['nombre_licencia_vencida'] = Contrato.objects.filter(vencimiento_licencia__lte=licencia_vencida)

        return context

# Reiniciar contraseña ========================================================================================================================
class PasswordsResetView(PasswordResetView):
    form_class = PasswordsResetForm
    template_name='password_reset/password_reset.html'
    success_url = reverse_lazy('password_reset_done')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        context ['titulo'] = 'CONDATOS | Reiniciar'

        return context
# Confirmar contraseña ========================================================================================================================
class PasswordsResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordsForm
    template_name='password_reset/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        context ['titulo'] = 'CONDATOS | Confirmacion'

        return context
