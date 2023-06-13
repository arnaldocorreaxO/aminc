from django import forms
from django.forms import ModelForm

from core.base.models import Transaccion
from core.contable.models import Movimiento
from core.socio.models import PromocionIngreso, Socio, SolicitudIngreso

from .models import *
from .procedures import *


class TransaccionCajaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        data = {}
        if request:
            print(request.user)
            data = sp_generar_codigo_movimiento(request)
            cod_movimiento = data["msg"]
            if data["val"]:
                cod_movimiento = data["val"]

            data = sp_obt_nro_comprobante(request, tip_comprobante="FCT", operacion="R")
            nro_factura = data["val"]
            data = sp_obt_nro_comprobante(request, tip_comprobante="RCB", operacion="R")
            nro_recibo = data["val"]
        super(TransaccionCajaForm, self).__init__(*args, **kwargs)
        if data:
            self.fields["cod_movimiento"].initial = cod_movimiento
            self.fields["nro_factura"].initial = nro_factura
            self.fields["nro_recibo"].initial = nro_recibo

    fec_movimiento = forms.DateField(
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control datetimepicker-input",
                "id": "fec_movimiento",
                "value": datetime.now().strftime("%d/%m/%Y"),
                "data-toggle": "datetimepicker",
                "data-target": "#fec_movimiento",
                "disabled": True,
            },
        )
    )
    cod_movimiento = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": True,
                "style": "font-size: small",
            },
        )
    )
    socio = forms.ModelChoiceField(
        queryset=Socio.objects.filter(activo=True),
        empty_label="(Todos)",
        widget=forms.Select(attrs={"class": "form-control select2"}),
        required=False,
    )
    # socio.widget.attrs.update({"class": "form-control select2"})

    nro_factura = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "disabled": True,
                "style": "font-size: small",
            },
        )
    )
    nro_recibo = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "disabled": True,
                "style": "font-size: small",
            },
        )
    )
    transaccion = forms.ModelChoiceField(
        queryset=Transaccion.objects.filter(activo=True, tipo_acceso="C"),
        empty_label="(Todos)",
        widget=forms.Select(attrs={"class": "form-control select2"}),
        required=False,
    )

    total = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: xx-large",
                "disabled": True,
            }
        ),
    )


class Trx700Form(forms.Form):
    fec_movimiento = forms.DateField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    cod_movimiento = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    nro_documento = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    socio = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))

    promocion = forms.ModelChoiceField(
        queryset=PromocionIngreso.objects.filter(activo=True),
        empty_label="(Todos)",
        widget=forms.Select(attrs={"class": "form-control select2", "disabled": True}),
    )

    aporte_ingreso = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
                "readonly": True,
            }
        ),
    )
    aporte = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
                "readonly": True,
            }
        ),
    )
    solidaridad = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
                "readonly": True,
            }
        ),
    )
    gastos = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
                "readonly": True,
            }
        ),
    )
    total = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
                "readonly": True,
            }
        ),
    )
    efectivo = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
                # "readonly": True,
            }
        ),
    )


class Trx701Form(forms.Form):
    fec_movimiento = forms.DateField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    cod_movimiento = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    nro_documento = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    socio = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))

    aporte_efectivo = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
            }
        ),
    )


class Trx702Form(forms.Form):
    fec_movimiento = forms.DateField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    cod_movimiento = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    nro_documento = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))
    socio = forms.CharField(widget=forms.TextInput(attrs={"type": "hidden2"}))

    solidaridad_efectivo = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
            }
        ),
    )


class Trx700FormPrueba(forms.Form):
    pass
    # def __init__(self, *args, **kwargs):
    #     request = kwargs.pop("request", None)
    #     if request:
    #         socio = request.POST["socio"]
    #         print(socio)
    #         if socio:
    #             data = (
    #                 SolicitudIngreso.objects.values(
    #                     "promocion",
    #                     "promocion__mto_ini_aporte_ingreso",
    #                     "promocion__mto_ini_aporte_social",
    #                     "promocion__mto_ini_aporte_solidaridad",
    #                 )
    #                 .filter(socio=socio)
    #                 .first()
    #             )
    #             print(data)

    #         super(Trx700Form, self).__init__(*args, **kwargs)
    #         if data:
    #             self.fields["promocion"].initial = data["promocion"]
    #             self.fields["aporte_ingreso"].initial = data[
    #                 "promocion__mto_ini_aporte_ingreso"
    #             ]
    #             self.fields["aporte"].initial = data["promocion__mto_ini_aporte_social"]
    #             self.fields["solidaridad"].initial = data[
    #                 "promocion__mto_ini_aporte_solidaridad"
    #             ]

    # self.fields["nro_factura"].initial = nro_factura
    # self.fields["nro_recibo"].initial = nro_recibo
