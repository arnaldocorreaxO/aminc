import json
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.forms import model_to_dict

from core.base.choices import choiceMultipleDesembolso, choiceSiNo
from core.base.models import (ModeloBase, Modulo, Moneda, RefDet, Sucursal,
                              Transaccion)
from core.contable.models import OperativaContable, PlanDeCuenta
from core.general.models import Cliente, Plazo


# Create your models here.
# ***********************************************
# * NIVELES DE APROBACION
# * Codigo 1 al 5 define el nivel de aprobacion
# ***********************************************
class NivelAprobacion(ModeloBase):
    cod_nivel_aprobacion = models.CharField(
        verbose_name="Cod. Nivel Aprobacion",
        db_column="cod_nivel_aprobacion",
        max_length=4,
        unique=True,
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)

    def __str__(self):
        return f"{self.denominacion} - {self.cod_nivel_aprobacion}"

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "pr_nivel_aprobacion"
        verbose_name = "Nivel Aprobacion"
        verbose_name_plural = "Nivel Aprobacion"


# ***********************************************
# * SITUACION DE PRESTAMOS
# ***********************************************
class SituacionPrestamo(ModeloBase):
    cod = models.CharField(
        verbose_name="Codigo", db_column="cod", max_length=4, unique=True
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)
    rango_inferior = models.IntegerField(default=0)
    rango_superior = models.IntegerField(default=0)

    def __str__(self):
        return "{} - {} de {} a {}".format(
            self.cod, self.denominacion, self.rango_inferior, self.rango_superior
        )

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "pr_situacion_prestamo"
        verbose_name = "Situacion Prestamo"
        verbose_name_plural = "Situacion Prestamo"


# ***********************************************
# * ESTADO DESEMBOLSO DE PRESTAMOS
# ***********************************************
class EstadoDesembolso(ModeloBase):
    cod = models.CharField(
        verbose_name="Codigo", db_column="cod", max_length=4, unique=True
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)

    def __str__(self):
        return "{} - {}".format(self.cod, self.denominacion)

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "pr_estado_desembolso"
        verbose_name = "Estado Desembolso"
        verbose_name_plural = "Estado Desembolso"


# ***********************************************
# * ESQUEMA CONTABLE PARA PRESTAMOS
# ***********************************************
class EsquemaContable(ModeloBase):
    plazo = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_cod_referencia": "TIPO_PLAZO_PRESTAMO"},
        db_column="plazo",
        on_delete=models.RESTRICT,
        related_name="plazo_esquema_contable",
        max_length=1,
    )
    vencimiento = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_cod_referencia": "IND_PRESTAMO_VENCIDO"},
        db_column="vencimiento",
        on_delete=models.RESTRICT,
        related_name="vencimiento",
        max_length=1,
    )
    estado_cliente = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_cod_referencia": "ESTADO_SOCIO"},
        db_column="estado_cliente",
        on_delete=models.RESTRICT,
        related_name="estado_cliente",
        max_length=4,
    )
    situacion_prestamo = models.ForeignKey(
        SituacionPrestamo,
        to_field="cod",
        default="NORM",
        db_column="situacion_prestamo",
        on_delete=models.RESTRICT,
        related_name="situacion_prestamo",
        max_length=4,
    )
    tipo_credito = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_cod_referencia": "GRUPO_TIPO_CREDITO"},
        db_column="tipo_credito",
        on_delete=models.RESTRICT,
        related_name="tipo_credito",
        max_length=25,
        default="COOPERATIVA",
    )
    rubro_comision = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_comision",
        on_delete=models.PROTECT,
        related_name="rubro_comision",
    )
    rubro_capital = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_capital",
        on_delete=models.PROTECT,
        related_name="rubro_capital",
    )
    rubro_interes = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_interes",
        on_delete=models.PROTECT,
        related_name="rubro_intres",
    )
    rubro_interes_moratorio = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_interes_moratorio",
        on_delete=models.PROTECT,
        related_name="rubro_interes_moratorio",
    )
    rubro_interes_punitorio = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_interes_punitorio",
        on_delete=models.PROTECT,
        related_name="rubro_interes_punitorio",
    )
    rubro_capital_inverso = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_capital_inverso",
        on_delete=models.PROTECT,
        related_name="rubro_capital_inverso",
    )
    rubro_desafectacion = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_desafectacion",
        on_delete=models.PROTECT,
        related_name="rubro_desafectacion",
    )
    rubro_constitucion = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_constitucion",
        on_delete=models.PROTECT,
        related_name="rubro_constitucion",
    )
    rubro_prevision = models.ForeignKey(
        PlanDeCuenta,
        db_column="rubro_prevision",
        on_delete=models.PROTECT,
        related_name="rubro_prevision",
    )
    vinculado = models.CharField(max_length=1, default="N", choices=choiceSiNo())

    def __str__(self):
        return f"{str(self.plazo)}->{str(self.vencimiento)}-> SOCIO: {str(self.estado_cliente)}->\
                 {str(self.situacion_prestamo)}-> VINCULADO: {str(self.vinculado)}"

    class Meta:
        db_table = "pr_esquema_contable"
        verbose_name = "Esquema Contable "
        verbose_name_plural = "Esquemas Contables"


