import json
import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView

from core.base.forms import TransaccionBaseForm
from core.base.models import Transaccion

# API para obtener información de una transacción por su código
def get_transaccion_info(request):
    codigo = request.GET.get("codigo")
    trx = Transaccion.objects.filter(cod_transaccion=codigo).first()
    if trx:
        return JsonResponse(trx.toJSON())
    return JsonResponse({"error": "Transacción no encontrada"}, status=404)


class TransaccionBaseFormView(PermissionRequiredMixin, FormView):
    """
    Vista base para formularios de transacciones contables.
    Permite búsqueda dinámica de transacciones según módulo y tipo de acceso.
    """
    template_name = "base/transaccion/create.html"
    form_class = TransaccionBaseForm
    permission_required = "contable.add_movimiento"
    success_url = reverse_lazy("movimiento_list")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "")
        term = request.POST.get("term", "")
        modulo = request.POST.get("modulo", "")
        tipo_acceso = request.POST.get("tipo_acceso", "")
        data = {}

        print("POST recibido en TransaccionBaseFormView: %s", request.POST)

        try:
            if action == "search_trx_url":
                transacciones = self._buscar_transacciones(term, modulo, tipo_acceso)
                data = [{"id": "", "text": "------------"}] + [
                    {
                        "id": str(t.cod_transaccion),
                        "text": f"{t.cod_transaccion} - {t.denominacion}"
                    }
                    for t in transacciones
                ]
        except Exception as e:
            data["error"] = str(e)

        return HttpResponse(json.dumps(data), content_type="application/json")

    def _buscar_transacciones(self, term, modulo, tipo_acceso):
        qs = Transaccion.objects.filter(activo=True)

        if modulo:
            # Regla especial para módulo de caja si no es caja ( CJ ) filtramos por modulo y tipo de acceso
            if modulo != "CJ":
                qs = qs.filter(
                    Q(modulo=modulo, tipo_acceso=tipo_acceso) |
                    Q(cod_transaccion__in=[3, 4])
                )
            else:
                # Si es módulo de caja ( CJ ), las transacciones con tipo C = CAJA (No se filtra por modulo)
                qs = qs.filter(tipo_acceso=tipo_acceso)

        if term:
            qs = qs.filter(
                Q(cod_transaccion__icontains=term) |
                Q(denominacion__icontains=term)
            )

        return qs.order_by("cod_transaccion")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = TransaccionBaseForm(request=self.request)
        context["list_url"] = self.success_url
        context["title"] = "Transacciones de Módulos"
        return context
