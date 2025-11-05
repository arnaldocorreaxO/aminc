let trxUrl = ""; // variable global para almacenar la URL real

function insertarFormularioTransaccion(codigoTrx, codCliente) {
  $.ajax({
    url: "/base/api/transaccion/info/",
    type: "GET",
    data: { codigo: codigoTrx },
    success: function (trx) {
      if (trx.requiere_cliente && !codCliente) {
        message_info("Debe seleccionar un socio antes de continuar.");
        return;
      }

      trxUrl = trx.url; // guardar la URL real para usarla al procesar

      $.ajax({
        url: trx.url,
        type: "POST",
        data: {
          action: "load_form",
          cod_cliente: codCliente,
          csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),
        },
        beforeSend: function () {
          $("#div_transaccion").html(""); // limpia el contenedor
        },
        success: function (response) {
          if (!response.hasOwnProperty("error")) {
            $("#div_transaccion").html(response.html_form);

            // Carga el script específico de la transacción desde /static/
            if (trx.script) {
              const script = document.createElement("script");
              script.type = "text/javascript";

              // Si el script ya incluye /static/, no lo duplicamos
              const basePath = trx.script.startsWith("/static/")
                ? trx.script
                : `/static/${trx.script}`;

              script.src = `${basePath}?v=${new Date().getTime()}`; // versión para evitar caché
              script.async = true;
              document.body.appendChild(script);
            }

            // Opcional: actualizar atributos del formulario principal si es necesario
            $("#frmTransaccion").attr("action", trx.url);
            return false;
          }
          message_error(response.error);
        },
        error: function () {
          message_error("Error al cargar el formulario de transacción.");
        },
      });
    },
    error: function () {
      message_error("No se pudo obtener la información de la transacción.");
    },
  });
}
