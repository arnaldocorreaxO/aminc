# TRANSACCIONES CABECERA
import json
import math

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView

from core.base.forms import TransaccionBaseForm, TransaccionModalFormView
from core.base.models import Transaccion
from core.base.utils import isNULL
from core.general.models import Cliente
from core.prestamo.forms import SolicitudPrestamoForm, Trx501Form, Trx503Form, Trx504Form
from core.prestamo.models import (
    ProformaCuota,
    SituacionSolicitudPrestamo,
    SolicitudPrestamo,
)
from core.prestamo.procedures import (
    fn_monto_plazo_prestamo,
    sp_alta_solicitud_prestamo,
    sp_generar_proforma_cuota,
    sp_trx503,
    sp_trx504,
)
from core.security.mixins import PermissionMixin


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

#!TRX 501
class Trx501(PermissionRequiredMixin, FormView):
    template_name = "prestamo/transaccion/trx501.html"
    permission_required = "contable.add_movimiento"
    form_class = Trx501Form

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Este usamos para el modal
    def post(self, request, *args, **kwargs):
        data = {}
        print("501TRX" * 100)
        action = request.POST["action"]
        print(request.POST)
        try:
            if action == "load_form":
                if request.user.has_perm("contable.add_movimiento"):
                    # fec_movimiento = request.POST["fec_movimiento"]
                    # cod_movimiento = request.POST["cod_movimiento"]
                    # nro_documento = request.POST["nro_recibo"].split("/")
                    # cod_cliente = request.POST["cod_cliente"]
                    cod_cliente = 2973
                    print(request.POST)
                    if cod_cliente:
                        solicitud = SolicitudPrestamo.objects.filter(
                            cliente__cod_cliente__iexact=cod_cliente
                        )
                        print(solicitud)
                        situacion_solicitud = SituacionSolicitudPrestamo.objects.filter(
                            activo=True
                        )
                        print(situacion_solicitud)

                        form = self.form_class
                        context = self.get_context_data()
                        context["form"] = form
                        context["action"] = "trx"
                        context["action_url"] = reverse_lazy("trx501_create")
                        # data["data"] = promocion.toJSON()
                        data["html_form"] = render_to_string(
                            self.template_name, context, request=request
                        )
                        data
                    else:
                        data[
                            "error"
                        ] = "Debe selecccionar un socio para esta transaccion"

                else:
                    data["error"] = "No tiene permisos para editar"

            elif action == "trx":
                data = sp_trx503(request)

        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(
            json.dumps(data, default=str), content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #!VERIFICAR
        context["create_url"] = reverse_lazy("trx_caja_create")
        context["title"] = "DESEMBOLSO DE PRESTAMOS"
        return context


class Trx503(TransaccionModalFormView):
    template_name = "prestamo/transaccion/trx503.html"
    form_class = Trx503Form
    permission_required = "contable.add_movimiento"
    action_url = reverse_lazy("trx503_create")
    titulo = "RESOLUCIÓN DE PRÉSTAMOS"

    def handle_search(self, request):
        cod_cliente = request.POST.get("cod_cliente")
        if not cod_cliente:
            return {"error": "Debe seleccionar un socio para esta transacción"}

        solicitudes = SolicitudPrestamo.objects.filter(
            cliente__cod_cliente__iexact=cod_cliente
        )
        situaciones = SituacionSolicitudPrestamo.objects.filter(activo=True)

        return {
            "solicitudes": [s.toJSON() for s in solicitudes],
            "situaciones": [s.toJSON() for s in situaciones],
        }

    def handle_trx(self, request):
        return sp_trx503(request)

# #!TRX 503
# class Trx503(PermissionRequiredMixin, FormView):
#     template_name = "prestamo/transaccion/trx503.html"
#     permission_required = "contable.add_movimiento"
#     form_class = Trx503Form

#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

#     # Este usamos para el modal
#     def post(self, request, *args, **kwargs):
#         data = {}
#         print("503TRX" * 100)
#         action = request.POST["action"]
#         print(request.POST)
#         try:
#             if action == "load_form":
#                 if request.user.has_perm("contable.add_movimiento"):
#                     # fec_movimiento = request.POST["fec_movimiento"]
#                     # cod_movimiento = request.POST["cod_movimiento"]
#                     # nro_documento = request.POST["nro_recibo"].split("/")
#                     # cod_cliente = request.POST["cod_cliente"]
#                     cod_cliente = 2973
#                     print(request.POST)
#                     if cod_cliente:
#                         solicitud = SolicitudPrestamo.objects.filter(
#                             cliente__cod_cliente__iexact=cod_cliente
#                         )
#                         print(solicitud)
#                         situacion_solicitud = SituacionSolicitudPrestamo.objects.filter(
#                             activo=True
#                         )
#                         print(situacion_solicitud)

#                         form = self.form_class
#                         context = self.get_context_data()
#                         context["form"] = form
#                         context["action"] = "trx"
#                         context["action_url"] = reverse_lazy("trx503_create")
#                         # data["data"] = promocion.toJSON()
#                         data["html_form"] = render_to_string(
#                             self.template_name, context, request=request
#                         )
#                         data
#                     else:
#                         data[
#                             "error"
#                         ] = "Debe selecccionar un socio para esta transaccion"

#                 else:
#                     data["error"] = "No tiene permisos para editar"

#             elif action == "trx":
#                 data = sp_trx503(request)

#         except Exception as e:
#             data["error"] = str(e)
#         return HttpResponse(
#             json.dumps(data, default=str), content_type="application/json"
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         #!VERIFICAR
#         context["create_url"] = reverse_lazy("trx_caja_create")
#         context["title"] = "RESOLUCION DE PRESTAMOS"
#         return context



# 🔐 Vista institucional para ejecutar la transacción TRX 504 (Liquidación de préstamos)
# Hereda de TransaccionModalFormView para centralizar lógica de carga, búsqueda y ejecución

class Trx504(TransaccionModalFormView):
    template_name = "prestamo/transaccion/trx504.html"
    form_class = Trx504Form
    permission_required = "contable.add_movimiento"
    action_url = reverse_lazy("trx504_create")
    titulo = "LIQUIDACIÓN DE PRÉSTAMOS"

    # 🔍 Método personalizado para buscar una solicitud de préstamo por número
    # Devuelve los datos en formato JSON para ser usados en el frontend

    def handle_search(self, request):
        nro = request.POST.get("solicitud_prestamo")
        solicitud = SolicitudPrestamo.objects.filter(nro_solicitud=nro).first()
        return solicitud.toJSON() if solicitud else {}
    
    # ⚙️ Método que ejecuta la lógica contable de TRX 504
    # Llama al procedimiento almacenado que realiza la liquidación

    def handle_trx(self, request):
        return sp_trx504(request)


# #!TRX 504
# class Trx504(PermissionRequiredMixin, FormView):
#     template_name = "prestamo/transaccion/trx504.html"
#     permission_required = "contable.add_movimiento"
#     form_class = Trx504Form

#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

#     # Este usamos para el modal
#     def post(self, request, *args, **kwargs):
#         data = {}
#         print("504TRX_" * 100)
#         action = request.POST["action"]
#         print(request.POST)
#         try:
#             if action == "load_form":
#                 if request.user.has_perm("contable.add_movimiento"):
#                     print(request.POST)

#                     form = self.form_class
#                     context = self.get_context_data()
#                     context["form"] = form
#                     context["action"] = "trx"
#                     context["action_url"] = reverse_lazy("trx504_create")
#                     # data["data"] = promocion.toJSON()
#                     data["html_form"] = render_to_string(
#                         self.template_name, context, request=request
#                     )
#                     data

#                 else:
#                     data["error"] = "No tiene permisos para editar"

#             elif action == "search":
#                 data = []
#                 solicitud_prestamo = request.POST["solicitud_prestamo"]
#                 data = (
#                     SolicitudPrestamo.objects.filter(nro_solicitud=solicitud_prestamo)
#                     .first()
#                     .toJSON()
#                 )

#             elif action == "trx":
#                 data = sp_trx504(request)

#         except Exception as e:
#             data["error"] = str(e)
#         return HttpResponse(
#             json.dumps(data, default=str), content_type="application/json"
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         #!VERIFICAR
#         context["create_url"] = reverse_lazy("trx_caja_create")
#         context["title"] = "LIQUIDACION DE PRESTAMOS"
#         return context
