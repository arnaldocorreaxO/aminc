# TRANSACCIONES CABECERA
import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

from core.base.forms import TransaccionBaseForm
from core.base.models import Transaccion
from core.base.utils import isNULL


# API para obtener información de una transacción por su código
def get_transaccion_info(request):
    codigo = request.GET.get("codigo")
    trx = Transaccion.objects.filter(cod_transaccion=codigo).first()
    if trx:
        return JsonResponse(trx.toJSON())
    return JsonResponse({"error": "Transacción no encontrada"}, status=404)

# TRANSACCIONES CABECERA
# El path debe ir siempre con el nombre del modulo principal para
# evitar conflictos con los templates de transacciones de otros modulos
# template_name = "transaccion/base/create.html"
class TransaccionBaseFormView(PermissionRequiredMixin, FormView):
    template_name = "base/transaccion/create.html"
    form_class = TransaccionBaseForm
    permission_required = "contable.add_movimiento"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST["action"]
        print("TRX" * 100)
        print(request.POST)
        data = {}
        try:
            if action == "search_trx_url":
                data = []
                term = request.POST["term"]
                modulo = request.POST["modulo"]
                tipo_acceso = request.POST["tipo_acceso"]  # C = CAJA - D = DIARIO

                transaccion = Transaccion.objects.filter(activo__exact=True)

                if modulo:
                    # Si el modulo que llama es distinto a CAJA = CJ retornamos filtrando modulo y tipo acceso
                    if modulo != "CJ":
                        transaccion = transaccion.filter(
                            (
                                Q(modulo__exact=modulo)
                                & Q(tipo_acceso__exact=tipo_acceso)
                            )
                            | Q(cod_transaccion__in=[3, 4])
                        )
                    # Se está llamando transacciones de tipo acceso C = CAJA (No se filtra por modulo)
                    else:
                        transaccion = transaccion.filter(
                            Q(tipo_acceso__exact=tipo_acceso)
                        )

                if term:
                    transaccion = transaccion.filter(
                        (
                            Q(cod_transaccion__icontains=term)
                            | Q(denominacion__icontains=term)
                        )
                    )

                transaccion = transaccion.order_by("cod_transaccion")[0:10]

                data = [{"id": "", "text": "------------"}]

                for row in transaccion:
                    # Como codigo de cliente no tiene ID, retornamos asi, o sino no funciona SELECT2
                    # una matriz de objetos que contienen, como mínimo, las propiedades 'id' y 'text'
                    item = {}
                    item["id"] = str(row.cod_transaccion) # siempre el codigo como value
                    item["text"] = str(row) # lo que se ve en el select
                    data.append(item)
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form"] = TransaccionBaseForm(request=self.request)
        context["list_url"] = self.success_url
        context["title"] = "Transacciones de Modulos"
        # context["action"] = "add" #LA TRANSACCION PRINCIPAL CABECERA NO TIENE ACTION POR AHORA
        return context