# ***********************************************
# * SECTOR DE PRESTAMOS = GRUPO DE PRESTAMOS
# ***********************************************
class SectorPrestamo(ModeloBase):
    denominacion = models.CharField(max_length=100)
    dias_ensuspension = models.IntegerField(default=61)

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "pr_sector_prestamo"
        verbose_name = "Sector Prestamo"
        verbose_name_plural = "Sector Prestamos"


# ***********************************************
# * TIPOS DE PRESTAMOS
# ***********************************************
class TipoPrestamo(ModeloBase):
    denominacion = models.CharField(max_length=100)
    denom_corta = models.CharField(verbose_name="Denominacion Corta", max_length=8)
    sector_prestamo = models.ForeignKey(
        SectorPrestamo,
        on_delete=models.RESTRICT,
        null=True,
    )
    cod_nivel_aprobacion = models.ForeignKey(
        NivelAprobacion,
        to_field="cod_nivel_aprobacion",
        db_column="cod_nivel_aprobacion",
        on_delete=models.RESTRICT,
        related_name="nivel_aprobacion",
        max_length=4,
        null=True,
    )
    forma_desembolso = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_cod_referencia": "FORMA_DESEMBOLSO"},
        db_column="forma_desembolso",
        on_delete=models.RESTRICT,
        related_name="forma_desembolso",
        max_length=4,
        default="EFEC",
    )
    multiple_desembolso = models.IntegerField(
        default=1, choices=choiceMultipleDesembolso()
    )
    tasa_interes_moratorio = models.DecimalField(
        default=0, max_digits=4, decimal_places=2
    )
    tasa_interes_punitorio = models.DecimalField(
        default=0, max_digits=4, decimal_places=2
    )
    requiere_liquidacion = models.BooleanField(default=True)

    def __str__(self):
        return f"{str(self.denominacion)} -> {str(self.sector_prestamo)}"

    class Meta:
        db_table = "pr_tipo_prestamo"
        verbose_name = "Tipo Prestamo"
        verbose_name_plural = "Tipos Prestamos"


# ***********************************************
# * SITUACION DE SOLICITUDES DE PRESTAMOS
# ***********************************************
class SituacionSolicitud(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=100)
    situacion_final = models.CharField(
        verbose_name="Situacion Final", max_length=1, choices=choiceSiNo(), default="N"
    )
    # Estado Solicitud: Para aplicar segun situacion de la Solicitud de Prestamo
    estado = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_cod_referencia": "ESTADO_APROBACION"},
        db_column="estado",
        on_delete=models.RESTRICT,
        related_name="estado_solicitud2",
        max_length=1,
    )
    cod_nivel_aprobacion = models.ForeignKey(
        NivelAprobacion,
        to_field="cod_nivel_aprobacion",
        db_column="cod_nivel_aprobacion",
        on_delete=models.RESTRICT,
        related_name="nivel_aprobacion_situacion",
        max_length=4,
        null=True,
    )

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "pr_situacion_solicitud"
        verbose_name = "Situacion Solicitud"
        verbose_name_plural = "Situacion Solicitud"


