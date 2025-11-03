from core.base.procedures import SP_EXECUTE
from core.base.utils import RESET_FORMATO, TEXTO, isNULL


def sp_alta_solicitud_prestamo(request):
    cod_usuario = request.user.cod_usuario
    params = {}
    params["sucursal"] = request.POST["sucursal"]
    params["cod_cliente"] = request.POST["cliente"]
    params["tipo_prestamo"] = request.POST["tipo_prestamo"]
    params["fec_solicitud"] = TEXTO(request.POST["fec_solicitud"])
    params["destino_prestamo"] = request.POST["destino_prestamo"]
    params["monto_solicitado"] = request.POST["monto_solicitado"]
    params["monto_prestamo"] = request.POST["monto_prestamo"]
    params["plazo_meses"] = request.POST["plazo_meses"]
    params["moneda"] = request.POST["moneda"]
    params["tasa_interes"] = request.POST["tasa_interes"]
    params["cant_cuota"] = request.POST["cant_cuota"]
    params["monto_cuota_inicial"] = request.POST["monto_cuota_inicial"]
    params["fec_desembolso"] = TEXTO(request.POST["fec_desembolso"])
    params["fec_1er_vencimiento"] = TEXTO(request.POST["fec_1er_vencimiento"])
    params["total_interes"] = request.POST["total_interes"]
    params["monto_neto"] = request.POST["monto_neto"]
    params["usu_actual"] = cod_usuario
    params["forma_desembolso"] = TEXTO(request.POST["forma_desembolso"])
    params["monto_refinanciado"] = request.POST["monto_refinanciado"]

    print(params)
    storedProc = f"""  
                    DECLARE @RC INT
                    DECLARE @SUCURSAL_ID INT
                    DECLARE @COD_CLIENTE INT
                    DECLARE @NRO_SOLICITUD CHAR(10)
                    DECLARE @TIPO_PRESTAMO_ID INT
                    DECLARE @FEC_SOLICITUD DATETIME
                    DECLARE @DESTINO_PRESTAMO_ID INT
                    DECLARE @MONTO_SOLICITADO NUMERIC(14,2)
                    DECLARE @MONTO_PRESTAMO NUMERIC(14,2)
                    DECLARE @PLAZO_MESES INT
                    DECLARE @MONEDA_ID INT
                    DECLARE @TASA_INTERES NUMERIC(7,2)
                    DECLARE @CANT_CUOTA INT
                    DECLARE @MONTO_CUOTA_INICIAL NUMERIC(14,2)
                    DECLARE @FEC_DESEMBOLSO DATETIME
                    DECLARE @FEC_1ER_VENCIMIENTO DATETIME
                    DECLARE @TOTAL_INTERES NUMERIC(12,2)
                    DECLARE @COD_TIPO_DCTO INT
                    DECLARE @TOTAL_GASTOS NUMERIC(14,2)
                    DECLARE @TOTAL_DESCUENTOS NUMERIC(14,2)
                    DECLARE @MONTO_NETO NUMERIC(14,2)
                    DECLARE @CANT_CUOTA_EXTRAORDINARIO NUMERIC(5,0)
                    DECLARE @MONTO_AMORTIZACION NUMERIC(12,2)
                    DECLARE @FEC_1RA_AMORTIZACION CHAR(10)
                    DECLARE @PERIODO_AMORTIZACION NUMERIC(5,0)
                    DECLARE @COND_LIQUIDACION NUMERIC(5,0)
                    DECLARE @USU_INSERCION NUMERIC(4,0)
                    DECLARE @INGRESO_FAMILIAR NUMERIC(12,2)
                    DECLARE @COD_GRUPO_PRESTAMO NUMERIC(5,0)
                    DECLARE @COD_TIPO_LINEA_CREDITO NUMERIC(8,0)
                    DECLARE @FORMA_DESEMBOLSO INT
                    DECLARE @COD_CTA_AHORRO NUMERIC(10,0)
                    DECLARE @MONTO_REFINANCIADO NUMERIC(14,2)
                    DECLARE @SUSCRIPCION_ADESCONTAR NUMERIC(14,2)
                    DECLARE @CUO_GRACIA_INT_REF NUMERIC(3,0)
                    DECLARE @CNT_CUO_INT_REF NUMERIC(3,0)
                    DECLARE @COD_COMERCIO INT
                    DECLARE @MENSAJE VARCHAR(100)
                    DECLARE @MSG VARCHAR(100)
                    DECLARE @NRO_SOL_GEN VARCHAR(10) --NRO. SOLICITUD GENERADA

                    -- TODO: Establezca los valores de los parámetros aquí.

                    BEGIN TRAN

                    EXECUTE @RC = [dbo].[PA_ALTA_SOLICITUD_PRESTAMO] 
                     @SUCURSAL_ID={params['sucursal']}
                    ,@COD_CLIENTE={params['cod_cliente']}
                    ,@NRO_SOLICITUD=@NRO_SOL_GEN OUTPUT
                    ,@TIPO_PRESTAMO_ID={params['tipo_prestamo']}
                    ,@FEC_SOLICITUD={params['fec_solicitud']}
                    ,@DESTINO_PRESTAMO_ID={params['destino_prestamo']}
                    ,@COD_TIPO_GARANTIA=NULL
                    ,@LIMITE_CREDITO=NULL
                    ,@MONTO_SOLICITADO={params['monto_solicitado']}
                    ,@MONTO_PRESTAMO={params['monto_prestamo']}
                    ,@COD_SISTEMA_CALCULO=NULL
                    ,@PLAZO_MESES={params['plazo_meses']}
                    ,@MONEDA_ID={params['moneda']}
                    ,@TASA_INTERES={params['tasa_interes']}
                    ,@CANT_CUOTA={params['cant_cuota']}
                    ,@MONTO_CUOTA_INICIAL={params['monto_cuota_inicial']}
                    ,@FEC_DESEMBOLSO={params['fec_desembolso']}
                    ,@FEC_1ER_VENCIMIENTO={params['fec_1er_vencimiento']}
                    ,@TOTAL_INTERES={params['total_interes']}
                    ,@TIPO_CUOTA=NULL
                    ,@TIPO_INTERES=NULL
                    ,@COD_TIPO_DCTO=NULL
                    ,@TOTAL_GASTOS=NULL
                    ,@TOTAL_DESCUENTOS=NULL
                    ,@MONTO_NETO={params['monto_neto']}
                    ,@CANT_CUOTA_EXTRAORDINARIO=NULL
                    ,@MONTO_AMORTIZACION=NULL
                    ,@FEC_1RA_AMORTIZACION=NULL
                    ,@PERIODO_AMORTIZACION=NULL
                    ,@COND_LIQUIDACION=NULL
                    ,@USU_INSERCION={params['usu_actual']}
                    ,@INGRESO_FAMILIAR=NULL
                    ,@COD_GRUPO_PRESTAMO=NULL
                    ,@COD_TIPO_LINEA_CREDITO=NULL
                    ,@FORMA_DESEMBOLSO={params['forma_desembolso']}
                    ,@COD_CTA_AHORRO=NULL
                    ,@MONTO_REFINANCIADO={params['monto_refinanciado']}
                    ,@SUSCRIPCION_ADESCONTAR=NULL
                    ,@CUO_GRACIA_INT_REF=NULL
                    ,@CNT_CUO_INT_REF=NULL
                    ,@COD_COMERCIO=NULL                      
                    ,@MENSAJE=@MSG OUTPUT;

                       IF @RC<>0 
                            ROLLBACK TRAN
                        ELSE
                            COMMIT TRAN 

                    SELECT @RC AS RTN, @MSG AS MSG,@NRO_SOL_GEN AS VAL;
    """
    return SP_EXECUTE(storedProc)


