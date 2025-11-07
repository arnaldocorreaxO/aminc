from datetime import date
from django import forms
from django.forms import ModelForm

from core.base.forms import readonly_fields
from core.base.models import Parametro, RefDet
from core.base.utils import get_fecha_actual, get_fecha_actual_ymd
from core.general.models import Banco, CuentaBanco

from .models import *


class SolicitudPrestamoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fec_solicitud"].widget.attrs["autofocus"] = True
        self.fields["cant_cuota"].initial = (
            Parametro.objects.filter(parametro="CANT_CUOTA_ANUAL_INICIAL").first() or 12
        ).valor
        self.fields["sucursal"].queryset = Sucursal.objects.exclude(activo=False)
        self.fields["cliente"].queryset = Cliente.objects.none()
        if self.instance:
            self.fields["cliente"].queryset = Cliente.objects.filter(
                cod_cliente=self.instance.cliente_id
            )

    class Meta:
        model = SolicitudPrestamo
        fields = "__all__"
        localized_fields = "__all__"  # Formatea numeros y fechas a formato regional
        exclude = readonly_fields
        widgets = {
            "nro_solicitud": forms.TextInput(
                attrs={"placeholder": "Genera Automático"}
            ),
            "fec_solicitud": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "fec_solicitud",
                    "value": get_fecha_actual_ymd,
                    "data-toggle": "datetimepicker",
                    "data-target": "#fec_solicitud",
                },
            ),
            "fec_desembolso": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "fec_desembolso",
                    "value": get_fecha_actual_ymd,
                    "data-toggle": "datetimepicker",
                    "data-target": "#fec_desembolso",
                },
            ),
            "fec_1er_vencimiento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control datetimepicker-input",
                    "id": "fec_1er_vencimiento",
                    "value": get_fecha_actual_ymd,
                    "data-toggle": "datetimepicker",
                    "data-target": "#fec_1er_vencimiento",
                },
            ),
            # "monto_cuota_inicial": forms.TextInput(
            #     attrs={
            #         "placeholder": "Indique un Nro. de Telefono para Contacto",
            #     },
            # ),
            "cliente": forms.Select(
                attrs={"class": "custom-select select2", "style": "width: 100%;"}
            ),
            "tipo_prestamo": forms.Select(
                attrs={"class": "custom-select select2", "style": "width: 100%;"}
            ),
            "destino_prestamo": forms.Select(
                attrs={"class": "custom-select select2", "style": "width: 100%;"}
            ),
            # "forma_desembolso": forms.Select(
            #     attrs={"class": "custom-select select2", "style": "width: 100%;"}
            # ),
        }
        labels = {
            "tasa_interes": "Tasa%",
            "plazo_meses": "Plazo",
            "cant_cuota": "C.Anual",
            "fec_1er_vencimiento": "Fec. 1er Vencimiento",
            # "forma_desembolso": "Forma Desembolso",
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


# *TRX 501
class Trx501Form(forms.Form):
    prestamo = forms.ModelChoiceField(
        label="Préstamo a Desembolsar",
        queryset=Prestamo.objects.filter(
            activo=True, situacion_prestamo__in=["PEND", "INIC"]
        ),
        empty_label="(Todos)",
        required=True,
        to_field_name="nro_prestamo",
        # widget=forms.Select(attrs={"class": "form-control select2", "disabled": True}),
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
            },
        ),
    )
    forma_desembolso = forms.ModelChoiceField(
        label="Forma de Desembolso",
        queryset=RefDet.objects.filter(
            activo=True, refcab__cod_referencia__exact="FORMA_DESEMBOLSO"
        ),
        empty_label="(Todos)",
        required=True,
        # widget=forms.Select(attrs={"class": "form-control select2", "disabled": True}),
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
            }
        ),
    )
    banco = forms.ModelChoiceField(
        label="Banco / Tesorería",
        queryset=Banco.objects.filter(activo=True),
        empty_label="(Todos)",
        required=True,
        # widget=forms.Select(attrs={"class": "form-control select2", "disabled": True}),
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
            }
        ),
    )
    nro_cuenta_banco = forms.ModelChoiceField(
        label="Nro. Cuenta Banco / Tesorería",
        queryset=CuentaBanco.objects.filter(activo=True),
        empty_label="(Todos)",
        required=True,
        # widget=forms.Select(attrs={"class": "form-control select2", "disabled": True}),
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
            }
        ),
    )