# ***********************************************
# * CLASIFICACION POR DESTINOS DE PRESTAMOS
# ***********************************************
class ClasificacionPorDestino(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=100)

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "pr_clasificacion_por_destino"
        verbose_name = "Clasificacion por Destino de Prestamo"
        verbose_name_plural = "Clasificacion por Destino de Prestamos"


# ***********************************************
# * DESTINOS DE PRESTAMOS
# ***********************************************
class DestinoPrestamo(ModeloBase):
    denominacion = models.CharField(verbose_name="Denominacion", max_length=100)
    grupo_prestamo = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_cod_referencia": "GRUPO_PRESTAMO"},
        db_column="grupo_prestamo",
        on_delete=models.RESTRICT,
        related_name="grupo_prestamo2",
        max_length=4,
    )
    clasificacion_por_destino = models.ForeignKey(
        ClasificacionPorDestino,
        on_delete=models.PROTECT,
        related_name="clasificacion_por_destino",
    )

    def __str__(self):
        return self.denominacion

    class Meta:
        db_table = "pr_destino_prestamo"
        verbose_name = "Destino de Prestamos"
        verbose_name_plural = "Destinos de Prestamos"


# ***********************************************
# * PLAZOS DE PRESTAMOS
# ***********************************************
class Plazo(ModeloBase):
    tasa_interes = models.DecimalField(max_digits=6, decimal_places=2)
    desde_plazo = models.IntegerField(default=1)
    hasta_plazo = models.IntegerField(default=12)
    desde_monto = models.DecimalField(max_digits=14, decimal_places=2)
    hasta_monto = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"MES: {self.desde_plazo} HASTA: {self.hasta_plazo} \
            => MONTO: {self.desde_monto} HASTA: {self.hasta_monto} \
            => TASA: {self.tasa_interes}"

    class Meta:
        ordering = ["id"]
        db_table = "pr_plazo"
        verbose_name = "Plazos Prestamos"
        verbose_name_plural = "Plazos Prestamos"


