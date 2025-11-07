function formatearCampoMoneda(selector, decimales = 0) {
  const $campo = $(selector);

  $campo.on("input", function () {
    let valorOriginal = $(this).val();
    console.log("Campo moneda input original:", valorOriginal);

    // Elimina todo excepto dígitos y coma como separador decimal
    // let limpio = valorOriginal.replace(/[^\d,]/g, "");
    // 🔹 Limpia puntos de millar antes de procesar
    let limpio = valorOriginal.replace(/\./g, "").replace(/[^\d,]/g, "");

    // Divide en parte entera y decimal
    const partes = limpio.split(",");
    const entero = partes[0] || "";
    const decimal = partes[1] || "";

    // Formatea parte entera con separador de miles
    const enteroFormateado = entero.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

    // Reconstruye el valor
    const resultado =
      decimales > 0 && decimal.length > 0
        ? `${enteroFormateado},${decimal.slice(0, decimales)}`
        : enteroFormateado;

    $(this).val(resultado);
    console.log("Campo moneda input:", resultado);
  });

  // 🔍 Asegura que el evento se asocie al formulario hijo
  $(document).on("submit", "#frmTransaccionHijo", function () {
    let limpio = $campo.val().replace(/\./g, "").replace(",", ".").trim();
    console.log("Campo moneda submit limpio:", limpio);
    if (decimales === 0) {
      limpio = limpio.split(".")[0];
    }

    $campo.val(limpio);
  });
}

function inicializarCampoFecha(selector) {
  const $campo = $(selector);
  const valorInicial = $campo.val().trim();

  // Configuración base del datetimepicker
  const opciones = {
    format: "DD/MM/YYYY", // formato día/mes/año
    locale: "es", // idioma español
    useCurrent: false, // evita preselección automática
    viewMode: "days", // vista principal en días
    showTodayButton: true,
    showClear: true,
    showClose: true,
    icons: {
      time: "far fa-clock",
      date: "far fa-calendar",
      up: "fas fa-chevron-up",
      down: "fas fa-chevron-down",
      previous: "fas fa-chevron-left",
      next: "fas fa-chevron-right",
      today: "far fa-calendar-check",
      clear: "far fa-trash-alt",
      close: "fas fa-times",
    },
  };
  // Establece la fecha inicial si existe
  if (valorInicial) {
    opciones.date = valorInicial;
  }
  // Inicializa el datetimepicker
  $campo.datetimepicker(opciones);
}

/**
 * 🔁 Función institucional para procesar formularios transaccionales vía AJAX.
 *
 * - Asocia el botón de procesamiento con el envío del formulario hijo.
 * - Limpia campos monetarios según el atributo data-decimales.
 * - Valida el formulario con jQuery Validate.
 * - Envía los datos con submit_formdata_with_ajax().
 *
 * Parámetros:
 *   $botonProcesar → botón que dispara el procesamiento
 *   opciones → {
 *     formSelector: selector del formulario hijo (por defecto: #frmTransaccionHijo)
 *     url: URL de procesamiento (por defecto: trxUrl global)
 *     titulo: título del modal de confirmación
 *     mensaje: mensaje de confirmación
 *     callback: función a ejecutar luego del submit exitoso
 *   }
 */

function procesarTransaccionAjax($botonProcesar, opciones = {}) {
  const {
    $form = $("#frmTransaccionHijo"), // 🔹 formulario explícito o por defecto
    url = trxUrl,
    titulo = "Notificación",
    mensaje = "¿Procesar Transacción?",
    callback = null,
  } = opciones;

  $botonProcesar.on("click", function () {
    if ($form.length === 0) {
      alert("No se encontró el formulario de detalle.");
      return false;
    }

    // 🔹 Limpieza de campos monetarios
    $form.find("input[data-decimales]").each(function () {
      const decimales = parseInt($(this).data("decimales")) || 0;
      let limpio = $(this).val().replace(/\./g, "").replace(",", ".").trim();
      if (decimales === 0) {
        limpio = limpio.split(".")[0];
      }
      $(this).val(limpio);
    });

    const validator = $form.validate({ lang: "es" });
    if (!validator.form()) return false;

    if (!url) {
      alert("No se ha definido la URL de procesamiento.");
      return false;
    }

    const parameters = new FormData($form[0]);
    console.log("Procesando TRX:", url);

    submit_formdata_with_ajax(
      titulo,
      mensaje,
      url,
      parameters,
      function (data) {
        if (!data.hasOwnProperty("error")) {
          console.log(data.val);
          if (data.rtn !== 0) {
            message_warning(data.msg);
          } else {
            message_success_to_url(data.msg, ".");
          }
          if (typeof callback === "function") callback(data);
        }
      }
    );

    return false;
  });
}
