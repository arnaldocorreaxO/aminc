var fv;
var input_fec_solicitud;
var input_fec_desembolso;
var input_fec_1er_vencimiento;

document.addEventListener("DOMContentLoaded", function (e) {
  const form = document.getElementById("frmForm");
  fv = FormValidation.formValidation(form, {
    locale: "es_ES",
    localization: FormValidation.locales.es_ES,
    plugins: {
      trigger: new FormValidation.plugins.Trigger(),
      submitButton: new FormValidation.plugins.SubmitButton(),
      bootstrap: new FormValidation.plugins.Bootstrap(),
      icon: new FormValidation.plugins.Icon({
        valid: "fa fa-check",
        invalid: "fa fa-times",
        validating: "fa fa-refresh",
      }),
    },
    fields: {
      sucursal: {
        validators: {
          notEmpty: {
            message: "Sucursal es obligatorio",
          },
        },
      },
      cliente: {
        validators: {
          notEmpty: {
            message: "Cliente es obligatorio",
          },
          remote: {
            url: pathname,
            data: function () {
              return {
                obj: form.querySelector('[name="cliente"]').value,
                type: "cliente",
                action: "validate_data",
              };
            },
            message: "El Cliente ya posee una solicitud de prestamo",
            method: "POST",
          },
        },
      },
      fec_solicitud: {
        validators: {
          notEmpty: {
            message: "La fecha es obligatoria",
          },
          date: {
            format: "DD/MM/YYYY",
            message: "La fecha no es válida",
          },
          callback: {
            message: "La fecha de solicitud es mayor a la fecha de desembolso",
            callback: function (input) {
              return validarFechaSolicitudDesembolso(form);
            },
          },
        },
      },
      fec_desembolso: {
        validators: {
          notEmpty: {
            message: "La fecha es obligatoria",
          },
          date: {
            format: "DD/MM/YYYY",
            message: "La fecha no es válida",
          },
          callback: {
            message: "La fecha de desembolso es menor a la fecha de solicitud",
            callback: function (input) {
              return validarFechaSolicitudDesembolso(form);
            },
          },
        },
      },
      fec_1er_vencimiento: {
        validators: {
          notEmpty: {
            message: "La fecha es obligatoria",
          },
          date: {
            format: "DD/MM/YYYY",
            message: "La fecha no es válida",
          },
          callback: {
            message:
              "La fecha de vencimiento es menor a la fecha de desembolso",
            callback: function (input) {
              return validarFechaPrimerVtoDesembolso(form);
            },
          },
        },
      },
    },
  })
    .on("core.element.validated", function (e) {
      if (e.valid) {
        const groupEle = FormValidation.utils.closest(e.element, ".form-group");
        if (groupEle) {
          FormValidation.utils.classSet(groupEle, {
            "has-success": false,
          });
        }
        FormValidation.utils.classSet(e.element, {
          "is-valid": false,
        });
      }
      const iconPlugin = fv.getPlugin("icon");
      const iconElement =
        iconPlugin && iconPlugin.icons.has(e.element)
          ? iconPlugin.icons.get(e.element)
          : null;
      iconElement && (iconElement.style.display = "none");
    })
    .on("core.validator.validated", function (e) {
      if (!e.result.valid) {
        const messages = [].slice.call(
          form.querySelectorAll(
            '[data-field="' + e.field + '"][data-validator]'
          )
        );
        messages.forEach((messageEle) => {
          const validator = messageEle.getAttribute("data-validator");
          messageEle.style.display =
            validator === e.validator ? "block" : "none";
        });
      }
    })
    .on("core.form.valid", function () {
      // submit_formdata_with_ajax_form(fv);
      var form = fv.form;
      var parameters = new FormData($(form)[0]);
      submit_formdata_with_ajax(
        "Notificación",
        "¿Está seguro que desea realizar la siguiente operación?",
        window.location.pathname,
        parameters,
        function (data) {
          if (!data.hasOwnProperty("error")) {
            console.log(data.val);
            if (data.rtn != 0) {
              message_warning(data.msg);
              return false;
            } else {
              message_success_to_url(data.msg, form.getAttribute("data-url"));
            }
            return false;
          } else {
            message_error(data.error);
          }
        }
      );
    });
});

