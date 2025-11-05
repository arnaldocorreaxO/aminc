import os
import re
from django.templatetags.static import static

from core.models import ModeloBase
from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import model_to_dict
from config import settings as setting

from core.base.choices import *
from core.base.utils import calculate_age

# Create your models here.
"""REFERENCIA CABECERA"""
class RefCab(ModeloBase):
    cod_referencia = models.CharField(
        verbose_name="Codigo Referencia", max_length=100,null=True,blank=True
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50)

    def __str__(self):
        return "{} - {}".format(self.cod_referencia, self.denominacion)

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "bs_refcab"
        verbose_name = "Referencia Cabecera"
        verbose_name_plural = "Referencias Cabecera"


"""REFERENCIA DETALLE"""
class RefDet(ModeloBase):
    refcab = models.ForeignKey(
        RefCab,
        verbose_name="Referencia Cabecera",
        on_delete=models.RESTRICT,
        related_name="referencia",
    )
    cod_referencia = models.CharField(
        verbose_name="Codigo Referencia", max_length=100,null=True,blank=True
    )
    denominacion = models.CharField(verbose_name="Denominacion", max_length=50) #Nombre Referencia
    descripcion = models.CharField(verbose_name="Descripción", max_length=50,null=True,blank=True)#Descripcion Referencia
    valor_alfanumerico = models.CharField(verbose_name="Valor Alfanumerico", max_length=100, null=True, blank=True)
    valor_numerico = models.DecimalField(verbose_name="Valor Numérico", max_digits=18, decimal_places=4, null=True, blank=True)   
    valor_fecha = models.DateField(verbose_name="Valor Fecha", null=True, blank=True)
    valor_unico = models.CharField(verbose_name="Valor Único", max_length=25,unique=True,null=True) # Valor unico para relacionar en otras tablas

    def __str__(self):
        return self.denominacion or ""

    # Generar valor unico automatico si no se ingresa
    def save(self, *args, **kwargs):
        if not self.valor_unico:
            # Guardar primero para obtener el ID
            super().save(*args, **kwargs)
            self.valor_unico = str(self.id)
            # Guardar solo el campo actualizado
            super().save(update_fields=["valor_unico"])
        else:
            super().save(*args, **kwargs)

    class Meta:
        # ordering = ['tip_movimiento',]
        db_table = "bs_refdet"
        verbose_name = "Referencia Detalle"
        verbose_name_plural = "Referencias Detalle"
        unique_together = ["refcab", "valor_unico"]


"""MESES"""
class Meses(ModeloBase):
    # id = models.CharField('Código',db_column='cod_modulo',max_length=2,primary_key=True)
    mes = models.IntegerField("Mes", db_column="mes", primary_key=True)
    denominacion = models.CharField(max_length=20, unique=True)
    cant_dias = models.IntegerField()

    def __str__(self):
        return f"{self.mes} - {self.denominacion}"

    class Meta:
        # ordering = ['id', ]
        db_table = "bs_meses"
        verbose_name = "meses"
        verbose_name_plural = "meses"


"""MODULOS"""
class Modulo(ModeloBase):
    cod_modulo = models.CharField(
        "Código", db_column="cod_modulo", max_length=2, primary_key=True
    )
    denominacion = models.CharField(max_length=100, unique=True)
    tipo_cartera = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_id": 12},
        db_column="tipo_cartera",
        on_delete=models.RESTRICT,
        related_name="modulo_tipo_cartera",
        max_length=1,
        default="N",
    )

    def __str__(self):
        return f"{self.cod_modulo} - {self.denominacion}"

    class Meta:
        # ordering = ['id', ]
        db_table = "bs_modulo"
        verbose_name = "modulo"
        verbose_name_plural = "modulos"