def sp_generar_proforma_cuota(request):
    print(request.POST)
    params = {}
    cod_usuario = request.user.cod_usuario
    params["sucursal"] = request.POST["sucursal"]
    params["fec_solicitud"] = TEXTO(request.POST["fec_solicitud"])
    params["nro_solicitud"] = TEXTO(request.POST["nro_solicitud"])
    params["monto_solicitado"] = RESET_FORMATO(request.POST["monto_solicitado"])
    params["monto_prestamo"] = RESET_FORMATO(request.POST["monto_prestamo"])
    params["plazo_meses"] = request.POST["plazo_meses"]
    params["moneda"] = request.POST["moneda"]
    params["tasa_interes"] = RESET_FORMATO(request.POST["tasa_interes"])
    params["cant_cuota"] = request.POST["cant_cuota"]
    params["monto_cuota_inicial"] = RESET_FORMATO(request.POST["monto_cuota_inicial"])
    params["fec_desembolso"] = TEXTO(request.POST["fec_desembolso"])
    params["fec_1er_vencimiento"] = TEXTO(request.POST["fec_1er_vencimiento"])
    params["total_interes"] = RESET_FORMATO(request.POST["total_interes"])
    params["monto_neto"] = RESET_FORMATO(request.POST["monto_neto"])
    params["usu_actual"] = cod_usuario
    params["monto_refinanciado"] = RESET_FORMATO(request.POST["monto_refinanciado"])

    print(params)
    storedProc = f"""
                    DECLARE @RC INT
                    DECLARE @NRO_SOLICITUD CHAR(10)
                    DECLARE @FEC_SOLICITUD DATE
                    DECLARE @FEC_1ER_VENCIMIENTO DATE
                    DECLARE @TASA_INTERES NUMERIC(14,2)
                    DECLARE @PLAZO_MESES INT
                    DECLARE @CANT_CUOTA_ANHO INT
                    DECLARE @MONTO_PRESTAMO NUMERIC(14,2)
                    DECLARE @MONTO_SOLICITADO NUMERIC(14,2)
                    DECLARE @MONTO_NETO NUMERIC(14,2)
                    DECLARE @MONTO_CUOTA NUMERIC(14,2)
                    DECLARE @COD_USUARIO CHAR(4)
                    DECLARE @MENSAJE VARCHAR(100)

                    -- TODO: Establezca los valores de los parámetros aquí.

                    BEGIN TRAN

                    EXECUTE @RC = [dbo].[PA_GENERAR_PROFORMA_CUOTA] 
                    @NRO_SOLICITUD = {params['nro_solicitud']}
                    ,@FEC_SOLICITUD ={params['fec_solicitud']}
                    ,@FEC_1ER_VENCIMIENTO={params['fec_1er_vencimiento']}
                    ,@TASA_INTERES={params['tasa_interes']}
                    ,@PLAZO_MESES={params['plazo_meses']}
                    ,@CANT_CUOTA_ANHO={params['cant_cuota']}
                    ,@MONTO_PRESTAMO={params['monto_prestamo']}
                    ,@MONTO_SOLICITADO={params['monto_solicitado']}
                    ,@MONTO_NETO={params['monto_neto']}
                    ,@COD_USUARIO={params['usu_actual']}
                    ,@MONTO_CUOTA = @MONTO_CUOTA OUTPUT
                    ,@MENSAJE=@MENSAJE OUTPUT
                    
                    IF @RC<>0 
                        ROLLBACK TRAN
                    ELSE
                        COMMIT TRAN 

                    SELECT @RC AS RTN, @MENSAJE AS MSG,@MONTO_CUOTA AS VAL;
    """
    return SP_EXECUTE(storedProc)


