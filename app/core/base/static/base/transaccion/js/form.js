// Espera a que el DOM esté completamente cargado
$(document).ready(function () {
  // Obtiene el elemento <select> que contiene las transacciones disponibles
  const transaccion = document.querySelector("#transaccion"); // selector del combo de transacciones

  // Define el comportamiento cuando el usuario selecciona una transacción
  transaccion.onchange = function () {
    // Extrae el código de la transacción seleccionada (ej. trx503)
    const codigoTrx = transaccion.value;

    // Obtiene el código del cliente desde el campo correspondiente
    // ⚠️ Asegurarse que el campo tenga el ID correcto en el HTML: #cod_cliente
    const codCliente = $("#cod_cliente").val();

    // Llama a la función institucional que carga dinámicamente el formulario hijo
    // Esta función debe insertar el HTML en #div_transaccion y cargar el JS asociado
    insertarFormularioTransaccion(codigoTrx, codCliente);
  };
});