"""TRANSACION"""
class Transaccion(ModeloBase):
    cod_transaccion = models.IntegerField(verbose_name="Código", primary_key=True)
    modulo = models.ForeignKey(
        Modulo,
        db_column="cod_modulo",
        verbose_name="Modulo",
        on_delete=models.RESTRICT,
        related_name="transacciones",
    )
    denominacion = models.CharField(
        verbose_name="Transaccion", max_length=100, unique=True
    )
    tipo_dc = models.CharField(
        verbose_name="Tipo", max_length=1, choices=choiceTipoDC()
    )
    tipo_acceso = models.CharField(
        verbose_name="Tipo Acceso", max_length=1, choices=choiceTipoAcceso()
    )
    abreviatura = models.CharField(verbose_name="Abreviatura", max_length=15)
    imprime_comprobante = models.BooleanField(
        verbose_name="Imprime Comprobante", null=True, blank=True, default=False
    )
    transaccion_por_defecto = models.BooleanField(
        verbose_name="Transacción Por Defecto", null=True, blank=True, default=False
    )
    url = models.CharField(
        max_length=100, verbose_name="Url", unique=True, null=True, blank=True
    )
    requiere_cliente = models.BooleanField(
    default=False,
    verbose_name="Requiere Cliente",
    help_text="Indica si esta transacción requiere un código de cliente para ejecutarse"
    )


    # Si la transaccion es por defecto, automaticamente es la opcion disponible para los movimientos, si no se elige otra opcion
    def __str__(self):
        return f"{self.cod_transaccion}-{self.denominacion}"
    
    @property
    def script_url(self):
        """
        Deriva la ruta del script JavaScript asociado a la transacción.
        Convierte '/modulo/trxXXX/' → '/static/modulo/js/trxXXX.js'
        Mantiene una única fuente de verdad en el campo `url`.
        """
        if self.url:
            ruta = self.url.lstrip("/")  # quita el primer / para evitar /static//
            ruta_js = re.sub(r"^(.*/)?trx(\d+)/$", r"\1js/trx\2.js", ruta)
            return static(ruta_js)
        return ""



    def toJSON(self):
        # Serializa los datos clave de la transacción para uso en el frontend
        # Incluye la URL de ejecución y la ruta del script derivada automáticamente
        return {
            "cod_transaccion": self.cod_transaccion,
            "denominacion": self.denominacion,
            "modulo": self.modulo.cod_modulo,
            "url": self.url,
            "script": self.script_url,
            "requiere_cliente": self.requiere_cliente,
        }

    class Meta:
        ordering = [
            "cod_transaccion",
        ]
        db_table = "bs_transaccion"
        verbose_name = "Transaccion"
        verbose_name_plural = "Transacciones"


"""PARAMETROS GENERALES"""
class Parametro(ModeloBase):
    modulo = models.ForeignKey(
        Modulo, verbose_name="Modulo", on_delete=models.RESTRICT, related_name="modulos"
    )
    parametro = models.CharField(max_length=25, unique=True)
    descripcion = models.CharField(max_length=100, unique=True)
    valor = models.CharField(max_length=100)

    def __str__(self):
        return "%s - %s " % (self.parametro, self.valor)

    class Meta:
        ordering = [
            "parametro",
        ]
        db_table = "bs_parametro"
        verbose_name = "Parametro"
        verbose_name_plural = "Parametros"


# PAISES
class Pais(ModeloBase):
    # ID
    cod = models.CharField(verbose_name="Código", max_length=3, unique=True)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )
    nacionalidad = models.CharField(
        verbose_name="Nacionalidad", max_length=100, unique=True, null=True, blank=True
    )

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_pais"
        verbose_name = "Pais"
        verbose_name_plural = "Paises"

# DEPARTAMENTO
class Departamento(ModeloBase):
    # ID
    pais = models.ForeignKey(
        Pais, verbose_name="Pais", on_delete=models.RESTRICT, related_name="paises"
    )
    denominacion = models.CharField(verbose_name="Denominación", max_length=100)

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_departamento"
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        unique_together = ["pais", "denominacion"]

# CIUDAD
class Ciudad(ModeloBase):
    # ID
    departamento = models.ForeignKey(
        Departamento,
        verbose_name="Departamento",
        on_delete=models.RESTRICT,
        related_name="departamento",
    )
    denominacion = models.CharField(verbose_name="Denominación", max_length=100)

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_ciudad"
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        # unique_together = ["departamento", "denominacion"]


# BARRIO
class Barrio(ModeloBase):
    # ID
    ciudad = models.ForeignKey(
        Ciudad,
        verbose_name="Ciudad",
        on_delete=models.RESTRICT,
        related_name="ciudades",
    )
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    def toJSON(self):
        return model_to_dict(self)

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_barrio"
        verbose_name = "Barrio"
        verbose_name_plural = "Barrios"
        unique_together = ["ciudad", "denominacion"]


