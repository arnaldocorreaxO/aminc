from django.db import models
from django.forms import model_to_dict
from core.models import ModeloBase

from core.base.choices import (
    choiceAmortizable,
    choiceCajaDiario,
    choiceMetodoInteres,
    choiceSiNo,
    choiceTipoCuenta,
    choiceTipoDC,
)
from core.base.models import Empresa, Modulo, RefDet, TipoComprobante, Transaccion

from core.base.utils import *


class PlanDeCuenta(ModeloBase):
    empresa = models.ForeignKey(
        Empresa,
        verbose_name="Empresa",
        on_delete=models.PROTECT,
        related_name="plan_de_cuenta",
    )
    cod_cuenta_contable = models.CharField(
        verbose_name="Cuenta Contable",
        max_length=30,
        db_column="cod_cuenta_contable",
        primary_key=True,
    )
    denominacion = models.CharField(verbose_name="Denominación", max_length=100)
    nivel = models.IntegerField(verbose_name="Nivel")
    cuenta_mayor = models.ForeignKey(
        "self",
        verbose_name="Cuenta Mayor",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        to_field="cod_cuenta_contable",
        related_name="plan_de_cuenta",
    )

    naturaleza = models.CharField(
        verbose_name="Naturaleza", max_length=1, default="C", choices=choiceTipoCuenta()
    )
    asentable = models.BooleanField(verbose_name="Asentable", default=False)
    centro_costo = models.CharField(
        verbose_name="Centro Costo", max_length=1, default="N", choices=choiceSiNo()
    )
    modulo = models.ForeignKey(
        Modulo,
        verbose_name="Modulo",
        db_column="cod_modulo",
        on_delete=models.PROTECT,
        related_name="plan_de_cuenta",
    )

    def to_JSON(self):
        item = model_to_dict(self)
        return item

    def __str__(self):
        return f"{self.cod_cuenta_contable} - {self.denominacion}"

    def __str2__(self):
        return (
            "+"
            + "--" * self.nivel
            + f" > {self.cod_cuenta_contable} - {self.denominacion}"
        )

    class Meta:
        ordering = [
            "cod_cuenta_contable",
        ]
        db_table = "cb_plan_de_cuenta"
        verbose_name = "Plan de Cuenta"
        verbose_name_plural = "Plan de Cuentas"


# #CONCEPTOS CONTABLES
# class ConceptoAsiento(ModeloBase):
#     modulo = models.ForeignKey(Modulo, verbose_name='Modulo', db_column='cod_modulo',
#                                on_delete=models.PROTECT, default=1, related_name='concepto_asiento')
#     descripcion = models.CharField(verbose_name='Descripción', max_length=100)

#     def __str__(self):
#         return '{}'.format(self.descripcion)

#     class Meta:
#         # ordering = ['tip_movimiento', ]
#         db_table = 'cb_concepto_asiento'
#         verbose_name = 'Concepto Asiento'
#         verbose_name_plural = 'Conceptos Asientos'

# ESQUEMA CONTABLE