def fn_monto_plazo_prestamo(request):
    print(request.POST)
    params = {}
    params["monto_solicitado"] = request.POST["monto_solicitado"]
    params["plazo_solicitado"] = isNULL(request.POST["plazo_solicitado"], "0")

    print(params)
    storedProc = f"""
                DECLARE @VAL NUMERIC(14,2)                  

                -- TODO: Establezca los valores de los parámetros aquí.

                SELECT @VAL = [dbo].[fnMONTO_PLAZO_PRESTAMO]( 
                            {params['monto_solicitado']}
                            ,{params['plazo_solicitado']});
                
                SELECT @VAL AS VAL;
                
                """
    return SP_EXECUTE(storedProc)


def sp_trx503(request):
    # print(request.POST)
    params = {}
    cod_usuario = request.user.cod_usuario
    params["nro_solicitud"] = TEXTO(request.POST["solicitud"])
    params["situacion_solicitud_id"] = request.POST["situacion_solicitud"]
    params["fecha"] = TEXTO(request.POST["fecha"])
    params["comentario"] = TEXTO(request.POST["comentario"])
    params["nro_acta"] = TEXTO(request.POST["nro_acta"])
    params["fec_acta"] = TEXTO(request.POST["fec_acta"])
    params["nro_resolucion"] = request.POST["nro_resolucion"]
    # params["nro_prestamo"] = request.POST["nro_prestamo"]
    # params["cant_desembolso"] = TEXTO(request.POST["cant_desembolso"])
    params["cant_desembolso"] = 1
    params["monto_aprobado"] = request.POST["monto_aprobado"]
    params["usu_actual"] = cod_usuario

    print(params)
    storedProc = f"""
                    DECLARE @RC INT
                    DECLARE @NRO_SOLICITUD CHAR(10)
                    DECLARE @SITUACION_SOLICITUD_ID INT
                    DECLARE @FECHA DATETIME
                    DECLARE @COMENTARIO VARCHAR(200)
                    DECLARE @NRO_ACTA VARCHAR(15)
                    DECLARE @FEC_ACTA VARCHAR(10)
                    DECLARE @NRO_RESOLUCION NUMERIC(8,0)
                    DECLARE @NRO_PRESTAMO NUMERIC(10,0)
                    DECLARE @CANT_DESEMBOLSO NUMERIC(5,0)
                    DECLARE @MONTO_APROBADO NUMERIC(14,2)
                    DECLARE @USU_ACTUAL INT
                    DECLARE @MENSAJE VARCHAR(300)

                    -- TODO: Establezca los valores de los parámetros aquí.
                    BEGIN TRAN

                    EXECUTE @RC = [dbo].[TRX_503] 
                    @NRO_SOLICITUD = {params['nro_solicitud']}
                    ,@SITUACION_SOLICITUD_ID = {params['situacion_solicitud_id']}
                    ,@FECHA  = {params['fecha']}
                    ,@COMENTARIO = {params['comentario']}
                    ,@NRO_ACTA= {params['nro_acta']}
                    ,@FEC_ACTA= {params['fec_acta']}
                    ,@NRO_RESOLUCION= {params['nro_resolucion']}
                    ,@NRO_PRESTAMO=@NRO_PRESTAMO OUTPUT
                    ,@CANT_DESEMBOLSO= {params['cant_desembolso']}
                    ,@MONTO_APROBADO= {params['monto_aprobado']}
                    ,@USU_ACTUAL= {params['usu_actual']}
                    ,@MENSAJE=@MENSAJE OUTPUT

                    
                    IF @RC<>0 
                        ROLLBACK TRAN
                    ELSE
                        COMMIT TRAN 

                    SELECT @RC AS RTN, @MENSAJE AS MSG, @NRO_PRESTAMO AS VAL;
    """
    return SP_EXECUTE(storedProc)