# EMPRESA
class Empresa(ModeloBase):
    ruc = models.CharField(
        verbose_name="RUC", max_length=10, validators=[MinLengthValidator(6)]
    )
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )
    nombre_fantasia = models.CharField(
        verbose_name="Nombre de Fantasía", max_length=100, unique=True
    )
    direccion = models.CharField(verbose_name="Dirección", max_length=100)
    telefono = models.CharField(verbose_name="Teléfono", max_length=20)
    celular = models.CharField(
        verbose_name="Celular", max_length=20, null=True, blank=True
    )
    email = models.CharField(max_length=50, verbose_name="Email", null=True, blank=True)
    website = models.CharField(
        max_length=250, verbose_name="Página web", null=True, blank=True
    )
    descripcion = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Descripción"
    )
    imagen = models.ImageField(
        null=True, blank=True, upload_to="empresa/%Y/%m/%d", verbose_name="Logo"
    )
    iva = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=9, verbose_name="Iva"
    )

    def __str__(self):
        return self.denominacion

    def getNombreFantasia(self):
        return self.nombre_fantasia

    def get_image(self):
        if self.imagen:
            return "{}{}".format(setting.MEDIA_URL, self.imagen)
        return "{}{}".format(setting.STATIC_URL, "img/default/empty.png")

    def get_iva(self):
        return format(self.iva, ".2f")

    def remove_image(self):
        try:
            if self.imagen:
                os.remove(self.imagen.path)
        except:
            pass
        finally:
            self.imagen = None

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        # ordering = ['1',]
        db_table = "bs_empresa"
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        default_permissions = ()
        permissions = (("view_empresa", "Can view Empresa"),)
        ordering = ["-id"]


"""SUCURSAL"""
class Sucursal(ModeloBase):
    # ID
    empresa = models.ForeignKey(
        Empresa,
        verbose_name="Empresa",
        on_delete=models.RESTRICT,
        related_name="empresa",
    )
    cod = models.CharField(verbose_name="Código", max_length=3)
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )
    denominacion_corta = models.CharField(
        verbose_name="Denominación Corta",
        max_length=25,
        unique=True,
        null=True,
        blank=True,
    )
    denominacion_puesto = models.CharField(
        verbose_name="Denominación de Puesto",
        max_length=35,
        unique=True,
        null=True,
        blank=True,
    )
    direccion = models.CharField(verbose_name="Dirección", max_length=100)
    telefono = models.CharField(verbose_name="Teléfono", max_length=100)

    def __str__(self):
        return "{}".format(self.denominacion)

    def get_short_name(self):
        return "{}".format(self.denominacion_corta)

    class Meta:
        # ordering = ['1',]
        db_table = "bs_sucursal"
        verbose_name = "sucursal"
        verbose_name_plural = "sucursales"


# MONEDA
class Moneda(ModeloBase):
    # ID
    cod_moneda = models.CharField(verbose_name="Código", max_length=3, unique=True)
    iso = models.CharField(verbose_name="ISO", max_length=3, unique=True)
    denominacion = models.CharField(verbose_name="Denominación", max_length=100)
    decimales = models.IntegerField(verbose_name="Decimales")
    fec_cotizacion = models.DateField(verbose_name="Fecha Cotizacion")
    precio_compra = models.FloatField(verbose_name="Precio Compra")
    precio_venta = models.FloatField(verbose_name="Precio Venta")

    def __str__(self):
        return "{}".format(self.denominacion)

    class Meta:
        # ordering = ['1',]
        db_table = "bs_moneda"
        verbose_name = "moneda"
        verbose_name_plural = "monedas"


# TIPOS DE COMPROBANTES FACTURA, RECIBO,ETC
class TipoComprobante(ModeloBase):
    # ID
    tip_comprobante = models.CharField(
        verbose_name="Tipo Comprobante", max_length=6, unique=True
    )
    descripcion = models.CharField(verbose_name="Descripción", max_length=100)
    operacion_stock = models.CharField(
        verbose_name="Operacion Stock",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceOperacionSaldo(),
    )
    operacion_saldo = models.CharField(
        verbose_name="Operacion Saldo",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceOperacionSaldo(),
    )
    ver_en_recibo = models.CharField(
        verbose_name="Ver en Recibo",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceSiNo(),
    )
    ver_en_compra = models.CharField(
        verbose_name="Ver en Compra",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceSiNo(),
    )
    ver_en_venta = models.CharField(
        verbose_name="Ver en Venta",
        max_length=1,
        blank=True,
        null=True,
        choices=choiceSiNo(),
    )
    cant_lineas = models.IntegerField(verbose_name="Cantidad de Lineas Pre-Impreso")

    def __str__(self):
        return "{} - {}".format(self.tip_comprobante, self.descripcion)

    class Meta:
        # ordering = ['1',]
        db_table = "bs_tipo_comprobante"
        verbose_name = "Tipo de Comprobante"
        verbose_name_plural = "Tipos de Comprobantes"