# *TRX 503
class Trx503Form(forms.Form):
    fecha = forms.DateField(
        label="Fecha Situación Solicitud",
        required=True,
        initial=get_fecha_actual_ymd(),
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control datetimepicker-input",
                "id": "fecha",
                "data-toggle": "datetimepicker",
                "data-target": "#fecha",
            },
        ),
    )
    solicitud = forms.ModelChoiceField(
        label="Solicitud de Préstamo",
        queryset=SolicitudPrestamo.objects.filter(
            activo=True, estado__in=["PEND", "INIC"]
        ),
        empty_label="(Todos)",
        required=True,
        to_field_name="nro_solicitud",
        # widget=forms.Select(attrs={"class": "form-control select2", "disabled": True}),
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
            },
        ),
    )
    situacion_solicitud = forms.ModelChoiceField(
        label="Situación Solicitud",
        queryset=SituacionSolicitud.objects.filter(activo=True),
        empty_label="(Todos)",
        required=True,
        # widget=forms.Select(attrs={"class": "form-control select2", "disabled": True}),
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
            }
        ),
    )
    comentario = forms.CharField(required=False)

    nro_acta = forms.CharField(
        label="Nro. Acta",
        required=False,
        initial=SituacionSolicitudPrestamo.get_ultimo_nro_acta,
    )

    fec_acta = forms.DateField(
        label="Fecha Acta",
        required=False,
        initial=SituacionSolicitudPrestamo.get_ultima_fecha_acta,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control datetimepicker-input",
                "id": "fec_acta",
                "data-toggle": "datetimepicker",
                "data-target": "#fec_acta",
            },
        ),
    )
    nro_resolucion = forms.CharField(
        label="Nro. Resolución",
        required=True,
        initial=SituacionSolicitudPrestamo.get_ultimo_nro_resolucion,
    )

    monto_aprobado = forms.DecimalField(
        label="Monto a Aprobar",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-right",
                "size": "40",
                "style": "font-size: medium",
                "id": "monto_aprobado",
                "maxlength": "25",
                "data-decimales": "0",  # 🔹 clave para formateo JS
                "data-col": "2",  # 🔹 clave para formateo JS
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Asignar col-md-x institucionalmente
        self.fields["fecha"].col = 6
        self.fields["solicitud"].col = 6
        self.fields["situacion_solicitud"].col = 6
        self.fields["comentario"].col = 6
        self.fields["nro_acta"].col = 3
        self.fields["fec_acta"].col = 3
        self.fields["nro_resolucion"].col = 3
        self.fields["monto_aprobado"].col = 3


# *TRX 504
class Trx504Form(forms.Form):
    solicitud = forms.ModelChoiceField(
        queryset=SolicitudPrestamo.objects.filter(
            activo=True, liquidado__exact="N", estado__in=["APRO"]
        ),
        empty_label="(Todos)",
        required=True,
        to_field_name="nro_solicitud",
        # widget=forms.Select(attrs={"class": "form-control select2", "disabled": True}),
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
            },
        ),
    )

    fec_ult_desembolso = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control datetimepicker-input",
                "id": "fec_ult_desembolso",
                "value": get_fecha_actual_ymd,
                "data-toggle": "datetimepicker",
                "data-target": "#fec_ult_desembolso",
            },
        ),
    )
    fec_1er_vencimiento = forms.DateField(
        required=True,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control datetimepicker-input",
                "id": "fec_1er_vencimiento",
                "value": get_fecha_actual_ymd,
                "data-toggle": "datetimepicker",
                "data-target": "#fec_1er_vencimiento",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Asignar col-md-x institucionalmente
        self.fields["solicitud"].col = 12
        self.fields["fec_ult_desembolso"].col = 6
        self.fields["fec_1er_vencimiento"].col = 6
