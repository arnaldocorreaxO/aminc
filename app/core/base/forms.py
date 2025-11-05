# 🔧 Django core
from django import forms
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin

# 📦 Utilidades del proyecto
from core.base.utils import get_fecha_actual, get_fecha_actual_ymd
from core.caja.procedures import sp_generar_codigo_movimiento

# 📁 Modelos locales
from .models import *

# 🧮 Otros
import json


# Campo de solo lectura para todos los forms
readonly_fields = [
    "usu_insercion",
    "fec_insercion",
    "usu_modificacion",
    "fec_modificacion",
]


class EmpresaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["denominacion"].widget.attrs["autofocus"] = True
        for form in self.visible_fields():
            form.field.widget.attrs.update(
                {"class": "form-control", "autocomplete": "off"}
            )

    class Meta:
        model = Empresa
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "denominacion": forms.TextInput(attrs={"placeholder": "Ingrese un nombre"}),
            "ruc": forms.TextInput(attrs={"placeholder": "Ingrese un ruc"}),
            "celular": forms.TextInput(
                attrs={"placeholder": "Ingrese un teléfono celular"}
            ),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Ingrese un teléfono convencional"}
            ),
            "email": forms.TextInput(attrs={"placeholder": "Ingrese un email"}),
            "direccion": forms.TextInput(
                attrs={"placeholder": "Ingrese una dirección"}
            ),
            "website": forms.TextInput(
                attrs={"placeholder": "Ingrese una dirección web"}
            ),
            "desc": forms.Textarea(
                attrs={"placeholder": "Ingrese una descripción", "rows": 3, "cols": 3}
            ),
            "iva": forms.TextInput(),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data["error"] = self.errors
        except Exception as e:
            data["error"] = str(e)
        return data


class SucursalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["denominacion"].widget.attrs["autofocus"] = True
        for form in self.visible_fields():
            form.field.widget.attrs.update(
                {"class": "form-control", "autocomplete": "off"}
            )

    class Meta:
        model = Sucursal
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "denominacion": forms.TextInput(attrs={"placeholder": "Ingrese un nombre"}),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Ingrese un teléfono convencional"}
            ),
            "direccion": forms.TextInput(
                attrs={"placeholder": "Ingrese una dirección"}
            ),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data["error"] = self.errors
        except Exception as e:
            data["error"] = str(e)
        return data


class PersonaForm(ModelForm):
    class NacionalidadModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.nacionalidad

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ci"].widget.attrs["autofocus"] = True
        # ESTADO CIVIL
        estado_civil = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia__exact="ESTADO_CIVIL"),
            to_field_name="valor_unico",
            empty_label="(Ninguno)",
        )
        estado_civil.widget.attrs.update({"class": "form-control select2"})
        self.fields["estado_civil"] = estado_civil
        # GENERO
        sexo = forms.ModelChoiceField(
            queryset=RefDet.objects.filter(refcab__cod_referencia__exact="SEXO"),
            to_field_name="valor_unico",
            empty_label="(Ninguno)",
        )
        sexo.widget.attrs.update({"class": "form-control select2"})
        self.fields["sexo"] = sexo
        # NACIONALIDAD
        nacionalidad = self.NacionalidadModelChoiceField(
            queryset=Pais.objects.all(), empty_label="(Ninguno)"
        )
        nacionalidad.widget.attrs.update(
            {"class": "form-control select2", "style": "width: 100%;"}
        )
        self.fields["nacionalidad"] = nacionalidad
        self.fields["ciudad"].queryset = Ciudad.objects.none()
        if self.instance:
            self.fields["ciudad"].queryset = Ciudad.objects.filter(
                id=self.instance.ciudad_id
            )

    class Meta:
        model = Persona
        fields = "__all__"
        exclude = readonly_fields
        widgets = {
            "ci": forms.TextInput(attrs={"placeholder": "Ingrese CI"}),
            "ruc": forms.TextInput(attrs={"placeholder": "Ingrese RUC"}),
            "nombre": forms.TextInput(attrs={"placeholder": "Ingrese nombre"}),
            "apellido": forms.TextInput(attrs={"placeholder": "Ingrese apellido"}),
            # 'nacionalidad': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
            "ciudad": forms.Select(
                attrs={"class": "custom-select select2", "style": "width: 100%;"}
            ),
            "barrio": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            "direccion": forms.TextInput(
                attrs={"placeholder": "Ingrese una dirección"}
            ),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Ingrese un teléfono convencional"}
            ),
            "celular": forms.TextInput(
                attrs={"placeholder": "Ingrese un teléfono celular"}
            ),
            "email": forms.TextInput(attrs={"placeholder": "Ingrese un email"}),
            "fec_nacimiento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "fec_nacimiento",
                    "value": get_fecha_actual_ymd,
                    "data-toggle": "datetimepicker",
                    "data-target": "#fec_nacimiento",
                },
            ),
            "nacionalidad": forms.Select(
                attrs={"class": "form-control select2", "style": "width: 100%;"}
            ),
            # 'estado_civil': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data["error"] = self.errors
        except Exception as e:
            data["error"] = str(e)
        return data

