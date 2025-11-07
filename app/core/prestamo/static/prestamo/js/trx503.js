$(document).ready(function () {
  console.log("trx503.js!");

  const $procesar = $("#procesar");
  const $selectSolicitud = $('select[name="solicitud"]');
  const $montoAprobado = $("#monto_aprobado");

  // Inicializar
  inicializarCampoFecha("#fecha");
  inicializarCampoFecha("#fec_acta");
  formatearCampoMoneda("#monto_aprobado");

  // Maneja el cambio de solicitud
  $selectSolicitud.on("change", function () {
    const solicitudId = $(this).val();
    console.log("Solicitud seleccionada:", solicitudId);

    $.ajax({
      url: "/prestamo/trx503/",
      type: "POST",
      dataType: "json",
      data: {
        action: "search",
        solicitud_prestamo: solicitudId,
      },
      success: function (response) {
        $montoAprobado.val("");

        if (!response.hasOwnProperty("error")) {
          console.log("Respuesta:", response);
          $montoAprobado.val(response.monto_solicitado || "");
        } else {
          message_error(response.error);
        }
      },
      error: function () {
        message_error("Error al consultar la solicitud.");
      },
    });
  });

  // Procesa el formulario hijo vía AJAX
  procesarTransaccionAjax($procesar);
});
