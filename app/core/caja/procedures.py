from core.base.procedures import SP_EXECUTE
from core.base.utils import TEXTO, YYYY_MM_DD


def sp_generar_codigo_movimiento(request):
    # Define variables
    params = {}
    params["cod_usuario"] = TEXTO(request.user.cod_usuario)

    # Prepare the stored procedure execution script and parameter values
    # print(params)
    storedProc = f"""   SET NOCOUNT ON;
                        DECLARE @RC int
                        DECLARE @COD_USUARIO char(4)
                        DECLARE @COD_MOVIMIENTO char(8)
                        DECLARE @MENSAJE varchar(200)

                        -- TODO: Establezca los valores de los parámetros aquí.

                        EXECUTE @RC = [dbo].[PA_GENERAR_CODIGO_MOVIMIENTO] 
                        @COD_USUARIO={params['cod_usuario']}
                        ,@COD_MOVIMIENTO=@COD_MOVIMIENTO OUTPUT
                        ,@MENSAJE=@MENSAJE OUTPUT;                                        

                        SELECT @RC AS RTN, @MENSAJE AS MSG, @COD_MOVIMIENTO AS VAL;
                    """
    return SP_EXECUTE(storedProc)


def sp_obt_nro_comprobante(request, *args, **kwargs):
    # Define variables
    params = {}
    params["nro_caja"] = TEXTO(request.user.caja.nro_caja)
    params["tip_comprobante"] = kwargs["tip_comprobante"]
    params["operacion"] = kwargs["operacion"]

    # Prepare the stored procedure execution script and parameter values
    # print(params)
    storedProc = f"""   SET NOCOUNT ON;
                        DECLARE @RC int
                        DECLARE @NRO_CAJA numeric(4,0)
                        DECLARE @TIP_COMPROBANTE varchar(6)
                        DECLARE @OPERACION char(1)
                        DECLARE @NRO_TIMBRADO numeric(10,0)
                        DECLARE @NRO_ACT_COMPROBANTE numeric(20,0)
                        DECLARE @MENSAJE varchar(200)
                        

                        -- TODO: Establezca los valores de los parámetros aquí.

                        EXECUTE @RC = [dbo].[PA_OBT_NRO_COMPROBANTE] 
                        @NRO_CAJA={params['nro_caja']}
                        ,@TIP_COMPROBANTE={params['tip_comprobante']}
                        ,@OPERACION={params['operacion']}
                        ,@NRO_TIMBRADO=@NRO_TIMBRADO OUTPUT
                        ,@NRO_ACT_COMPROBANTE=@NRO_ACT_COMPROBANTE OUTPUT
                        ,@MENSAJE=@MENSAJE OUTPUT;
                                        

                        --SELECT @RC AS RTN, @MENSAJE AS MSG, CAST(@NRO_TIMBRADO AS VARCHAR) +' / '+ CAST(@NRO_ACT_COMPROBANTE AS VARCHAR) AS VAL;
                        SELECT @RC AS RTN, @MENSAJE AS MSG, @NRO_ACT_COMPROBANTE AS VAL;
                    """

    return SP_EXECUTE(storedProc)