# ***********************************************
# * SOLICITUDES DE PRESTAMOS
# ***********************************************
class SolicitudPrestamo(ModeloBase):
    nro_solicitud = models.CharField(
        verbose_name="Nro. Solicitud",
        db_column="nro_solicitud",
        max_length=10,
        unique=True,
    )
    nro_prestamo = models.CharField(
        verbose_name="Nro. Prestamo",
        db_column="nro_prestamo",
        max_length=10,
        # unique=True,
        null=True,
        blank=True,
    )
    cod_tipo_operativa = models.ForeignKey(
        OperativaContable,
        to_field="cod_tipo_operativa",
        db_column="cod_tipo_operativa",
        on_delete=models.RESTRICT,
        related_name="operativa_contable",
        default=101,
        blank=True
    )
    fec_solicitud = models.DateField(verbose_name="Fecha Solicitud")
    sucursal = models.ForeignKey(
        Sucursal, verbose_name="Sucursal", on_delete=models.PROTECT
    )
    cliente = models.ForeignKey(
        Cliente,
        db_column="cod_cliente",
        verbose_name="Cliente",
        on_delete=models.PROTECT,
    )
    tipo_prestamo = models.ForeignKey(
        TipoPrestamo, verbose_name="Tipo Prestamo", on_delete=models.PROTECT
    )
    destino_prestamo = models.ForeignKey(
        DestinoPrestamo, verbose_name="Destino Prestamo", on_delete=models.PROTECT
    )
    monto_solicitado = models.DecimalField(
        verbose_name="Monto Solicitado", max_digits=14, decimal_places=2, default=0
    )
    monto_prestamo = models.DecimalField(
        verbose_name="Monto Prestamo", max_digits=14, decimal_places=2, default=0
    )
    monto_aprobado = models.DecimalField(
        verbose_name="Monto Aprobado", max_digits=14, decimal_places=2, default=0
    )
    monto_refinanciado = models.DecimalField(
        verbose_name="Monto Refinanciado", max_digits=14, decimal_places=2, default=0
    )
    monto_neto = models.DecimalField(
        verbose_name="Monto Neto", max_digits=14, decimal_places=2, default=0
    )
    monto_cuota_inicial = models.DecimalField(
        verbose_name="Monto Cuota Inicial", max_digits=14, decimal_places=2, default=0
    )
    plazo_meses = models.IntegerField()
    moneda = models.ForeignKey(Moneda, verbose_name="Moneda", on_delete=models.PROTECT)
    estado = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab__cod_referencia": "ESTADO_APROBACION"},
        db_column="estado",
        on_delete=models.RESTRICT,
        related_name="estado_solicitud",
        max_length=4,
    )
    tasa_interes = models.DecimalField(
        verbose_name="Tasa Interes", default=0, max_digits=4, decimal_places=2
    )
    cant_cuota = models.IntegerField()  # Cantidad Cuota por Año
    cant_desembolso = models.IntegerField(default=1, null=True)
    fec_desembolso = models.DateField(
        verbose_name="Fecha Desembolso", blank=True, null=True
    )
    fec_1er_vencimiento = models.DateField(
        verbose_name="Fecha Primer Vencimiento", blank=True, null=True
    )
    total_interes = models.DecimalField(
        verbose_name="Total Interes", max_digits=14, decimal_places=2, default=0
    )
    liquidado = models.CharField(
        verbose_name="Liquidado", max_length=1, choices=choiceSiNo(), default="N"
    )
    nro_acta = models.CharField(
        verbose_name="Nro. Acta", max_length=20, blank=True, null=True
    )
    fec_acta = models.DateField(verbose_name="Fecha Acta", blank=True, null=True)
    nro_resolucion = models.CharField(
        verbose_name="Nro. Resolucion", max_length=20, blank=True, null=True
    )
    forma_desembolso = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab__cod_referencia": "FORMA_DESEMBOLSO"},
        db_column="forma_desembolso",
        on_delete=models.RESTRICT,
        related_name="forma_desembolso_solicitud",
        max_length=4,
        default="EFEC",
    )
    situacion_solicitud = models.ForeignKey(
        SituacionSolicitud, verbose_name="Situacion Solicitud", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.nro_solicitud} - {self.cliente} - {self.nro_prestamo}"

    def toJSON(self):
        # item = model_to_dict(self)
        # item = json.dumps(item, default=str)
        item = {}
        item["id"] = str(self.id)
        item["nro_solicitud"] = str(self.nro_solicitud)
        item["monto_solicitado"] = format(self.monto_solicitado, ",.0f").replace(
            ",", "."
        )
        item["cliente"] = str(self.cliente.persona)
        item["telefono"] = (
            self.cliente.persona.telefono
            if self.cliente.persona.telefono
            else self.cliente.persona.celular
        )
        item["fec_solicitud"] = (
            self.fec_solicitud.strftime("%d/%m/%Y") if self.fec_solicitud else None
        )
        # La fecha de acta indica la APROBACION O DESAPROBACION DEL CREDITO OP 503
        item["fec_acta"] = self.fec_acta.strftime("%d/%m/%Y") if self.fec_acta else None
        item["estado"] = self.estado.denominacion
        item["tipo_prestamo"] = self.tipo_prestamo.denominacion
        item["fec_desembolso"] = (
            self.fec_desembolso.strftime("%d/%m/%Y") if self.fec_desembolso else None
        )
        item["fec_1er_vencimiento"] = (
            self.fec_1er_vencimiento.strftime("%d/%m/%Y")
            if self.fec_1er_vencimiento
            else None
        )
        item["fec_desembolso_ymd"] = (
            self.fec_desembolso.strftime("%Y-%m-%d") if self.fec_desembolso else None
        )
        item["fec_1er_vencimiento_ymd"] = (
            self.fec_1er_vencimiento.strftime("%Y-%m-%d")
            if self.fec_1er_vencimiento
            else None
        )

        return item

    class Meta:
        db_table = "pr_solicitud_prestamo"
        verbose_name = "Solicitud de Prestamo"
        verbose_name_plural = "Solicitudes de Prestamos"


