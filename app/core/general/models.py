from django.db import models
from django.forms import model_to_dict

from core.contable.models import PlanDeCuenta
from core.models import ModeloBase
from core.base.models import Persona, RefDet, Sucursal, Moneda

# CALIFICACION CLIENTE
class CalificacionCliente(ModeloBase):
    cod = models.CharField(verbose_name="Código", max_length=1, unique=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=25, unique=True
    )
    promedio_atraso = models.IntegerField(verbose_name="Promedio Atraso")

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        db_table = "ge_calificacion_cliente"
        verbose_name = "Calificacion Cliente"
        verbose_name_plural = "Calificacion Clientes"


# ESTADO CLIENTE
class EstadoCliente(ModeloBase):
    cod = models.CharField(verbose_name="Código", max_length=4, unique=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=25, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        db_table = "ge_estado_cliente"
        verbose_name = "Estado Cliente"
        verbose_name_plural = "Estado Clientes"


# SOCIO
class Cliente(ModeloBase):
    cod_cliente = models.IntegerField(verbose_name="Cod. Cliente", primary_key=True)
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name="Sucursal",
        on_delete=models.RESTRICT,
        related_name="cliente_sucursal",
    )
    nro_socio = models.IntegerField(verbose_name="Nro. Socio", unique=True)
    persona = models.ForeignKey(
        Persona,
        verbose_name="Persona",
        on_delete=models.RESTRICT,
        related_name="cliente_persona",
    )
    fec_ingreso = models.DateField(verbose_name="Fecha Ingreso")
    fec_retiro = models.DateField(verbose_name="Fecha Retiro", null=True, blank=True)
    estado = models.ForeignKey(
        EstadoCliente,
        to_field="cod",
        db_column="estado",
        verbose_name="Estado Cliente",
        on_delete=models.RESTRICT,
        related_name="cliente_estado",
    )
    calificacion = models.ForeignKey(
        CalificacionCliente,
        to_field="cod",
        db_column="calificacion",
        verbose_name="Calificacion Cliente",
        on_delete=models.RESTRICT,
        related_name="cliente_calificacion",
    )
    comentario = models.CharField(
        verbose_name="Comentario", max_length=100, null=True, blank=True
    )

    def __str__(self):
        return "{} - {}".format(self.nro_socio, self.persona)

    def get_nro_socio_nombre(self):
        return "{} - {}".format(self.nro_socio, self.persona)

    def toJSON(self):
        item = model_to_dict(self)
        item["persona"] = str(self.persona)
        item["ci"] = self.persona.ci
        item["telefono"] = (
            self.persona.telefono if self.persona.telefono else self.persona.celular
        )
        item["fec_ingreso"] = (
            self.fec_ingreso.strftime("%d/%m/%Y") if self.fec_ingreso else None
        )
        item["fec_retiro"] = (
            self.fec_retiro.strftime("%d/%m/%Y") if self.fec_retiro else None
        )
        return item

    class Meta:
        db_table = "ge_cliente"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

"""PLAZOS EN DIAS"""


class Plazo(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)
    plazo = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_id": 5},
        db_column="plazo",
        on_delete=models.RESTRICT,
        max_length=1,
    )
    rango_inferior = models.IntegerField(default=0)
    rango_superior = models.IntegerField(default=0)
    contrato_inferior = models.IntegerField(default=0)
    contrato_superior = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.denominacion} - {self.plazo} "

    class Meta:
        ordering = ["id"]
        db_table = "ge_plazo"
        verbose_name = "Plazos en Dias"
        verbose_name_plural = "Plazos en Dias"



"""TIPO BANCO"""
class TipoBanco(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)
    def __str__(self):
        return f"{self.denominacion}"

    class Meta:
        ordering = ["id"]
        db_table = "ge_tipo_banco"
        verbose_name = "Tipo Banco"
        verbose_name_plural = "Tipos de Bancos"


"""BANCOS"""
class Banco(ModeloBase):
    tipo_banco = models.ForeignKey(
        TipoBanco,
        to_field="id",
        db_column="tipo_banco_id",
        verbose_name="Tipo Banco",
        on_delete=models.RESTRICT,
        related_name="banco_tipo_banco",
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)
    def __str__(self):
        return f"{self.denominacion}"

    class Meta:
        ordering = ["id"]
        db_table = "ge_banco"
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"


"""CUENTAS BANCO"""
class CuentaBanco(ModeloBase):
    nro_cuenta = models.CharField(
        verbose_name="Nro. Cuenta", max_length=50, unique=True
    )
    banco = models.ForeignKey(
        Banco,
        to_field="id",
        db_column="banco_id",
        verbose_name="Banco",
        on_delete=models.RESTRICT,
        related_name="cuenta_banco_banco",
    )
    rubro_contable = models.ForeignKey(
        PlanDeCuenta,
        verbose_name="Rubro Contable",
        db_column="rubro_contable",
        on_delete=models.PROTECT,
        related_name="rubro_contable_cuenta_banco",
        limit_choices_to={"asentable": 1},
        null=True,
        blank=True,
        help_text="Seleccione el rubro contable al que pertenece esta cuenta bancaria.",  
    )
    saldo = models.DecimalField(
        verbose_name="Saldo", default=0, max_digits=20, decimal_places=2
    )
    nro_cheque_desde = models.CharField(
        max_length=20,
        verbose_name="Número de cheque desde",
        help_text="Ingrese el número de cheque desde donde desea iniciar."
    )
    nro_cheque_hasta = models.CharField(
        max_length=20,
        verbose_name="Número de cheque hasta",
        help_text="Ingrese el número de cheque hasta donde desea finalizar."
    )
    nro_cheque_actual = models.CharField(
        max_length=20,
        verbose_name="Número de cheque actual",
        help_text="Ingrese el número de cheque actual."
    )
    Moneda = models.ForeignKey(
        Moneda,
        to_field="id",
        db_column="moneda_id",
        verbose_name="Moneda",
        on_delete=models.RESTRICT,
        related_name="cuenta_banco_moneda",
    )
    Sucursal = models.ForeignKey(
        Sucursal,
        to_field="id",
        db_column="sucursal_id",
        verbose_name="Sucursal",
        on_delete=models.RESTRICT,
        related_name="cuenta_banco_sucursal",
    )
    saldo_minimo = models.DecimalField(
        verbose_name="Saldo Mínimo",
        default=0,
        max_digits=20,
        decimal_places=2,
        help_text="Ingrese el saldo mínimo permitido en la cuenta.",
    )
    saldo_promedio = models.DecimalField(
        verbose_name="Saldo Promedio",
        default=0,
        max_digits=20,
        decimal_places=2,
        help_text="Ingrese el saldo promedio de la cuenta.",
    )
    def __str__(self):
        return f"{self.banco} - {self.nro_cuenta}"

    class Meta:
        ordering = ["id"]
        db_table = "ge_cuenta_banco"
        verbose_name = "Cuenta Banco"
        verbose_name_plural = "Cuentas Bancos"
