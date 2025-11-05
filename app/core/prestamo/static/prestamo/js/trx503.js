$(document).ready(function () {
  console.log("trx503.js!");

  const $procesar = $("#procesar");

  // Inicializa los datetimepickers
  $('input[name="fecha"], input[name="fec_acta"]').each(function () {
    $(this).datetimepicker({
      format: "DD/MM/YYYY", // formato día/mes/año
      locale: "es", // idioma español
    });
  });

  // Función para obtener el formulario hijo insertado dinámicamente
  function getFormularioDetalle() {
    return $("#div_transaccion").find("#frmTransaccionHijo").first(); // asume que el form hijo está dentro del div
  }

  // Función para validar y enviar el formulario hijo
  function saveFormAjax() {
    const $form = getFormularioDetalle();

    if ($form.length === 0) {
      alert("No se encontró el formulario de detalle.");
      return false;
    }

    const validator = $form.validate({ lang: "es" });

    if (validator.form()) {
      const parameters = new FormData($form[0]);

      if (!trxUrl) {
        alert("No se ha definido la URL de procesamiento.");
        return false;
      }

      console.log("Procesando TRX:", trxUrl);

      submit_formdata_with_ajax(
        "Notificación",
        "¿Procesar Transacción?",
        trxUrl,
        parameters,
        function (data) {
          if (!data.hasOwnProperty("error")) {
            console.log(data.val);
            if (data.rtn !== 0) {
              message_warning(data.msg);
            } else {
              message_success_to_url(data.msg, ".");
            }
          }
        }
      );
    }

    return false;
  }

  // Asocia el evento al botón procesar
  $procesar.on("click", saveFormAjax);
});