# ***********************************************
# * PROFORMA DE CUOTAS DE PRESTAMO
# * SE GENERA CON LA SOLICITUD DE PRESTAMO
# * APROBADO LA SOLICITUD SE INSERTA EN LA TABLA PR_CUOTAS
# ***********************************************
class ProformaCuota(ModeloBase):
    solicitud_prestamo = models.ForeignKey(
        SolicitudPrestamo,
        db_column="nro_solicitud",
        verbose_name="Solicitud Prestamo",
        on_delete=models.RESTRICT,
        related_name="solicitud",
        to_field="nro_solicitud",
        blank=True,
        null=True,
    )
    nro_cuota = models.IntegerField()
    fec_vencimiento = models.DateField(verbose_name="Fecha Vencimiento")
    saldo_anterior_capital = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    amortizacion = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    aporte_extraordinario = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    comision = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    seguro_vida = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tasa_interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def toJSON(self):
        item = {}
        item["id"] = str(self.id)
        item["nro_cuota"] = str(self.nro_cuota)
        item["fec_vencimiento"] = (
            self.fec_vencimiento.strftime("%d/%m/%Y") if self.fec_vencimiento else None
        )
        item["saldo_anterior_capital"] = format(self.saldo_anterior_capital, ".0f")
        item["amortizacion"] = format(self.amortizacion, ".0f")
        item["interes"] = format(self.interes, ".0f")
        item["comision"] = format(self.comision, ".0f")
        item["monto_cuota"] = format(
            (self.amortizacion + self.interes + self.comision), ".0f"
        )
        return item

    class Meta:
        db_table = "pr_proforma_cuota"
        verbose_name = "Proforma Cuota"
        verbose_name_plural = "Proforma Cuotas"


