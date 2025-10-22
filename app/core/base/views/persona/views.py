import json
import json as simplejson
import math
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.base.forms import Persona, PersonaForm
from core.base.models import Barrio, Ciudad
from core.base.procedures import sp_identificaciones
from core.base.utils import YYYY_MM_DD, get_fecha_actual, isNULL
from core.security.mixins import PermissionMixin

# MSSQL
def get_datos_persona(request):
    # import pdb; pdb.set_trace()
    data = str(request.GET.get("ci", "X"))
    # print("*" * 10)
    # print(vCi)
    persona = sp_identificaciones(ci=data)
    # print(persona)
    return HttpResponse(simplejson.dumps(persona), content_type="application/json")


# class PersonaList(PermissionMixin, ListView):
#     model = Persona
#     template_name = "persona/list.html"
#     permission_required = "view_persona"

#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["create_url"] = reverse_lazy("persona_create")
#         context["title"] = "Listado de Personas"
#         return context


class PersonaList(ListView):
    model = Persona
    template_name = "persona/list.html"
    permission_required = "view_persona"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        # print(request.POST)
        action = request.POST["action"]

        try:
            if action == "search":
                data = []

                _start = request.POST["start"]
                _length = request.POST["length"]
                _search = request.POST["search[value]"]

                _order = []

                for i in range(9):
                    _column_order = f"order[{i}][column]"
                    # print('Column Order:',_column_order)
                    if _column_order in request.POST:
                        _column_number = request.POST[_column_order]
                        _order.append(
                            request.POST[f"columns[{_column_number}][data]"].split(".")[
                                0
                            ]
                        )
                    if f"order[{i}][dir]" in request.POST:
                        _dir = request.POST[f"order[{i}][dir]"]
                        if _dir == "desc":
                            _order[i] = f"-{_order[i]}"

                _where = "1 = 1"
                qs = Persona.objects.filter().extra(where=[_where]).order_by(*_order)
                if len(_search):
                    if _search.isnumeric():
                        qs.filter(Q(id__exact=_search) | Q(ci__exact=_search))
                    else:
                        qs = (
                            qs.filter(
                                Q(nombre__icontains=_search)
                                | Q(apellido__icontains=_search)
                            )
                            .exclude(activo=False)
                            .order_by("id")
                        )

                # print(_where)

                total = qs.count()
                print(total)

                if _start and _length:
                    start = int(_start)
                    length = int(_length)
                    page = math.ceil(start / length) + 1
                    per_page = length

                if _length == "-1":
                    qs = qs[start:]
                else:
                    qs = qs[start : start + length]

                position = start + 1
                for i in qs:
                    item = i.toJSON()
                    # item['position'] = position
                    data.append(item)
                    position += 1

                data = {
                    "data": data,
                    "page": page,  # [opcional]
                    "per_page": per_page,  # [opcional]
                    "recordsTotal": total,
                    "recordsFiltered": total,
                }
            else:
                data["error"] = "No ha ingresado una opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(
            json.dumps(data, default=str), content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("persona_create")
        context["title"] = "Listado de Personas"
        return context