def sp_trx700(request, *args, **kwargs):
    # Define variables
    print(request.POST)
    params = {}
    params["fec_movimiento"] = TEXTO(request.POST["fec_movimiento"])
    params["cod_movimiento"] = TEXTO(request.POST["cod_movimiento"])
    params["cod_cliente"] = request.POST["cliente"]
    params["nro_documento"] = request.POST["nro_documento"]  # NRO_RECIBO
    params["aporte_ingreso"] = request.POST["aporte_ingreso"]
    params["aporte"] = request.POST["aporte"]
    params["solidaridad"] = request.POST["solidaridad"]
    params["gastos"] = request.POST["gastos"]

    # Prepare the stored procedure execution script and parameter values
    # print(params)
    storedProc = f"""   SET NOCOUNT ON;
                        DECLARE @RC int
                        DECLARE @COD_MOVIMIENTO CHAR(8)
                        DECLARE @FEC_MOVIMIENTO DATE
                        DECLARE @cod_cliente INT
                        DECLARE @NRO_DOCUMENTO NUMERIC(13,0)
                        DECLARE @APORTE_INGRESO NUMERIC(14,2)
                        DECLARE @APORTE NUMERIC(14,2)
                        DECLARE @SOLIDARIDAD NUMERIC(14,2)
                        DECLARE @FONDO_EDUCACION NUMERIC(14,2)
                        DECLARE @GASTOS_ADMINISTRATIVOS NUMERIC(14,2)
                        DECLARE @COD_MONEDA NUMERIC(4,0)
                        DECLARE @IMPORTE_CHEQUE NUMERIC(14,2)
                        DECLARE @MENSAJE VARCHAR(100)

                        -- TODO: Establezca los valores de los parámetros aquí.
                        BEGIN TRAN
                        EXECUTE @RC = [dbo].[PTRX_700] 
                        @COD_MOVIMIENTO={params['cod_movimiento']}
                        ,@FEC_MOVIMIENTO={params['fec_movimiento']}
                        ,@cod_cliente ={params['cod_cliente']}
                        ,@NRO_DOCUMENTO={params['nro_documento']}
                        ,@APORTE_INGRESO = {params['aporte_ingreso']}
                        ,@APORTE ={params['aporte']}
                        ,@SOLIDARIDAD = {params['solidaridad']}
                        ,@FONDO_EDUCACION=0
                        ,@GASTOS_ADMINISTRATIVOS={params['gastos']}
                        ,@COD_MONEDA=1
                        ,@IMPORTE_CHEQUE=0
                        ,@MENSAJE=@MENSAJE OUTPUT;

                        IF @RC<>0 
                        ROLLBACK TRAN
                        ELSE
                        COMMIT TRAN                        

                        SELECT @RC AS RTN, @MENSAJE AS MSG, @MENSAJE AS VAL;
                    """

    return SP_EXECUTE(storedProc)


def sp_fnCUOTA_OBLICACION_CUENTA(request, *args, **kwargs):
    # Define variables
    print(request.POST)
    params = {}
    params["fec_movimiento"] = TEXTO(request.POST["fec_movimiento"])
    params["tip_cuenta"] = TEXTO(args[0])

    # Prepare the stored procedure execution script and parameter values
    # print(params)
    storedProc = f"""   SET NOCOUNT ON;
                        DECLARE @RV NUMERIC(14) -- VALOR DE RETORNO
                        -- TODO: Establezca los valores de los parámetros aquí.

                        EXEC @RV = [dbo].[fnCUOTA_OBLIGACION_CUENTA]                  
                        {params['tip_cuenta']},
                        {params['fec_movimiento']}
                        ;
                        
                        SELECT 0 AS RTN, @RV AS MSG, @RV AS VAL;
                    """

    return SP_EXECUTE(storedProc)


def sp_trx701(request, *args, **kwargs):
    # Define variables
    print(request.POST)
    params = {}
    params["fec_movimiento"] = TEXTO(request.POST["fec_movimiento"])
    params["cod_movimiento"] = TEXTO(request.POST["cod_movimiento"])
    params["cod_cliente"] = request.POST["cliente"]
    params["nro_documento"] = request.POST["nro_documento"]  # NRO_RECIBO
    params["aporte_efectivo"] = request.POST["aporte_efectivo"]

    # Prepare the stored procedure execution script and parameter values
    # print(params)
    storedProc = f"""   SET NOCOUNT ON;
                        DECLARE @RC int
                        DECLARE @COD_MOVIMIENTO CHAR(8)
                        DECLARE @FEC_MOVIMIENTO DATE
                        DECLARE @cod_cliente INT
                        DECLARE @NRO_DOCUMENTO NUMERIC(13,0)                       
                        DECLARE @APORTE_EFECTIVO NUMERIC(14,2)                       
                        DECLARE @APORTE_CHEQUE NUMERIC(14,2)                       
                        DECLARE @COD_MONEDA NUMERIC(4,0)                     
                        DECLARE @MENSAJE VARCHAR(100)

                        -- TODO: Establezca los valores de los parámetros aquí.

                        EXECUTE @RC = [dbo].[PTRX_701] 
                         @COD_MOVIMIENTO={params['cod_movimiento']}
                        ,@FEC_MOVIMIENTO={params['fec_movimiento']}
                        ,@cod_cliente ={params['cod_cliente']}
                        ,@NRO_DOCUMENTO={params['nro_documento']}                     
                        ,@APORTE_EFECTIVO ={params['aporte_efectivo']}                      
                        ,@APORTE_CHEQUE =0
                        ,@COD_MONEDA=1
                        ,@MENSAJE=@MENSAJE OUTPUT;
                        

                        SELECT @RC AS RTN, @MENSAJE AS MSG, @MENSAJE AS VAL;
                    """

    return SP_EXECUTE(storedProc)


