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
        beforeSend: function () {
          $("#div_transaccion").html(""); // limpia el contenedor
        },
        success: function (response) {
          if (!response.hasOwnProperty("error")) {
            $("#div_transaccion").html(response.html_form);
            cargarScriptsTransaccion(trx); // carga los scripts necesarios
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

function cargarScriptsTransaccion(trx) {
  const scripts = [];

  // Siempre cargar el utilitario común
  scripts.push("/static/js/formulario_utils.js");

  // Agregar el script específico de la transacción si existe
  // El script debe estar en formato relativo a /static/
  // Ejemplo: 'prestamo/js/trx501.js'
  if (trx.script) {
    const basePath = trx.script.startsWith("/static/")
      ? trx.script
      : `/static/${trx.script}`;
    scripts.push(basePath);
  }

  // Cargar todos los scripts con control de caché y sin duplicar
  scripts.forEach((src) => {
    if (!document.querySelector(`script[src^="${src}"]`)) {
      const script = document.createElement("script");
      script.type = "text/javascript";
      script.src = `${src}?v=${new Date().getTime()}`;
      script.async = true;
      document.body.appendChild(script);
    }
  });
}