class PersonaCreate(PermissionMixin, CreateView):
    model = Persona
    template_name = "persona/create.html"
    form_class = PersonaForm
    success_url = reverse_lazy("persona_list")
    permission_required = "add_persona"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {"valid": True}
        type = self.request.POST["type"]
        obj = self.request.POST["obj"].strip()
        print(type)
        print(obj)

        try:
            type = self.request.POST["type"]
            obj = self.request.POST["obj"].strip()
            if type == "ci":
                if Persona.objects.filter(ci__iexact=obj):
                    data["valid"] = False
            if type == "ruc":
                if Persona.objects.filter(ruc__iexact=obj):
                    data["valid"] = False
            if type == "fec_nacimiento":
                fec_nacimiento = datetime.strptime(
                    obj, "%d/%m/%Y"
                )  # Este del from datetime
                edad = relativedelta(get_fecha_actual, fec_nacimiento)
                if edad.years:
                    if abs(edad.years) < 18:
                        data["valid"] = False
                else:
                    data["valid"] = False
        except Exception as e:
            print(str(e))
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "add":
                with transaction.atomic():
                    # INSTANCIAR
                    p = Persona()

                    # OBTENER VALORES
                    ci = isNULL(request.POST["ci"])
                    ruc = isNULL(request.POST["ruc"])
                    nombre = isNULL(request.POST["nombre"])
                    apellido = isNULL(request.POST["apellido"])
                    nacionalidad = isNULL(request.POST["nacionalidad"])
                    ciudad = isNULL(request.POST["ciudad"])
                    barrio = isNULL(request.POST["barrio"])
                    direccion = isNULL(request.POST["direccion"])
                    celular = isNULL(request.POST["celular"])
                    telefono = isNULL(request.POST["telefono"])
                    email = isNULL(request.POST["email"])
                    fec_nacimiento = YYYY_MM_DD(isNULL(request.POST["fec_nacimiento"]))
                    sexo = isNULL(request.POST["sexo"])
                    estado_civil = isNULL(request.POST["estado_civil"])

                    # SETEAR VALORES
                    p.ci = ci
                    p.ruc = ruc
                    p.nombre = nombre
                    p.apellido = apellido
                    p.nacionalidad_id = nacionalidad
                    p.ciudad_id = ciudad
                    p.barrio_id = barrio
                    p.direccion = direccion
                    p.celular = celular
                    p.telefono = telefono
                    p.email = email
                    p.fec_nacimiento = fec_nacimiento
                    p.sexo_id = sexo
                    p.estado_civil_id = estado_civil
                    # GRABAR
                    p.save()
                    data["id"] = p.id

                # data = self.get_form().save()
            elif action == "validate_data":
                return self.validate_data()
            elif action == "search_ciudad":
                data = []
                term = request.POST["term"]
                qs = Ciudad.objects.filter(
                    Q(activo__exact=True)
                    & (
                        Q(departamento__denominacion__icontains=term)
                        | Q(denominacion__icontains=term)
                    )
                ).order_by("departamento_id", "denominacion")[0:25]

                data = [{"id": "", "text": "------------"}]
                id_dpto_aux = 0
                for i in qs:
                    if id_dpto_aux != i.departamento_id:
                        data.append(
                            {
                                "text": str(i.departamento),
                                "children": [{"id": i.id, "text": str(i)}],
                            }
                        )
                    else:
                        data.append(
                            {
                                "children": [{"id": i.id, "text": str(i)}],
                            }
                        )
                    id_dpto_aux = i.departamento_id
                print(data)
            elif action == "search_barrio":
                data = [{"id": "", "text": "---------"}]
                ciudad_list = None
                if "id" in request.POST:
                    ciudad_list = [request.POST["id"] if "id" in request.POST else None]

                elif "id[]" in request.POST:
                    ciudad_list = (
                        request.POST.getlist("id[]") if "id[]" in request.POST else None
                    )
                if ciudad_list:
                    for i in Barrio.objects.filter(ciudad_id__in=ciudad_list):
                        data.append(
                            {"id": i.id, "text": str(i), "data": i.ciudad.toJSON()}
                        )
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["title"] = "Nuevo registro de una Persona"
        context["action"] = "add"
        return context


class PersonaUpdate(PermissionMixin, UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = "persona/create.html"

    success_url = reverse_lazy("persona_list")
    permission_required = "change_persona"

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
            if type == "ci":
                if Persona.objects.filter(ci__iexact=obj).exclude(id=id):
                    data["valid"] = False
            if type == "ruc":
                if Persona.objects.filter(ruc__iexact=obj).exclude(id=id):
                    data["valid"] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST["action"]
        try:
            if action == "edit":
                with transaction.atomic():
                    # data = self.get_form().save(commit=False)
                    # INSTANCIA
                    p = self.get_object()
                    # OBTENER VALORES
                    ci = isNULL(request.POST["ci"])
                    ruc = isNULL(request.POST["ruc"])
                    nombre = isNULL(request.POST["nombre"])
                    apellido = isNULL(request.POST["apellido"])
                    nacionalidad = isNULL(request.POST["nacionalidad"])
                    ciudad = isNULL(request.POST["ciudad"])
                    barrio = isNULL(request.POST["barrio"])
                    direccion = isNULL(request.POST["direccion"])
                    celular = isNULL(request.POST["celular"])
                    telefono = isNULL(request.POST["telefono"])
                    email = isNULL(request.POST["email"])
                    fec_nacimiento = YYYY_MM_DD(isNULL(request.POST["fec_nacimiento"]))
                    sexo = isNULL(request.POST["sexo"])
                    estado_civil = isNULL(request.POST["estado_civil"])

                    p.ci = ci
                    p.ruc = ruc
                    p.nombre = nombre
                    p.apellido = apellido
                    p.nacionalidad_id = nacionalidad
                    p.ciudad_id = ciudad
                    p.barrio_id = barrio
                    p.direccion = direccion
                    p.celular = celular
                    p.telefono = telefono
                    p.email = email
                    p.fec_nacimiento = fec_nacimiento
                    p.sexo_id = sexo
                    p.estado_civil_id = estado_civil
                    p.save()
                    data["id"] = p.id

            elif action == "validate_data":
                return self.validate_data()
            else:
                data["error"] = "No ha seleccionado ninguna opción"
        except Exception as e:
            data["error"] = str(e)
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.success_url
        context["title"] = "Edición de una Persona"
        context["action"] = "edit"
        return context


class PersonaDelete(PermissionMixin, DeleteView):
    model = Persona
    template_name = "persona/delete.html"
    success_url = reverse_lazy("persona_list")
    permission_required = "delete_persona"

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