# Formulario base para transacciones
class TransaccionBaseForm(forms.Form):
    
    modulo = forms.CharField(widget=HiddenInput())
    tipo_acceso = forms.CharField(widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.modulo = kwargs.pop("modulo", None)
        self.tipo_acceso = kwargs.pop("tipo_acceso", None)
        super().__init__(*args, **kwargs)

        if self.request:
            self._set_usuario_context()
            self._set_codigo_movimiento()
        
        # Inicializar campos ocultos
        self.fields["modulo"].initial = self.modulo
        self.fields["tipo_acceso"].initial = self.tipo_acceso


    def _set_usuario_context(self):
        user = self.request.user
        self.fields["cod_usuario"].initial = getattr(user, "cod_usuario", "")
        self.fields["usuario"].initial = user
        self.fields["sucursal_id"].initial = getattr(user, "sucursal_id", "")
        self.fields["sucursal"].initial = getattr(user, "sucursal", "")

    def _set_codigo_movimiento(self):
        resultado = sp_generar_codigo_movimiento(self.request)
        cod_movimiento = resultado.get("val") or resultado.get("msg")
        self.fields["cod_movimiento"].initial = cod_movimiento

    fec_movimiento = forms.DateField(
        label="Fecha Movimiento",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control datetimepicker-input",
                "id": "fec_movimiento",
                "value": get_fecha_actual,
                "data-toggle": "datetimepicker",
                "data-target": "#fec_movimiento",
                "disabled": True,
                "style": "font-size: medium",
            },
        ),
    )

    cod_movimiento = forms.CharField(
        label="Código Movimiento",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": True,
                "style": "font-size: medium",
            },
        ),
    )

    cliente = forms.CharField(
        label="Seleccionar Cliente",
        widget=forms.Select(
            attrs={
                "id": "cod_cliente",
                "class": "custom-select select2",
                "style": "width: 100%",
            }
        ),
        required=False,
    )

    cod_usuario = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "disabled": True,
                "style": "font-size: medium",
            },
        ),
        required=False,
    )

    usuario = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "disabled": True,
                "style": "font-size: medium",
            },
        ),
        required=False,
    )

    sucursal_id = forms.CharField(
        label="Sucursal",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "disabled": True,
                "style": "font-size: medium",
            },
        ),
        required=False,
    )

    sucursal = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "disabled": True,
                "style": "font-size: medium",
            },
        ),
        required=False,
    )

    transaccion = forms.CharField(
        label="Seleccionar Transacción",
        widget=forms.Select(
            attrs={
                "id": "transaccion",
                "class": "custom-select select2",
                "style": "width: 100%",
            }
        ),
        required=False,
    )

# 🧱 Clase base para transacciones modales (TRX)
# Centraliza lógica de carga de formulario, ejecución y búsqueda
class TransaccionModalFormView(PermissionRequiredMixin, FormView):
    template_name = None               # Debe ser definido por la subclase
    form_class = None                 # Debe ser definido por la subclase
    permission_required = None       # Debe ser definido por la subclase
    action_url = None                # URL que recibe el submit del formulario
    titulo = None                    # Título institucional para el modal

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get("action", "")
        try:
            if action == "load_form":
                if request.user.has_perm(self.permission_required):
                    context = self.get_context_data()
                    context["form"] = self.form_class()
                    context["action"] = "trx"
                    context["action_url"] = self.action_url
                    data["html_form"] = render_to_string(
                        self.template_name, context, request=request
                    )
                else:
                    data["error"] = "No tiene permisos para ejecutar esta transacción"

            elif action == "search":
                data = self.handle_search(request)

            elif action == "trx":
                data = self.handle_trx(request)

        except Exception as e:
            data["error"] = str(e)

        return HttpResponse(json.dumps(data, default=str), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.titulo or "Transacción Modal"
        return context

    # 🔍 Método opcional para búsquedas personalizadas
    def handle_search(self, request):
        return {"error": "Método de búsqueda no implementado"}

    # ⚙️ Método opcional para ejecutar la transacción
    def handle_trx(self, request):
        return {"error": "Transacción no implementada"}