$(function () {
  select_cliente = $('select[name="cliente"]');
  select_cliente.on("change", function () {
    fv.revalidateField("cliente");
  });

  input_fec_solicitud = $('input[name="fec_solicitud"]');
  input_fec_solicitud.datetimepicker({
    format: "DD/MM/YYYY",
    locale: "es",
    keepOpen: false,
    date: input_fec_solicitud.val(),
  });

  input_fec_solicitud.on("change.datetimepicker", function () {
    fv.revalidateField("fec_solicitud");
    fv.revalidateField("fec_desembolso");
    fv.revalidateField("fec_1er_vencimiento");
  });

  input_fec_desembolso = $('input[name="fec_desembolso"]');
  input_fec_desembolso.datetimepicker({
    format: "DD/MM/YYYY",
    locale: "es",
    keepOpen: false,
    date: input_fec_desembolso.val(),
  });

  input_fec_desembolso.on("change.datetimepicker", function () {
    fv.revalidateField("fec_solicitud");
    fv.revalidateField("fec_desembolso");
    fv.revalidateField("fec_1er_vencimiento");
  });

  input_fec_1er_vencimiento = $('input[name="fec_1er_vencimiento"]');
  input_fec_1er_vencimiento.datetimepicker({
    format: "DD/MM/YYYY",
    locale: "es",
    keepOpen: false,
    date: input_fec_1er_vencimiento.val(),
  });

  input_fec_1er_vencimiento.on("change.datetimepicker", function () {
    fv.revalidateField("fec_solicitud");
    fv.revalidateField("fec_desembolso");
    fv.revalidateField("fec_1er_vencimiento");
  });

  // GENERAR PROFORMA CUOTAS
  $("#btnGenerarProforma").on("click", function () {
    tblSearchProducts = $("#tblProformaCuota").DataTable({
      responsive: true,
      autoWidth: false,
      destroy: true,
      ajax: {
        url: pathname,
        type: "POST",
        data: {
          action: "search_proforma_cuota",
          sucursal: $("#id_sucursal").val(),
          nro_solicitud: $("#id_nro_solicitud").val(),
          fec_solicitud: $("#fec_solicitud").val(),
          fec_desembolso: $("#fec_desembolso").val(),
          fec_1er_vencimiento: $("#fec_1er_vencimiento").val(),
          plazo_meses: $("#id_plazo_meses").val(),
          moneda: $("#id_moneda").val(),
          tasa_interes: $("#id_tasa_interes").val(),
          cant_cuota: $("#id_cant_cuota").val(),
          total_interes: $("#id_total_interes").val(),
          // 'usu_actual': $('#id_usu_actual').val(),
          monto_solicitado: $("#id_monto_solicitado").val(),
          monto_prestamo: $("#id_monto_prestamo").val(),
          monto_cuota_inicial: $("#id_monto_cuota_inicial").val(),
          monto_refinanciado: $("#id_monto_refinanciado").val(),
          monto_neto: $("#id_monto_neto").val(),
        },
        dataSrc: "",
      },
      columns: [
        { data: "nro_cuota" },
        { data: "fec_vencimiento" },
        { data: "saldo_anterior_capital" },
        { data: "amortizacion" },
        { data: "interes" },
        { data: "comision" },
        { data: "monto_cuota" },
        // { data: "id" },
      ],
      columnDefs: [
        {
          targets: [-1, -2, -3, -4, -5],
          class: "text-center",
          render: function (data, type, row) {
            return formatoNumero(data);
          },
        },
      ],
      rowCallback: function (row, data, index) {},
      fnHeaderCallback: function (nHead, aData, iStart, iEnd, aiDisplay) {
        // Esta función se llama en cada evento de 'dibujar' y le permite modificar dinámicamente
        // la fila del encabezado.Esto se puede usar para calcular y mostrar información útil sobre la tabla.
        const data = aData[0];
        console.log(data);
        if (data !== undefined) {
          console.log(formatoNumero(data.total_interes));

          $("#id_monto_prestamo").val(parseFloat(data.monto_prestamo));
          $("#id_monto_refinanciado").val(parseFloat(data.monto_refinanciado));
          $("#id_monto_neto").val(parseFloat(data.monto_neto));
          $("#id_total_interes").val(parseFloat(data.total_interes));
          $("#id_monto_cuota_inicial").val(parseFloat(data.monto_cuota));
        }
      },
    });
    $("#myModalProformaCuota").modal("show");
  });
});

// VALIDACIONES
function validarFechaSolicitudDesembolso(form) {
  const f1 = form.querySelector('[name="fec_solicitud"]').value;
  const f2 = form.querySelector('[name="fec_desembolso"]').value;
  const dif = diasDiferencia(f1, f2);

  if (dif > 0) {
    return false;
  }
  return true;
}

function validarFechaPrimerVtoDesembolso(form) {
  const f1 = form.querySelector('[name="fec_1er_vencimiento"]').value;
  const f2 = form.querySelector('[name="fec_desembolso"]').value;
  const dif = diasDiferencia(f2, f1);

  if (dif > 0) {
    return false;
  }
  return true;
}