# SECTOR OPERATIVO
class SectorOperativo(ModeloBase):
    # ID
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name="Sucursal",
        on_delete=models.RESTRICT,
        related_name="fk_sucursal_%(app_label)s_%(class)s",
    )
    denominacion = models.CharField(
        verbose_name="Denominación", max_length=100, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.pk, self.denominacion)

    class Meta:
        ordering = [
            "pk",
        ]
        db_table = "bs_sector_operativo"
        verbose_name = "Sector Operativo"
        verbose_name_plural = "Sectores Operativos"


# TIPO MOVIMIENTO
class Caja(ModeloBase):
    nro_caja = models.IntegerField(
        verbose_name="Nro. Caja", db_column="nro_caja", primary_key=True
    )
    denominacion = models.CharField(verbose_name="Caja", max_length=100, unique=True)
    impresora1 = models.CharField(
        verbose_name="Impresora 1", max_length=100, blank=True, null=True
    )
    impresora2 = models.CharField(
        verbose_name="Impresora 2", max_length=100, blank=True, null=True
    )

    def __str__(self):
        return "{} - {}".format(self.nro_caja, self.denominacion)

    class Meta:
        ordering = [
            "nro_caja",
        ]
        db_table = "bs_caja"
        verbose_name = "caja"
        verbose_name_plural = "cajas"


# TIPO MOVIMIENTO
class CajaComprobante(ModeloBase):
    sucursal = models.ForeignKey(
        Sucursal, verbose_name="Sucursal", on_delete=models.RESTRICT, null=True
    )
    nro_caja = models.ForeignKey(
        Caja, verbose_name="Nro. Caja", db_column="nro_caja", on_delete=models.RESTRICT
    )
    tip_comprobante = models.ForeignKey(
        TipoComprobante,
        verbose_name="Tipo Comprobante",
        db_column="tip_comprobante",
        to_field="tip_comprobante",
        on_delete=models.RESTRICT,
    )
    nro_timbrado = models.IntegerField(verbose_name="Nro. Timbrado")
    nro_ini_comprobante = models.BigIntegerField(
        verbose_name="Nro. Comprobante Inicial"
    )
    nro_fin_comprobante = models.BigIntegerField(verbose_name="Nro. Comprobante Final")
    nro_act_comprobante = models.BigIntegerField(verbose_name="Nro. Comprobante Actual")
    fec_vigencia_desde = models.DateField(
        verbose_name="Fecha Vigencia Desde", null=True
    )
    fec_vigencia_hasta = models.DateField(
        verbose_name="Fecha Vigencia Hasta", null=True
    )

    def __str__(self):
        return "{} - {}".format(self.nro_caja, self.tip_comprobante)

    class Meta:
        # ordering = ['nro_caja',]
        db_table = "bs_caja_comprobante"
        verbose_name = "Caja Comprobante"
        verbose_name_plural = "Caja Comprobantes"
        unique_together = ["sucursal", "nro_caja", "tip_comprobante", "nro_timbrado"]