# ***********************************************
# * PRESTAMOS
# ***********************************************
class Prestamo(ModeloBase):
    nro_prestamo = models.CharField(
        verbose_name="Nro. Prestamo",
        db_column="nro_prestamo",
        max_length=10,
        unique=True,
        # null=True,
        # blank=True,
    )
    rubro_contable = models.ForeignKey(
        PlanDeCuenta,
        to_field="cod_cuenta_contable",
        db_column="rubro_contable",
        on_delete=models.PROTECT,
        related_name="rubro_contable_prestamo",
    )
    cod_tipo_operativa = models.ForeignKey(
        OperativaContable,
        to_field="cod_tipo_operativa",
        db_column="cod_tipo_operativa",
        on_delete=models.RESTRICT,
        # related_name="plazo_operativa_contable",
        # max_length=1,
    )
    sucursal = models.ForeignKey(
        Sucursal, verbose_name="Sucursal", on_delete=models.PROTECT
    )
    cliente = models.ForeignKey(
        Cliente,
        db_column="cod_cliente",
        verbose_name="Cliente",
        on_delete=models.PROTECT,
    )
    nro_solicitud = models.ForeignKey(
        SolicitudPrestamo,
        db_column="nro_solicitud",
        verbose_name="Solicitud Prestamo",
        on_delete=models.RESTRICT,
        related_name="solicitud_prestamo",
        to_field="nro_solicitud",
        blank=True,
        null=True,
    )
    tipo_prestamo = models.ForeignKey(
        TipoPrestamo, verbose_name="Tipo Prestamo", on_delete=models.PROTECT
    )
    destino_prestamo = models.ForeignKey(
        DestinoPrestamo, verbose_name="Destino Prestamo", on_delete=models.PROTECT
    )
    nro_acta_aprobacion = models.CharField(max_length=15)
    fec_aprobacion = models.DateField(verbose_name="Fecha Aprobacion")
    nro_resolucion = models.CharField(max_length=15, null=True, blank=True)
    cant_desembolso = models.IntegerField()
    cant_desembolsado = models.IntegerField()
    importe_desembolsado = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    fec_ult_desembolso = models.DateField(verbose_name="Fecha Ultimo Desembolso")
    fec_1er_vencimiento = models.DateField(verbose_name="Fecha Primer Vencimiento")
    cant_cuota_extraordinario = models.IntegerField(default=0)
    monto_amortizacion = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    fec_1ra_amortizacion = models.DateField(
        verbose_name="Fecha Primera Amortizacion", null=True, blank=True
    )
    periodo_amortizacion = models.IntegerField(default=0, null=True, blank=True)
    tasa_interes = models.DecimalField(
        verbose_name="Tasa Interes", default=0, max_digits=4, decimal_places=2
    )
    plazo = models.ForeignKey(Plazo, verbose_name="Plazo", on_delete=models.PROTECT)
    plazo_meses = models.IntegerField()
    cant_cuota_anho = models.IntegerField(default=12)
    monto_cuota_inicial = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    linea_credito = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    importe_prestamo = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    saldo_capital = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    saldo_interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    ult_cuota_pagada = models.IntegerField(default=0)
    fec_ult_pago = models.DateField(
        verbose_name="Fecha Ultimo Pago", null=True, blank=True
    )
    fec_ult_vto_pago = models.DateField(
        verbose_name="Fecha Ultimo Vencimiento Pago", null=True, blank=True
    )
    situacion_prestamo = models.ForeignKey(
        SituacionPrestamo,
        to_field="cod",
        db_column="situacion_prestamo",
        on_delete=models.RESTRICT,
        max_length=4,
    )
    capital_vencido = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    forma_desembolso = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_cod_referencia": "FORMA_DESEMBOLSO"},
        db_column="forma_desembolso",
        on_delete=models.RESTRICT,
        related_name="forma_desembolso_prestamo",
        max_length=4,
        default="EFEC",
    )
    cod_movimiento = models.CharField(
        verbose_name="Codigo Movimiento", max_length=8, null=True, blank=True
    )
    fec_movimiento = models.DateField(
        verbose_name="Fecha Movimiento", null=True, blank=True
    )
    estado_desembolso = models.ForeignKey(
        EstadoDesembolso,
        to_field="cod",
        db_column="estado_desembolso",
        on_delete=models.RESTRICT,
        max_length=4,
        default="PEND",
    )
    nro_orden_pago = models.CharField(max_length=13, null=True, blank=True)
    nro_prestamo_anterior = models.CharField(max_length=20, null=True, blank=True)
    moneda = models.ForeignKey(Moneda, verbose_name="Moneda", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nro_solicitud} - {self.cliente}"

    def toJSON(self):
        # item = model_to_dict(self)
        item = {}
        item["id"] = str(self.id)
        item["nro_solicitud"] = str(self.nro_solicitud)
        item["cliente"] = str(self.cliente.persona)
        item["telefono"] = self.cliente.persona.telefono
        # item["fec_solicitud"] = (
        #     self.fec_solicitud.strftime("%d/%m/%Y") if self.fec_solicitud else None
        # )
        # # La fecha de acta indica la APROBACION O DESAPROBACION DEL CREDITO OP 503
        # item["fec_acta"] = self.fec_acta.strftime("%d/%m/%Y") if self.fec_acta else None
        # item["estado"] = self.estado.denominacion
        return item

    class Meta:
        db_table = "pr_prestamo"
        verbose_name = "Prestamo"
        verbose_name_plural = "Prestamos"


# ***********************************************
# * SITUACION DE SOLICITUDES DE PRESTAMOS
# ***********************************************
class SituacionSolicitudPrestamo(ModeloBase):
    nro_solicitud = models.ForeignKey(
        SolicitudPrestamo,
        to_field="nro_solicitud",
        db_column="nro_solicitud",
        on_delete=models.PROTECT,
        # related_name="",
    )
    situacion_solicitud = models.ForeignKey(
        SituacionSolicitud,
        on_delete=models.PROTECT,
        # related_name="",
    )
    fecha = models.DateField()
    comentario = models.CharField(verbose_name="Comentario", max_length=200)
    nro_acta = models.CharField(
        verbose_name="Nro. Acta", max_length=20, blank=True, null=True
    )
    fec_acta = models.DateField(verbose_name="Fecha Acta", blank=True, null=True)
    nro_resolucion = models.CharField(
        verbose_name="Nro. Resolucion", max_length=20, blank=True, null=True
    )
    nro_prestamo = models.ForeignKey(
        Prestamo,
        to_field="nro_prestamo",
        db_column="nro_prestamo",
        on_delete=models.PROTECT,
        null=True,
    )
    monto_aprobado = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "pr_situacion_solicitud_prestamo"
        verbose_name = "Situacion Solicitud Prestamo"
        verbose_name_plural = "Situacion Solicitud Prestamo"


