from django import forms
from django.forms import ModelForm

from core.base.utils import get_fecha_actual, get_fecha_actual_ymd
from core.caja.procedures import sp_generar_codigo_movimiento

from .models import *

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


class TransaccionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        data = {}
        if request:
            cod_usuario = request.user.cod_usuario
            usuario = request.user
            sucursal_id = request.user.sucursal_id
            sucursal = request.user.sucursal

            # GENERAMOS CODIGO DE MOVIMIENTO
            data = sp_generar_codigo_movimiento(request)

            cod_movimiento = data["msg"]
            if data["val"]:
                cod_movimiento = data["val"]

        #         # OBTENEMOS NRO DE FACTURA
        #         data = sp_obt_nro_comprobante(request, tip_comprobante="FCT", operacion="R")
        #         nro_factura = data["val"]
        #         # OBTENEMOS NRO DE RECIBO
        #         data = sp_obt_nro_comprobante(request, tip_comprobante="RCB", operacion="R")
        #         nro_recibo = data["val"]

        # super(TransaccionForm, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        if request:
            self.fields["cod_usuario"].initial = cod_usuario
            self.fields["usuario"].initial = usuario
            self.fields["sucursal_id"].initial = sucursal_id
            self.fields["sucursal"].initial = sucursal
            self.fields["cod_movimiento"].initial = cod_movimiento
            # self.fields["transaccion"].queryset = Transaccion.objects.none()
            # self.fields["transaccion"].queryset = Transaccion.objects.filter(
            # cod_transaccion=502
            # )
            # self.fields["transaccion"].initial = 502
            # self.fields["transaccion"].initial = transaccion

    #     if data:
    #         self.fields["cod_movimiento"].initial = cod_movimiento
    #         self.fields["nro_factura"].initial = nro_factura
    #         self.fields["nro_recibo"].initial = nro_recibo

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
        label="Codigo Movimiento",
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
        label="Seleccionar Transaccion",
        widget=forms.Select(
            attrs={
                "id": "transaccion",
                "class": "custom-select select2",
                "style": "width: 100%",
            }
        ),
        required=False,
    )
    # transaccion = forms.ModelChoiceField(
    #     label="Transaccion",
    #     queryset=Transaccion.objects.filter(activo=True, tipo_acceso="C"),
    #     empty_label="(Todos)",
    #     widget=forms.Select(attrs={"class": "form-control select2"}),
    #     # disabled=True,
    #     # required=False,
    # )
def j():
    pass