# PERSONA
class Persona(ModeloBase):
    ci = models.BigIntegerField(verbose_name="CI", unique=True)
    ruc = models.CharField(
        verbose_name="RUC",
        max_length=10,
        validators=[MinLengthValidator(6)],
        unique=True,
        null=True,
        blank=True,
    )
    nombre = models.CharField(verbose_name="Nombre", max_length=150)
    apellido = models.CharField(verbose_name="Apellido", max_length=150)
    nacionalidad = models.ForeignKey(
        Pais, verbose_name="Nacionalidad", on_delete=models.RESTRICT
    )
    ciudad = models.ForeignKey(
        Ciudad, verbose_name="Ciudad", on_delete=models.RESTRICT, null=True, blank=True
    )
    barrio = models.ForeignKey(
        Barrio, verbose_name="Barrio", on_delete=models.RESTRICT, null=True, blank=True
    )
    direccion = models.CharField(
        verbose_name="Dirección", max_length=100, null=True, blank=True
    )
    telefono = models.CharField(
        verbose_name="Teléfono", max_length=20, null=True, blank=True
    )
    celular = models.CharField(
        verbose_name="Celular", max_length=20, null=True, blank=True
    )
    email = models.CharField(max_length=50, verbose_name="Email", null=True, blank=True)
    fec_nacimiento = models.DateField(verbose_name="Fecha Nacimiento", null=True)
    sexo = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        verbose_name="Genero",
        db_column="sexo",
        on_delete=models.RESTRICT,
        related_name="sexo",
        max_length=1,
        blank=True,
        null=True,
    )
    estado_civil = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        verbose_name="Estado Civil",
        db_column="estado_civil",
        on_delete=models.RESTRICT,
        related_name="estado_civil",
        max_length=2,
        blank=True,
        null=True,
    )

    def get_full_name(self):
        return "{}, {}".format(self.nombre, self.apellido)

    def __str__(self):
        return "{}, {}".format(self.nombre, self.apellido)

    def get_edad(self):
        return calculate_age(self.fec_nacimiento)

    def toJSON(self):
        item = model_to_dict(self)
        item["edad"] = self.get_edad()
        return item

    class Meta:
        db_table = "bs_persona"
        verbose_name = "Persona"
        verbose_name_plural = "Personas"


# MOVIMIENTOS BASE

from core.general.models import Cliente
from core.contable.models import PlanDeCuenta

# TIPO MOVIMIENTO
class TipoMovimiento(ModeloBase):
    tip_movimiento = models.CharField(
        verbose_name="Código", max_length=1, primary_key=True
    )
    denominacion = models.CharField(
        verbose_name="Tipo Movimiento", max_length=100, unique=True
    )

    def __str__(self):
        return "{} - {}".format(self.tip_movimiento, self.denominacion)

    class Meta:
        ordering = [
            "tip_movimiento",
        ]
        db_table = "ge_tipo_movimiento"
        verbose_name = "Tipo Movimiento"
        verbose_name_plural = "Tipos Movimientos"

