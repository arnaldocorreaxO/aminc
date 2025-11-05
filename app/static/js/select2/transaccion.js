// Inicializa el selector de transacciones con Select2 y búsqueda dinámica vía AJAX
$(function () {
  // Referencias a los campos relevantes del formulario
  const $transaccion = $('select[name="transaccion"]'); // combo de transacciones
  const $modulo = $('input[name="modulo"]'); // módulo actual (ej. prestamo, caja)
  const $tipoAcceso = $('input[name="tipo_acceso"]'); // tipo de acceso (ej. diario, cierre)

  // Configura el combo con Select2 y tema Bootstrap 4
  $transaccion.select2({
    theme: "bootstrap4", // estilo visual
    language: "es", // idioma español
    // placeholder: "Filtrar por Transacción", // opcional
    // minimumInputLength: 1,                 // opcional para activar búsqueda con mínimo de caracteres

    // Configuración AJAX para cargar transacciones desde el backend
    ajax: {
      url: "/base/transaccion/add/", // endpoint que responde con transacciones válidas
      type: "POST", // método POST para enviar parámetros
      delay: 250, // retardo para evitar múltiples llamadas rápidas

      // Cabecera de seguridad CSRF para Django
      headers: {
        "X-CSRFToken": csrftoken,
      },

      // Parámetros enviados al backend
      data: function (params) {
        return {
          term: isNULL(params.term, ""), // término de búsqueda ingresado
          action: "search_trx_url", // acción esperada por la vista
          modulo: isNULL($modulo.val(), ""), // módulo actual
          tipo_acceso: isNULL($tipoAcceso.val(), ""), // tipo de acceso
        };
      },

      // Procesa los resultados recibidos y los adapta al formato Select2
      processResults: function (data) {
        return {
          results: data, // debe ser un array de objetos con id y text
        };
      },
    },
  });
});
