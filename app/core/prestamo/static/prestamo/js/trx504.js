$(document).ready(function () {
  console.log("trx504.js!");

  const $procesar = $("#procesar");
  const $selectSolicitud = $('select[name="solicitud"]');
  const $fecUltDesembolso = $("#fec_ult_desembolso");
  const $fecPrimerVencimiento = $("#fec_1er_vencimiento");

  // Inicializa campos de fecha
  inicializarCampoFecha("#fec_ult_desembolso");
  inicializarCampoFecha("#fec_1er_vencimiento");

  // Maneja el cambio de solicitud
  $selectSolicitud.on("change", function () {
    const solicitudId = $(this).val();
    console.log("Solicitud seleccionada:", solicitudId);

    $.ajax({
      url: "/prestamo/trx504/",
      type: "POST",
      dataType: "json",
      data: {
        action: "search",
        solicitud_prestamo: solicitudId,
      },
      success: function (response) {
        $fecUltDesembolso.val("");
        $fecPrimerVencimiento.val("");

        if (!response.hasOwnProperty("error")) {
          console.log("Respuesta:", response);
          $fecUltDesembolso.val(response.fec_desembolso || "");
          $fecPrimerVencimiento.val(response.fec_1er_vencimiento || "");
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