class EsquemaContable(ModeloBase):
    transaccion = models.ForeignKey(
        Transaccion,
        verbose_name="Transaccion",
        db_column="cod_transaccion",
        on_delete=models.PROTECT,
        related_name="esquema_contable",
    )
    nombre_campo = models.CharField(verbose_name="Nombre Campo", max_length=100)
    tipo_dc = models.CharField(
        verbose_name="Debito/Credito", max_length=1, choices=choiceTipoDC()
    )
    rubro_contable = models.ForeignKey(
        PlanDeCuenta,
        verbose_name="Rubro Contable",
        db_column="rubro_contable",
        on_delete=models.PROTECT,
        related_name="esquema_contable",
        limit_choices_to={"asentable": 1},
    )
    concepto = models.CharField(verbose_name="Concepto", max_length=100)
    tip_comprobante = models.ForeignKey(
        TipoComprobante,
        verbose_name="Tipo Comprobante a Imprimir",
        db_column="tip_comprobante",
        to_field="tip_comprobante",
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return "{}".format(self.transaccion)

    class Meta:
        # ordering = ['tip_movimiento', ]
        db_table = "cb_esquema_contable"
        verbose_name = "Esquema Contable"
        verbose_name_plural = "Esquemas Contables"

# # TIPO MOVIMIENTO
# class TipoMovimiento(ModeloBase):
#     tip_movimiento = models.CharField(
#         verbose_name="Código", max_length=1, primary_key=True
#     )
#     denominacion = models.CharField(
#         verbose_name="Tipo Movimiento", max_length=100, unique=True
#     )

#     def __str__(self):
#         return "{} - {}".format(self.tip_movimiento, self.denominacion)

#     class Meta:
#         ordering = [
#             "tip_movimiento",
#         ]
#         db_table = "ge_tipo_movimiento"
#         verbose_name = "Tipo Movimiento"
#         verbose_name_plural = "Tipos Movimientos"

# # MOVIMIENTO ABSTRACT
# class MovimientoBase(ModeloBase):
#     fec_movimiento = models.DateField(verbose_name="Fecha Movimiento")
#     cod_movimiento = models.CharField(verbose_name="Codigo Movimiento", max_length=8)
#     tip_movimiento = models.ForeignKey(
#         TipoMovimiento,
#         verbose_name="Tipo",
#         db_column="tip_movimiento",
#         on_delete=models.PROTECT,
#         blank=True,
#         null=True,
#         default="A",
#     )
#     modulo = models.ForeignKey(
#         Modulo,
#         verbose_name="Modulo",
#         db_column="cod_modulo",
#         on_delete=models.PROTECT,
#         blank=True,
#         null=True,
#     )
#     transaccion = models.ForeignKey(
#         Transaccion,
#         verbose_name="Transacción",
#         db_column="cod_transaccion",
#         on_delete=models.PROTECT,
#         blank=True,
#         null=True,
#     )
#     nro_asiento = models.IntegerField(verbose_name="Nro. Asiento", default=0)
#     sucursal = models.ForeignKey(
#         Sucursal,
#         verbose_name="Sucursal",
#         on_delete=models.PROTECT,
#         blank=True,
#         null=True,
#     )
#     cliente = models.ForeignKey(
#         Cliente,
#         db_column="cod_cliente",
#         verbose_name="Cliente",
#         on_delete=models.PROTECT,
#         blank=True,
#         null=True,
#         related_name="%(app_label)s_%(class)s_cliente",
#     )
#     moneda = models.ForeignKey(
#         Moneda, verbose_name="Moneda", on_delete=models.PROTECT, blank=True, null=True
#     )
#     cotizacion = models.FloatField(verbose_name="Cotizacion", default=1)
#     mto_equi_local = models.DecimalField(
#         verbose_name="Monto Equivalente Local",
#         default=0,
#         max_digits=20,
#         decimal_places=2,
#     )
#     rubro_contable = models.ForeignKey(
#         PlanDeCuenta,
#         verbose_name="Rubro Contable",
#         db_column="rubro_contable",
#         on_delete=models.PROTECT,
#         related_name="%(app_label)s_%(class)s_rubro_contable",
#         blank=True,
#         null=True,
#     )
#     cuenta_operativa = models.CharField(
#         verbose_name="Cuenta Operativa", max_length=50, null=True, blank=True
#     )
#     concepto = models.CharField(verbose_name="Concepto", max_length=100, blank=True)
#     debito = models.DecimalField(
#         verbose_name="Debito", default=0, max_digits=20, decimal_places=2
#     )
#     credito = models.DecimalField(
#         verbose_name="Credito", default=0, max_digits=20, decimal_places=2
#     )
#     nombre_campo = models.CharField(
#         verbose_name="Nombre Campo", max_length=100, null=True, blank=True, default=None
#     )
#     referencia = models.CharField(
#         verbose_name="Referencia", max_length=100, null=True, blank=True, default=None
#     )
#     nro_caja = models.ForeignKey(
#         Caja,
#         verbose_name="Nro. Caja",
#         db_column="nro_caja",
#         on_delete=models.PROTECT,
#         default=0,
#         related_name="%(class)s_movimiento",
#         blank=True,
#         null=True,
#     )
#     caja_diario = models.CharField(
#         verbose_name="Caja Diario",
#         max_length=1,
#         choices=choiceCajaDiario(),
#         default="D",
#     )
#     nro_documento = models.CharField(
#         verbose_name="Nro. Documento", max_length=25, null=True, blank=True
#     )
#     fec_valor = models.DateField(
#         verbose_name="Fecha Valor", blank=True, null=True, default=None
#     )
#     iva = models.IntegerField(verbose_name="Iva %", default=0)
#     monto_iva = models.DecimalField(
#         verbose_name="Monto Iva", default=0, max_digits=20, decimal_places=2
#     )
#     # Compensaciones de Cheques
#     cod_compensacion = models.ForeignKey(
#         RefDet,
#         to_field="cod",
#         limit_choices_to={"refcab_id": 11},
#         db_column="cod_compensacion",
#         on_delete=models.RESTRICT,
#         related_name="%(app_label)s_%(class)s_compensacion",
#         max_length=1,
#         default=0,
#     )
#     tip_comprobante = models.ForeignKey(
#         TipoComprobante,
#         verbose_name="Tipo Comprobante",
#         db_column="tip_comprobante",
#         to_field="tip_comprobante",
#         on_delete=models.PROTECT,
#     )
#     cod_usuario = models.ForeignKey(
#         User,
#         verbose_name="Usuario Movimiento",
#         to_field="cod_usuario",
#         db_column="cod_usuario",
#         on_delete=models.PROTECT,
#         related_name="%(app_label)s_%(class)s_usuario_movimiento",
#         blank=True,
#         null=True,
#     )

#     class Meta:
#         abstract = True


# """MOVIMIENTOS DIARIOS"""


# class Movimiento(MovimientoBase):
#     def toJSON(self):
#         item = model_to_dict(self)
#         # item = {}
#         item["placta"] = {"rubro_contable": str(self.rubro_contable)}
#         item["debito"] = format(self.debito, ".2f")
#         item["credito"] = format(self.credito, ".2f")
#         item["fec_movimiento"] = (
#             self.fec_movimiento.strftime("%d/%m/%Y") if self.fec_movimiento else None
#         )
#         item["credito"] = format(self.credito, ".2f")
#         item["credito"] = format(self.credito, ".2f")
#         item["nro_socio"] = self.cliente.nro_socio
#         item["cod_cliente"] = self.cliente.cod_cliente
#         item["socio"] = self.cliente.get_nro_socio_nombre()
#         item["cod_usuario"] = self.usu_insercion.cod_usuario

#         return item

#     class Meta:
#         # ordering = ['tip_movimiento', ]
#         db_table = "cb_movimientos"
#         verbose_name = "Movimiento Diario"
#         verbose_name_plural = "Movimientos Diarios"


# """MOVIMIENTOS MENSUALES DEL PERIODO ACTUAL"""


# class MovimientosMensuales(MovimientoBase):
#     def toJSON(self):
#         item = model_to_dict(self)
#         item["placta"] = {"rubro_contable": str(self.rubro_contable)}
#         item["debito"] = format(self.debito, ".2f")
#         item["credito"] = format(self.credito, ".2f")
#         return item

#     class Meta:
#         # ordering = ['tip_movimiento', ]
#         db_table = "cb_movimientos_mensuales"
#         verbose_name = "Movimientos Mensuales"
#         verbose_name_plural = "Movimientos Mensuales"


# """MOVIMIENTOS ANUALES HASTA PERIODO ANTERIOR"""


# class MovimientosAnuales(MovimientoBase):
#     def toJSON(self):
#         item = model_to_dict(self)
#         item["placta"] = {"rubro_contable": str(self.rubro_contable)}
#         item["debito"] = format(self.debito, ".2f")
#         item["credito"] = format(self.credito, ".2f")
#         return item

#     class Meta:
#         # ordering = ['tip_movimiento', ]
#         db_table = "cb_movimientos_anuales"
#         verbose_name = "Movimientos Anuales"
#         verbose_name_plural = "Movimientos Anuales"


# class TmpMovimiento(MovimientoBase):
#     def toJSON(self):
#         # item = model_to_dict(self)
#         item = {}
#         item["transaccion"] = self.transaccion
#         item["placta"] = {"rubro_contable": str(self.rubro_contable)}
#         item["debito"] = format(self.debito, ".2f")
#         item["credito"] = format(self.credito, ".2f")
#         return item

#     class Meta:
#         # ordering = ['tip_movimiento', ]
#         db_table = "tmp_movimientos"
#         verbose_name = "Movimiento Temporal"
#         verbose_name_plural = "Movimientos Temporales"


class OperativaContable(ModeloBase):
    cod_tipo_operativa = models.IntegerField(
        verbose_name="Codigo", db_column="cod_tipo_operativa", unique=True
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=100)
    modulo = models.ForeignKey(
        Modulo,
        db_column="cod_modulo",
        on_delete=models.PROTECT,
        related_name="modulo_operativa_contable",
    )
    plazo = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_id": 5},
        db_column="plazo",
        on_delete=models.RESTRICT,
        related_name="plazo_operativa_contable",
        max_length=1,
    )
    amortizable = models.CharField(
        verbose_name="Amortizable",
        max_length=1,
        choices=choiceAmortizable(),
        default="S",
    )

    def __str__(self):
        return f"{self.cod_tipo_operativa} - {self.denominacion}"

    class Meta:
        ordering = ("id",)
        db_table = "cb_operativa_contable"
        verbose_name = "Operativa Contable Cab"
        verbose_name_plural = "Operativa Contable Cab"


