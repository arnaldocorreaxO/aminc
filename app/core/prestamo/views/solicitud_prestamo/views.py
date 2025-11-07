from datetime import datetime
import json
import math
from django.template.loader import get_template
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView
from regex import template
from weasyprint import HTML

from core.base.models import Empresa
from core.base.views.generics import BaseListView
from core.prestamo.forms import SolicitudPrestamoForm
from core.prestamo.models import ProformaCuota, SituacionSolicitudPrestamo, SolicitudPrestamo
from core.prestamo.procedures import (
    fn_monto_plazo_prestamo,
    sp_alta_solicitud_prestamo,
    sp_generar_proforma_cuota,
)
from core.security.mixins import PermissionMixin

class SolicitudPrestamoList(PermissionRequiredMixin, BaseListView):
    """
    Vista para listar solicitudes de préstamo con búsqueda, ordenamiento y paginación.
    Hereda de BaseListView para aplicar lógica común.
    """
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/list.html"
    permission_required = "view_solicitudprestamo"

    # Campos habilitados para búsqueda textual y numérica
    search_fields = [
        "nro_solicitud",
        "cliente__persona__nombre",
        "cliente__persona__apellido",
    ]
    numeric_fields = ["id", "nro_solicitud"]
    default_order_fields = ["-id"]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Maneja peticiones POST para búsqueda AJAX.
        """
        action = request.POST.get("action", "")
        if action == "search":
            return self.handle_search(request)
        return JsonResponse({"error": "No ha ingresado una opción válida"}, status=400)

    def get_context_data(self, **kwargs):
        """
        Agrega variables al contexto de la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("solicitud_prestamo_create")
        context["title"] = "Listado de Solicitudes de Préstamo"
        return context


class SolicitudPrestamoCreate(PermissionMixin,CreateView):
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/create.html"
    form_class = SolicitudPrestamoForm
    success_url = reverse_lazy("solicitud_prestamo_list")
    permission_required = "add_solicitudprestamo"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {"valid": True}
        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            print("*" * 100)
            print(type)
            print(obj)
            print("*" * 100)
            if type == "cliente":
                if SolicitudPrestamo.objects.filter(
                    Q(cliente_id=obj)
                    & Q(situacion_solicitud__estado__in=["INIC", "PEND"])
                ):
                    data["valid"] = False
        except Exception as e:
            print(str(e))
            data["error"] = str(e)

        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        print(action)
        try:
            if action == "add":
                # RETORNA EL NRO. DE SOLICITUD GENERADA
                data = sp_alta_solicitud_prestamo(request)
                if data["rtn"] == 0:
                    data["msg"] += "<br> NRO. DE SOLICITUD " + data["val"]
                # CONCATENAMOS DICCIONARIO
                # data.update(data_proc)
            elif action == "validate_data":
                return self.validate_data()
            elif action == "search_proforma_cuota":
                data = generar_proforma_cuota(request)
            elif action == "search_plazo_monto":
                data = fn_monto_plazo_prestamo(request)
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(
            json.dumps(data, default=str), content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["title"] = "Nuevo registro de Solicitud de Préstamo"
        context["action"] = "add"
        return context


class SolicitudPrestamoUpdate(PermissionMixin, UpdateView):
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/create.html"
    form_class = SolicitudPrestamoForm
    success_url = reverse_lazy("solicitud_prestamo_list")
    permission_required = "change_solicitudprestamo"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {"valid": True}
        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            id = self.get_object().id
            if type == "denominacion":
                if SolicitudPrestamo.objects.filter(denominacion__iexact=obj).exclude(
                    id=id
                ):
                    data["valid"] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "edit":
                data = self.get_form().save()
                data["rtn"] = 0
                data["msg"] = "OK"
            elif action == "validate_data":
                return self.validate_data()
            elif action == "search_proforma_cuota":
                data = generar_proforma_cuota(request)
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["title"] = "Edición de una Solicitud de Préstamo"
        context["action"] = "edit"
        return context


class SolicitudPrestamoDelete(PermissionMixin, DeleteView):
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/delete.html"
    success_url = reverse_lazy("solicitud_prestamo_list")
    permission_required = "delete_solicitudprestamo"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Notificación de eliminación"
        context["list_url"] = self.success_url
        return context


def generar_proforma_cuota(request):
    proforma = sp_generar_proforma_cuota(request)
    print(proforma)
    if proforma["rtn"] == 0:
        data = []
        nro_solicitud = (
            request.POST["nro_solicitud"] if request.POST["nro_solicitud"] else None
        )
        # print("*" * 100)
        # print(nro_solicitud)
        # print("*" * 100)
        search = ProformaCuota.objects.filter(
            Q(solicitud_prestamo=nro_solicitud) & Q(usu_insercion=request.user.cod_usuario)
        )
        total_interes = 0
        monto_prestamo = 0
        monto_refinanciado = 0  # Acá debemos recuperar el total del monto refinanciado
        monto_neto = 0  # Diferencia entre monto_prestamo - monto_refinanciado
        for p in search:
            item = p.toJSON()
            total_interes += float(item["interes"])
            monto_prestamo += float(item["amortizacion"])
            data.append(item)
        # RETORNAMOS LOS TOTALES EN LA PRIMERA FILA
        data[0]["monto_prestamo"] = monto_prestamo
        data[0]["monto_refinanciado"] = monto_refinanciado
        data[0]["monto_neto"] = monto_prestamo - monto_refinanciado
        data[0]["total_interes"] = total_interes

    else:
        data["error"] = str(proforma["msg"])

    return data



class SeguimientoSolicitudPDFView(View):
    def get(self, request, pk):
        solicitud = get_object_or_404(SolicitudPrestamo, pk=pk)
        situaciones = SituacionSolicitudPrestamo.objects.filter(
            nro_solicitud=solicitud
        ).order_by("fecha", "id")
        empresa = Empresa.objects.first()
        
        template = get_template('solicitud_prestamo/seguimiento_solicitud_pdf.html')
        context = {
            'solicitud': solicitud,
            'situaciones': situaciones,
            'empresa': empresa,
            'now': datetime.now(),
        }
        
        html_template = template.render(context).encode(encoding='UTF-8')

        pdf = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="seguimiento_{solicitud.nro_solicitud}.pdf"'
        return response
