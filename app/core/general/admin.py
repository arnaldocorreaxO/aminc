from django.contrib import admin

from core.base.admin import ModeloAdminBase
from core.general.models import *

admin.site.register(Plazo, ModeloAdminBase)
admin.site.register(CalificacionCliente, ModeloAdminBase)
admin.site.register(EstadoCliente, ModeloAdminBase)
admin.site.register(TipoBanco, ModeloAdminBase)
admin.site.register(Banco, ModeloAdminBase)
admin.site.register(CuentaBanco, ModeloAdminBase)