class OperativaContableDetalle(ModeloBase):
    operativa_contable = models.ForeignKey(
        OperativaContable,
        to_field="cod_tipo_operativa",
        db_column="cod_tipo_operativa",
        on_delete=models.PROTECT,
    )
    nombre_campo = models.CharField(
        verbose_name="Nombre Campo",
        max_length=50,
        null=True,
        blank=True,
        default=None,
    )

    rubro_contable = models.ForeignKey(
        PlanDeCuenta,
        verbose_name="Rubro Contable",
        db_column="rubro_contable",
        on_delete=models.PROTECT,
        related_name="rubro_contable",
        blank=True,
        null=True,
    )

    rubro_operativo = models.ForeignKey(
        PlanDeCuenta,
        verbose_name="Rubro Operativo",
        db_column="rubro_operativo",
        on_delete=models.PROTECT,
        related_name="rubro_operativo",
        blank=True,
        null=True,
    )
    nombre_generico = models.CharField(
        verbose_name="Nombre Generico",
        max_length=50,
        null=True,
        blank=True,
        default=None,
    )
    metodo_interes = models.CharField(
        verbose_name="Metodo Interes",
        max_length=1,
        choices=choiceMetodoInteres(),
        default="A",
    )
    uso_operacion = models.CharField(
        verbose_name="Uso Operacion",
        max_length=1,
        choices=choiceSiNo(),
        default="N",
    )

    def __str__(self):
        return f"{self.operativa_contable} ->{self.nombre_campo}"

    class Meta:
        ordering = ("id",)
        db_table = "cb_operativa_contable_detalle"
        verbose_name = "Operativa Contable Detalle"
        verbose_name_plural = "Operativa Contable Detalle"
        unique_together = ["operativa_contable", "nombre_campo"]
