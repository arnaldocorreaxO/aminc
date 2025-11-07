$(document).ready(function () {
  console.log("trx501.js!");
  const $procesar = $("#procesar");

  // Procesa el formulario hijo vía AJAX
  procesarTransaccionAjax($procesar);
});
