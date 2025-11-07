function abrirModalTransaccion(codigoTrx, codCliente) {
  $.ajax({
    url: "/base/api/transaccion/info/",
    type: "GET",
    data: { codigo: codigoTrx },
    success: function (trx) {
      if (trx.requiere_cliente && !codCliente) {
        message_info("Debe seleccionar un socio antes de continuar.");
        return;
      }

      // trxUrl es una variable global definida en form.js
      trxUrl = trx.url; // guardar la URL real para usarla al procesar

      $.ajax({
        url: trx.url,
        type: "POST",
        data: {
          action: "load_form",
          cod_cliente: codCliente,
          csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),
        },
        success: function (response) {
          $("#modal-transaccion .modal-content").html(response.html_form);
          $("#modal-transaccion").modal("show");

          // Carga el script específico de la transacción
          const script = document.createElement("script");
          script.src = trx.script + "?" + new Date().getTime();
          script.async = true;
          document.body.appendChild(script);
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