def sp_trx504(request):
    # print(request.POST)
    params = {}
    cod_usuario = request.user.cod_usuario
    params["nro_solicitud"] = TEXTO(request.POST["solicitud"])
    params["fec_ult_desembolso"] = TEXTO(request.POST["fec_ult_desembolso"])
    params["fec_1er_vencimiento"] = TEXTO(request.POST["fec_1er_vencimiento"])
    params["cod_usuario"] = TEXTO(cod_usuario)
    print(params)
    storedProc = f"""
                    DECLARE @RC INT
                    DECLARE @NRO_SOLICITUD CHAR(10)
                    DECLARE @FEC_ULT_DESEMBOLSO DATETIME
                    DECLARE @FEC_1ER_VENCIMIENTO DATETIME
                    DECLARE @COD_USUARIO CHAR(4)
                    DECLARE @MENSAJE VARCHAR(200)

                    -- TODO: Establezca los valores de los parámetros aquí.
                    --BEGIN TRAN
                    EXECUTE @RC = [dbo].[TRX_504] 
                     @NRO_SOLICITUD = {params['nro_solicitud']}
                    ,@FEC_ULT_DESEMBOLSO ={params['fec_ult_desembolso']}
                    ,@FEC_1ER_VENCIMIENTO={params['fec_1er_vencimiento']}
                    ,@COD_USUARIO={params['cod_usuario']}
                    ,@MENSAJE = @MENSAJE OUTPUT

                    
                    IF @RC<>0 
                        ROLLBACK TRAN
                    ELSE
                        COMMIT TRAN 

                    SELECT @RC AS RTN, @MENSAJE AS MSG, @NRO_SOLICITUD AS VAL;
    """
    return SP_EXECUTE(storedProc)