# ***********************************************
# * CUOTAS DE PRESTAMOS
# ***********************************************
class Cuotas(ModeloBase):
    nro_prestamo = models.ForeignKey(
        Prestamo,
        db_column="nro_prestamo",
        verbose_name="Prestamo",
        on_delete=models.RESTRICT,
        related_name="prestamo",
        to_field="nro_prestamo",
    )
    nro_cuota = models.IntegerField()
    fec_vencimiento = models.DateField(verbose_name="Fecha Vencimiento")
    tasa_interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    saldo_anterior_capital = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    # *AMORTIZACION
    amortizacion = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    pago_amortizacion = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    # *INTERES
    interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    interes_actual = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    pago_interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    quita_interes = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    # *APORTE EXTRAORDINARIO
    aporte_extraordinario = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    pago_aporte_extraordinario = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    # *COMISION
    comision = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    pago_comision = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    # *SEGURO DE VIDA
    seguro_vida = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    pago_seguro_vida = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    # *MORATORIO
    moratorio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    pago_moratorio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    quita_moratorio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    # *PUNITORIO
    punitorio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    pago_punitorio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    quita_punitorio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    # *CONTROL PAGOS
    fec_movimiento_anterior = models.DateField(null=True)
    fec_pago = models.DateField(null=True)
    cod_movimiento = models.CharField(
        verbose_name="Codigo Movimiento", max_length=8, null=True, blank=True
    )
    pagado = models.BooleanField(default=False)
    parcial = models.BooleanField(default=False)
    quita = models.BooleanField(default=False)
    cod_usuario = models.CharField(max_length=4, null=True, blank=True)

    class Meta:
        db_table = "pr_cuotas"
        verbose_name = "Cuotas del Prestamo"
        verbose_name_plural = "Cuotas del Prestamo"


# ***********************************************
# * LIQUIDACIONES DE PRESTAMOS
# ***********************************************
class LiquidacionPrestamo(ModeloBase):
    nro_solicitud = models.ForeignKey(
        SolicitudPrestamo,
        to_field="nro_solicitud",
        db_column="nro_solicitud",
        on_delete=models.PROTECT,
    )
    nro_prestamo = models.ForeignKey(
        Prestamo,
        to_field="nro_prestamo",
        db_column="nro_prestamo",
        on_delete=models.PROTECT,
    )
    fec_desembolso = models.DateField()
    fec_1er_vencimiento = models.DateField()

    class Meta:
        db_table = "pr_liquidacion_prestamo"
        verbose_name = "Liquidacion de Prestamo"
        verbose_name_plural = "Liquidaciones de Prestamos"


