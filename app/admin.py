from django.contrib import admin
from .models import *

# Register your models here.

# OSDE =================================================================================
class OsdeAdmin(admin.ModelAdmin):
    readonly_fields=('created', 'updated')

admin.site.register(Osde, OsdeAdmin)

# ENTIDAD =================================================================================
class EntidadAdmin(admin.ModelAdmin):
    readonly_fields=('created', 'updated')

admin.site.register(Entidad, EntidadAdmin)

# SOFTWARE =============================================================================
class SoftwareAdmin(admin.ModelAdmin):
    readonly_fields=('created', 'updated')

admin.site.register(Software, SoftwareAdmin)

# SERVICIO =============================================================================

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre_servicio', 'costo')
    readonly_fields=('created', 'updated')

admin.site.register(Servicio, ServicioAdmin)

# CONTRATO =============================================================================
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('id', 'osde', 'software', 'entidad', 'convenio')
    readonly_fields=('created', 'updated')

admin.site.register(Contrato, ContratoAdmin)

# TRABAJO ==============================================================================

class TrabImpAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'entidad', 'servicio', 'unidad_medida', 'cantidad', 'implantador', 'total')
    readonly_fields=('created', 'updated')

admin.site.register(Trabajo_Imp, TrabImpAdmin)

class TrabOfiAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'entidad', 'servicio', 'unidad_medida', 'cantidad', 'ofimatico', 'total')
    readonly_fields=('created', 'updated')

admin.site.register(Trabajo_Ofi, TrabOfiAdmin)