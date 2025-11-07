# TRANSACCIONES CABECERA
import json


from django.contrib.auth.mixins import PermissionRequiredMixin


from django.http import HttpResponse

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import  FormView
from core.base.forms import TransaccionBaseForm, TransaccionModalFormView
from core.general.models import Cliente
from core.prestamo.forms import Trx501Form, Trx503Form, Trx504Form
from core.prestamo.models import SolicitudPrestamo
from core.prestamo.procedures import (
	sp_trx501,
	sp_trx503,
	sp_trx504,
)

# Busquedas transaccionales generales reñacionadas a préstamos
def buscar_transaccional(post):	
    if "cod_cliente" in post:
        cliente = Cliente.objects.filter(cod=post["cod_cliente"]).first()
        if not cliente:
            return {"error": f"No se encontró el cliente con código {post['cod_cliente']}"}
        return cliente.toJSON()

    if "solicitud_prestamo" in post:
        solicitud = SolicitudPrestamo.objects.filter(nro_solicitud=post["solicitud_prestamo"]).first()
        if not solicitud:
            return {"error": f"No se encontró la solicitud N° {post['solicitud_prestamo']}"}
        return solicitud.toJSON()

    return {"error": "Debe enviar request.POST con parámetros válidos"}


# 🔐 Vista para transacciones del módulo de préstamos
# No guarda datos, solo inicializa el formulario con contexto institucional
class TransaccionPrestamoFormView(PermissionRequiredMixin, FormView):
	# 🧩 Template base compartido por todos los módulos de transacción
	template_name = "base/transaccion/create.html"

	# 🧾 Formulario base que se adapta según el módulo y tipo de acceso
	form_class = TransaccionBaseForm

	# 🔐 Permiso requerido para acceder a la vista
	permission_required = "contable.add_movimiento"

	# 🛡️ Exime la protección CSRF para permitir llamadas AJAX desde el frontend
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	# 📦 Inyecta parámetros personalizados al formulario base
	# Permite que el formulario se adapte dinámicamente al módulo "PR" (Préstamo)
	# y al tipo de acceso "D" (Diario)
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs.update({
			"request": self.request,   # Contexto del usuario autenticado
			"modulo": "PR",            # Código institucional del módulo
			"tipo_acceso": "D",        # Tipo de acceso contable (Diario)
		})
		return kwargs

	# 📮 Método POST institucional
	# No guarda datos, solo estructura la respuesta para futuras extensiones
	def post(self, request, *args, **kwargs):
		action = request.POST["action"]  # Acción enviada desde el frontend
		data = {}  # Diccionario de respuesta
		try:
			pass  # No se realiza ninguna operación de guardado
		except Exception as e:
			data["error"] = str(e)  # Captura de errores institucional
		return HttpResponse(json.dumps(data), content_type="application/json")

	# 🧠 Contexto adicional para el template
	# Define el título institucional de la vista
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["title"] = "Transacciones del Módulo de Préstamos"
		return context

# Transacción TRX 501 - Desembolso de Préstamos
# class Trx501(TransaccionModalFormView,PermissionRequiredMixin):
class Trx501(TransaccionModalFormView):
	template_name = "prestamo/transaccion/trx501.html"
	form_class = Trx501Form
	permission_required = "contable.add_movimiento"
	action_url = reverse_lazy("trx501_create")
	titulo = "DESEMBOLSO DE PRÉSTAMOS"

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	# 🔍 Método personalizado para buscar datos relacionados a la solicitud de préstamo
	def handle_search(self, request):
		pass
	# ⚙️ Método que ejecuta la lógica contable de TRX 501
	def handle_trx(self, request):
		return sp_trx501(request)

# Transacción TRX 503 - Resolución de Préstamos
class Trx503(TransaccionModalFormView,PermissionRequiredMixin):
	template_name = "prestamo/transaccion/trx503.html"
	form_class = Trx503Form
	permission_required = "contable.add_movimiento"
	action_url = reverse_lazy("trx503_create")
	titulo = "RESOLUCIÓN DE PRÉSTAMOS"

	# 🔍 Método personalizado para buscar datos relacionados a la solicitud de préstamo
	def handle_search(self, request):
		return buscar_transaccional(request.POST)
	
	# ⚙️ Método que ejecuta la lógica contable de TRX 503
	def handle_trx(self, request):
		return sp_trx503(request)

# Transacción TRX 504 - Liquidación de Préstamos
class Trx504(TransaccionModalFormView,PermissionRequiredMixin):
	template_name = "prestamo/transaccion/trx504.html"
	form_class = Trx504Form
	permission_required = "contable.add_movimiento"
	action_url = reverse_lazy("trx504_create")
	titulo = "LIQUIDACIÓN DE PRÉSTAMOS"
	
	# 🔍 Método personalizado para buscar datos relacionados a la solicitud de préstamo
	def handle_search(self, request):
		nro = request.POST.get("solicitud_prestamo")
		solicitud = SolicitudPrestamo.objects.filter(nro_solicitud=nro).first()
		return solicitud.toJSON() if solicitud else {}
	
	# ⚙️ Método que ejecuta la lógica contable de TRX 504
	def handle_trx(self, request):
		return sp_trx504(request)

