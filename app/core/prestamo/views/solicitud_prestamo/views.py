from datetime import datetime
import json
from django.template.loader import get_template
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, UpdateView
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
from typing import Any

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
        data:dict[str,Any] = {"valid": True}
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
                ).exists():
                    data["valid"] = False
        except Exception as e:
            print(str(e))
            data["error"] = str(e)

        return JsonResponse(data)

    def post(self, request, *args, **kwargs):

        data: dict[str, Any] = {}
    def post(self, request, *args, **kwargs):

        data: Any = {}
        action = request.POST.get("action", "")
        try:
            if action == "add":
                # RETORNA EL NRO. DE SOLICITUD GENERADA
                result = sp_alta_solicitud_prestamo(request)
                if isinstance(result, dict):
                    data = result
                    if data.get("rtn") == 0:
                        data["msg"] = (data.get("msg", "") or "") + "<br> NRO. DE SOLICITUD " + str(data.get("val", ""))
                else:
                    data = {"error": str(result)}
            elif action == "validate_data":
                return self.validate_data()
            elif action == "search_proforma_cuota":
                result = generar_proforma_cuota(request)
                # generar_proforma_cuota may return a list of items or a dict with error
                if isinstance(result, dict):
                    data = result
                else:
                    data = {"items": result}
            elif action == "search_plazo_monto":
                result = fn_monto_plazo_prestamo(request)
                if isinstance(result, dict):
                    data = result
                else:
                    data = {"result": result}
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(
            json.dumps(data, default=str), content_type="application/json"
        )
        context["list_url"] = self.success_url
        context["title"] = "Nuevo registro de Solicitud de Préstamo"
        context["action"] = "add"
        return context


class SolicitudPrestamoUpdate(PermissionMixin, UpdateView):
    model = SolicitudPrestamo
    template_name = "solicitud_prestamo/create.html"
    form_class = SolicitudPrestamoForm
    success_url = reverse_lazy("solicitud_prestamo_list")
    def validate_data(self):
        data = {"valid": True}
        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            pk = getattr(self.get_object(), "pk", None)
            if type == "denominacion":
                if SolicitudPrestamo.objects.filter(denominacion__iexact=obj).exclude(
                    id=pk
                ).exists():
                    data["valid"] = False
        except:
            pass
        return JsonResponse(data)
                if SolicitudPrestamo.objects.filter(denominacion__iexact=obj).exclude(
    def post(self, request, *args, **kwargs):
        data: Any = {}
        action = request.POST.get("action", "")
        try:
            if action == "edit":
                result = self.get_form().save()
                # save() may return a dict or a model instance; normalize to a dict
                if isinstance(result, dict):
                    data = result
                    data["rtn"] = data.get("rtn", 0)
                    data["msg"] = data.get("msg", "OK")
                else:
                    data = {"rtn": 0, "msg": "OK"}
            elif action == "validate_data":
                return self.validate_data()
            elif action == "search_proforma_cuota":
                result = generar_proforma_cuota(request)
                if isinstance(result, dict):
                    data = result
                else:
                    data = {"items": result}
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")
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
def generar_proforma_cuota(request):
    proforma = sp_generar_proforma_cuota(request)
    # If the procedure returns a dict with rtn == 0 proceed, otherwise return a dict with error
    if isinstance(proforma, dict) and proforma.get("rtn") == 0:
        data_list = []
        nro_solicitud = request.POST.get("nro_solicitud") or None
        search = ProformaCuota.objects.filter(
            Q(solicitud_prestamo=nro_solicitud) & Q(usu_insercion=request.user.cod_usuario)
        )
        total_interes = 0.0
        monto_prestamo = 0.0
        monto_refinanciado = 0.0  # Acá debemos recuperar el total del monto refinanciado
        for p in search:
            item = p.toJSON()
            try:
                total_interes += float(item.get("interes", 0))
            except Exception:
                pass
            try:
                monto_prestamo += float(item.get("amortizacion", 0))
            except Exception:
                pass
            data_list.append(item)
        # RETORNAMOS LOS TOTALES EN LA PRIMERA FILA SI HAY FILAS
        if data_list:
            data_list[0]["monto_prestamo"] = monto_prestamo
            data_list[0]["monto_refinanciado"] = monto_refinanciado
            data_list[0]["monto_neto"] = monto_prestamo - monto_refinanciado
            data_list[0]["total_interes"] = total_interes
        return data_list
    else:
        msg = proforma.get("msg") if isinstance(proforma, dict) else str(proforma)
        return {"error": str(msg)}
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