def sp_trx702(request, *args, **kwargs):
    # Define variables
    print(request.POST)
    params = {}
    params["fec_movimiento"] = TEXTO(request.POST["fec_movimiento"])
    params["cod_movimiento"] = TEXTO(request.POST["cod_movimiento"])
    params["cod_cliente"] = request.POST["cliente"]
    params["nro_documento"] = request.POST["nro_documento"]  # NRO_RECIBO
    params["solidaridad_efectivo"] = request.POST["solidaridad_efectivo"]

    # Prepare the stored procedure execution script and parameter values
    # print(params)
    storedProc = f"""   SET NOCOUNT ON;
                        DECLARE @RC int
                        DECLARE @COD_MOVIMIENTO CHAR(8)
                        DECLARE @FEC_MOVIMIENTO DATE
                        DECLARE @cod_cliente INT
                        DECLARE @NRO_DOCUMENTO NUMERIC(13,0)                       
                        DECLARE @APORTE_EFECTIVO NUMERIC(14,2)                       
                        DECLARE @APORTE_CHEQUE NUMERIC(14,2)                       
                        DECLARE @COD_MONEDA NUMERIC(4,0)                     
                        DECLARE @MENSAJE VARCHAR(100)

                        -- TODO: Establezca los valores de los parámetros aquí.

                        EXECUTE @RC = [dbo].[PTRX_702] 
                        @COD_MOVIMIENTO={params['cod_movimiento']}
                        ,@FEC_MOVIMIENTO={params['fec_movimiento']}
                        ,@cod_cliente ={params['cod_cliente']}
                        ,@NRO_DOCUMENTO={params['nro_documento']}                     
                        ,@SOLIDARIDAD_EFECTIVO ={params['solidaridad_efectivo']}                      
                        ,@SOLIDARIDAD_CHEQUE =0
                        ,@COD_MONEDA=1
                        ,@MENSAJE=@MENSAJE OUTPUT;
                        

                        SELECT @RC AS RTN, @MENSAJE AS MSG, @MENSAJE AS VAL;
                    """

    return SP_EXECUTE(storedProc)


def sp_PTRX_GRABAR_CAJA(request, *args, **kwargs):
    # Define variables
    print(request.POST)
    params = {}
    params["cod_movimiento"] = TEXTO(request.POST["cod_movimiento"])

    # Prepare the stored procedure execution script and parameter values
    # print(params)
    storedProc = f"""   
                        DECLARE @RC int
                        DECLARE @COD_MOVIMIENTO char(8)
                        DECLARE @MENSAJE varchar(200)

                        -- TODO: Establezca los valores de los parámetros aquí.
                        BEGIN TRAN
                        EXECUTE @RC = [dbo].[PTRX_GRABAR_CAJA] 
                        @COD_MOVIMIENTO ={params['cod_movimiento']}
                        ,@MENSAJE=@MENSAJE OUTPUT

                        IF @RC <> 0 
                            ROLLBACK TRAN
                        ELSE
                            COMMIT TRAN 

                        SELECT @RC AS RTN, @MENSAJE AS MSG, @MENSAJE AS VAL;
                    """

    return SP_EXECUTE(storedProc)


# PRINT RECIBO
def sp_rptcaj012(request, **kwargs):
    # Define variables
    try:
        params = {}
        params["fec_movimiento"] = TEXTO(kwargs["fec_movimiento"]).replace("-", "/")
        params["cod_movimiento"] = TEXTO(kwargs["cod_movimiento"])
        params["cod_cliente"] = kwargs["cod_cliente"]
        params["cod_usuario"] = TEXTO(kwargs["cod_usuario"])
        # Prepare the stored procedure execution script and parameter values
        storedProc = f"""   DECLARE @RC int
                            DECLARE @COD_CLIENTE numeric(7,0)
                            DECLARE @COD_MOVIMIENTO char(8)
                            DECLARE @FEC_MOVIMIENTO char(10)
                            DECLARE @COD_USUARIO char(4)
                            DECLARE @TIP_COMPROBANTE char(3)
                            
                            -- TODO: Establezca los valores de los parámetros aquí.

                            EXECUTE @RC = [dbo].[RPT_CAJ012] 
                            @COD_CLIENTE = {params['cod_cliente']}
                            ,@COD_MOVIMIENTO = {params['cod_movimiento']}
                            ,@FEC_MOVIMIENTO ={params["fec_movimiento"]}
                            ,@COD_USUARIO ={params["cod_usuario"]}
                            ,@TIP_COMPROBANTE = 'RCB';

                            --SELECT @RC;
                        
                        """

        return SP_EXECUTE(storedProc, all=True)
    except Exception as e:
        print(e)