# ***********************************************
# * LIQUIDACIONES DE PRESTAMOS DETALLE
# ***********************************************
class LiquidacionPrestamoDetalle(ModeloBase):
    nro_prestamo = models.ForeignKey(
        Prestamo,
        to_field="nro_prestamo",
        db_column="nro_prestamo",
        on_delete=models.PROTECT,
    )
    nro_prestamo_refinanciado = models.ForeignKey(
        Prestamo,
        to_field="nro_prestamo",
        db_column="nro_prestamo_refinanciado",
        on_delete=models.PROTECT,
        related_name="prestamo_refinanciado",
        null=True,
        blank=True,
    )
    nro_cta_ahorro = models.CharField(max_length=12, null=True, blank=True)
    nombre_campo = models.CharField(max_length=50, null=True, blank=True)
    rubro_contable = models.ForeignKey(
        PlanDeCuenta,
        to_field="cod_cuenta_contable",
        db_column="rubro_contable",
        on_delete=models.PROTECT,
        related_name="rubro_contable_liquidacion_prestamo",
    )
    descripcion = models.CharField(max_length=50, null=True, blank=True)
    importe_debito = models.DecimalField(max_digits=14, decimal_places=2)
    importe_credito = models.DecimalField(max_digits=14, decimal_places=2)
    modulo = models.ForeignKey(
        Modulo, db_column="cod_modulo", verbose_name="Modulo", on_delete=models.RESTRICT
    )
    transaccion = models.ForeignKey(
        Transaccion,
        verbose_name="Transaccion",
        db_column="cod_transaccion",
        on_delete=models.PROTECT,
    )
    contabilizado = models.BooleanField(default=False)

    class Meta:
        db_table = "pr_liquidacion_prestamo_detalle"
        verbose_name = "Liquidacion de Prestamo Detalle"
        verbose_name_plural = "Liquidaciones de Prestamos Detalles"



# ***********************************************
# * DESEMBOLSO DE PRESTAMOS
# ***********************************************
class DesembolsoPrestamo(ModeloBase):
    sucursal = models.ForeignKey(
        Sucursal, verbose_name="Sucursal", on_delete=models.PROTECT
    )
    nro_solicitud = models.ForeignKey(
        SolicitudPrestamo,
        db_column="nro_solicitud",
        verbose_name="Solicitud Prestamo",
        on_delete=models.RESTRICT,
        related_name="solicitud_desembolso",
        to_field="nro_solicitud",
        blank=True,
        null=True,
    )
    nro_prestamo = models.ForeignKey(
        Prestamo,
        db_column="nro_prestamo",
        verbose_name="Nro. Prestamo",
        on_delete=models.RESTRICT,
        related_name="prestamo_desembolso",
        to_field="nro_prestamo",
        blank=True,
        null=True,
    )
    nro_desembolso = models.IntegerField()
    monto_previsto = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    fecha_prevista = models.DateField()
    monto_desembolsado = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    fecha_desembolsado = models.DateField()
    monto_retencion_garantia = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    procesado = models.BooleanField(default=False)
    cod_movimiento = models.CharField(verbose_name="Codigo Movimiento", max_length=8, null=True, blank=True)
    
    class Meta:
        db_table = "pr_desembolso_prestamo"
        verbose_name = "Desembolso de Prestamo"
        verbose_name_plural = "Desembolsos de Prestamos"


# ***********************************************
# * PRESTAMO REFINANCIADO
# ***********************************************
class PrestamoRefinanciado(models.Model):
    nro_prestamo = models.ForeignKey(
        Prestamo,
        db_column="nro_prestamo",
        verbose_name="Nro. Prestamo",
        on_delete=models.RESTRICT,
        related_name="prestamo_refinanciado_new",
        to_field="nro_prestamo",
        blank=True,
        null=True,
    )
    nro_prestamo_refinanciado = models.ForeignKey(
        Prestamo,
        db_column="nro_prestamo_refinanciado",
        verbose_name="Nro. Prestamo Refinanciado",
        on_delete=models.RESTRICT,
        related_name="prestamo_refinanciado_old",
        to_field="nro_prestamo",
        blank=True,
        null=True,
    )
    nro_solicitud = models.ForeignKey(
        SolicitudPrestamo,
        db_column="nro_solicitud",
        verbose_name="Solicitud Prestamo",
        on_delete=models.RESTRICT,
        related_name="solicitud_prestamo_refinanciado",
        to_field="nro_solicitud",
        blank=True,
        null=True,
    )
    tipo_prestamo = models.ForeignKey(
        TipoPrestamo, verbose_name="Tipo Prestamo", on_delete=models.PROTECT
    )
    saldo_suscripcion = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_saldo = models.DateTimeField()

    class Meta:
        db_table = "pr_prestamo_refinanciado"
        verbose_name = "Prestamo Refinanciado"
        verbose_name_plural = "Prestamos Refinanciados"

