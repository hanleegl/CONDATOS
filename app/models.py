from django.contrib.auth.models import User
from django.urls.base import reverse
from datetime import datetime
from django.db import models

# Create your models here.

# OSDE ===================================================================================================
class Osde(models.Model):
    siglas_osde=models.CharField(max_length=50, unique=True)
    nombre_osde=models.CharField(max_length=50, unique=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.siglas_osde
    
    def get_absolute_url(self):
        return reverse('listar_osde')
    
    class Meta:
        verbose_name = 'Osde'
        verbose_name_plural = 'Osdes'

# ENTIDAD ================================================================================================
class Entidad(models.Model):
    nombre_entidad=models.CharField(max_length=200, unique=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_entidad
    
    def get_absolute_url(self):
        return reverse('listar_entidad')
    
    class Meta:
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'

# SOFTWARE ===============================================================================================
class Software(models.Model):
    nombre_software=models.CharField(max_length=100, unique=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_software
    
    def get_absolute_url(self):
        return reverse('listar_software')
    
    class Meta:
        verbose_name = 'Software'
        verbose_name_plural = 'Softwares'

# SERVICIO ===============================================================================================
class Servicio(models.Model):
    nombre_servicio=models.CharField(max_length=100, unique=True)
    costo=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_servicio
    
    def get_absolute_url(self):
        return reverse('listar_servicio')
    
    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

# CONTRATO ===============================================================================================
class Contrato(models.Model):
    concepto = (
        ('Venta de Mercancia', 'Venta de Mercancia'), 
        ('Venta de Servicio', 'Venta de Servicio'),
    )
    tipo_base_datos = (
        ('Dinamica', 'Dinamica'),
        ('Consolidadora', 'Consolidadora'), 
    )
    osde = models.ForeignKey(Osde, on_delete=models.CASCADE)
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    software = models.ForeignKey(Software, on_delete=models.CASCADE)   
    convenio = models.CharField(max_length=100, null=True, blank=True)
    concepto = models.CharField(choices=concepto, max_length=100)
    tipo_base_datos = models.CharField(choices=tipo_base_datos, max_length=100, null=True, blank=True)
    cantidad_base_datos = models.PositiveIntegerField(default=0, null=True, blank=True)
    vencimiento_licencia = models.DateField(default=datetime.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.entidad

    def get_absolute_url(self):
        return reverse('listar_contrato')
 
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

# TRABAJO ================================================================================================
class Trabajo_Imp(models.Model):
    unidades = (
        ('U', 'U'), 
        ('HR', 'HR'),
        ('MES', 'MES'),
    )
    
    fecha = models.DateField(default=datetime.now)
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    unidad_medida = models.CharField(choices=unidades, max_length=10, verbose_name='U/M')
    cantidad = models.PositiveIntegerField(default=0)
    implantador = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.entidad

    def get_absolute_url(self):
        return reverse('listar_trabajo_imp')

    @property
    def costo_total(self):
        return (self.servicio.costo * self.cantidad)
    
    def save(self):
        self.total = self.costo_total
        super (Trabajo_Imp, self).save()
    
    class Meta:
        verbose_name = 'Trabajo_Implantador'
        verbose_name_plural = 'Trabajos_Implantadores'

class Trabajo_Ofi(models.Model):
    unidades = (
        ('U', 'U'), 
        ('HR', 'HR'),
        ('MES', 'MES'),
    )
    
    fecha = models.DateField(default=datetime.now)
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    unidad_medida = models.CharField(choices=unidades, max_length=10, verbose_name='U/M')
    cantidad = models.PositiveIntegerField(default=0)
    ofimatico = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.entidad

    def get_absolute_url(self):
        return reverse('listar_trabajo_ofi')

    @property
    def costo_total(self):
        return (self.servicio.costo * self.cantidad)
    
    def save(self):
        self.total = self.costo_total
        super (Trabajo_Ofi, self).save()
    
    class Meta:
        verbose_name = 'Trabajo_Ofimatico'
        verbose_name_plural = 'Trabajos_Ofimaticos'