# MOVIMIENTO ABSTRACT
class MovimientoBase(ModeloBase):
    fec_movimiento = models.DateField(verbose_name="Fecha Movimiento")
    cod_movimiento = models.CharField(verbose_name="Codigo Movimiento", max_length=8)
    tip_movimiento = models.ForeignKey(
        TipoMovimiento,
        verbose_name="Tipo",
        db_column="tip_movimiento",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default="A",
    )
    modulo = models.ForeignKey(
        Modulo,
        verbose_name="Modulo",
        db_column="cod_modulo",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    transaccion = models.ForeignKey(
        Transaccion,
        verbose_name="Transacción",
        db_column="cod_transaccion",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    nro_asiento = models.IntegerField(verbose_name="Nro. Asiento", default=0)
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name="Sucursal",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    cliente = models.ForeignKey(
        Cliente,
        db_column="cod_cliente",
        verbose_name="Cliente",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_cliente",
    )
    moneda = models.ForeignKey(
        Moneda, verbose_name="Moneda", on_delete=models.PROTECT, blank=True, null=True
    )
    cotizacion = models.FloatField(verbose_name="Cotizacion", default=1)
    mto_equi_local = models.DecimalField(
        verbose_name="Monto Equivalente Local",
        default=0,
        max_digits=20,
        decimal_places=2,
    )
    rubro_contable = models.ForeignKey(
        PlanDeCuenta,
        verbose_name="Rubro Contable",
        db_column="rubro_contable",
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_rubro_contable",
        blank=True,
        null=True,
    )
    cuenta_operativa = models.CharField(
        verbose_name="Cuenta Operativa", max_length=50, null=True, blank=True
    )
    concepto = models.CharField(verbose_name="Concepto", max_length=100, blank=True)
    debito = models.DecimalField(
        verbose_name="Debito", default=0, max_digits=20, decimal_places=2
    )
    credito = models.DecimalField(
        verbose_name="Credito", default=0, max_digits=20, decimal_places=2
    )
    nombre_campo = models.CharField(
        verbose_name="Nombre Campo", max_length=100, null=True, blank=True, default=None
    )
    referencia = models.CharField(
        verbose_name="Referencia", max_length=100, null=True, blank=True, default=None
    )
    nro_caja = models.ForeignKey(
        Caja,
        verbose_name="Nro. Caja",
        db_column="nro_caja",
        on_delete=models.PROTECT,
        default=0,
        related_name="%(class)s_movimiento",
        blank=True,
        null=True,
    )
    caja_diario = models.CharField(
        verbose_name="Caja Diario",
        max_length=1,
        choices=choiceCajaDiario(),
        default="D",
    )
    nro_documento = models.CharField(
        verbose_name="Nro. Documento", max_length=25, null=True, blank=True
    )
    fec_valor = models.DateField(
        verbose_name="Fecha Valor", blank=True, null=True, default=None
    )
    iva = models.IntegerField(verbose_name="Iva %", default=0)
    monto_iva = models.DecimalField(
        verbose_name="Monto Iva", default=0, max_digits=20, decimal_places=2
    )
    # Compensaciones de Cheques
    cod_compensacion = models.ForeignKey(
        RefDet,
        to_field="valor_unico",
        limit_choices_to={"refcab_id": 11},
        db_column="cod_compensacion",
        on_delete=models.RESTRICT,
        related_name="%(app_label)s_%(class)s_compensacion",
        max_length=1,
        default=0,
    )
    tip_comprobante = models.ForeignKey(
        TipoComprobante,
        verbose_name="Tipo Comprobante",
        db_column="tip_comprobante",
        to_field="tip_comprobante",
        on_delete=models.PROTECT,
    )
    # cod_usuario = models.ForeignKey(
    #     setting.AUTH_USER_MODEL,
    #     verbose_name="Usuario Movimiento",
    #     to_field="cod_usuario",
    #     db_column="cod_usuario",
    #     on_delete=models.PROTECT,
    #     related_name="%(app_label)s_%(class)s_usuario_movimiento",
    #     blank=True,
    #     null=True,
    # )

    class Meta:
        abstract = True


"""MOVIMIENTOS DIARIOS"""


class Movimiento(MovimientoBase):
    def toJSON(self):
        item = model_to_dict(self)
        # item = {}
        item["placta"] = {"rubro_contable": str(self.rubro_contable)}
        item["debito"] = format(self.debito, ".2f")
        item["credito"] = format(self.credito, ".2f")
        item["fec_movimiento"] = (
            self.fec_movimiento.strftime("%d/%m/%Y") if self.fec_movimiento else None
        )
        item["credito"] = format(self.credito, ".2f")
        item["credito"] = format(self.credito, ".2f")
        item["nro_socio"] = self.cliente.nro_socio
        item["cod_cliente"] = self.cliente.cod_cliente
        item["socio"] = self.cliente.get_nro_socio_nombre()
        item["cod_usuario"] = self.usu_insercion.cod_usuario

        return item

    class Meta:
        # ordering = ['tip_movimiento', ]
        db_table = "cb_movimientos"
        verbose_name = "Movimiento Diario"
        verbose_name_plural = "Movimientos Diarios"


"""MOVIMIENTOS MENSUALES DEL PERIODO ACTUAL"""


class MovimientosMensuales(MovimientoBase):
    def toJSON(self):
        item = model_to_dict(self)
        item["placta"] = {"rubro_contable": str(self.rubro_contable)}
        item["debito"] = format(self.debito, ".2f")
        item["credito"] = format(self.credito, ".2f")
        return item

    class Meta:
        # ordering = ['tip_movimiento', ]
        db_table = "cb_movimientos_mensuales"
        verbose_name = "Movimientos Mensuales"
        verbose_name_plural = "Movimientos Mensuales"


"""MOVIMIENTOS ANUALES HASTA PERIODO ANTERIOR"""


class MovimientosAnuales(MovimientoBase):
    def toJSON(self):
        item = model_to_dict(self)
        item["placta"] = {"rubro_contable": str(self.rubro_contable)}
        item["debito"] = format(self.debito, ".2f")
        item["credito"] = format(self.credito, ".2f")
        return item

    class Meta:
        # ordering = ['tip_movimiento', ]
        db_table = "cb_movimientos_anuales"
        verbose_name = "Movimientos Anuales"
        verbose_name_plural = "Movimientos Anuales"


class TmpMovimiento(MovimientoBase):
    def toJSON(self):
        # item = model_to_dict(self)
        item = {}
        item["transaccion"] = self.transaccion
        item["placta"] = {"rubro_contable": str(self.rubro_contable)}
        item["debito"] = format(self.debito, ".2f")
        item["credito"] = format(self.credito, ".2f")
        return item

    class Meta:
        # ordering = ['tip_movimiento', ]
        db_table = "tmp_movimientos"
        verbose_name = "Movimiento Temporal"
        verbose_name_plural = "Movimientos Temporales"