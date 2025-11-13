var tblData;
var input_daterange;
var columns = [];

movimiento = {
  list: function (all) {
    /*Cuando el objecto select es multiple retorna un array []
        Si utilizamos select_cliente.val()            retorna la variable cliente[]=[''] Ej. cadena vacía
        Si utilizamos select_cliente.val().join(", ") retorna la variable cliente  =[''] Ej. cadena vacía      
        */

    var parameters = {
      action: "search",
      start_date: input_daterange
        .data("daterangepicker")
        .startDate.format("YYYY-MM-DD"),
      end_date: input_daterange
        .data("daterangepicker")
        .endDate.format("YYYY-MM-DD"),
      transporte: select_transporte.val().join(", "),
      cliente: select_cliente.val().join(", "),
      destino: select_destino.val().join(", "),
      producto: select_producto.val().join(", "),
      chofer: select_chofer.val().join(", "),
      vehiculo: select_vehiculo.val().join(", "),
    };

    if (all) {
      parameters["start_date"] = "";
      parameters["end_date"] = "";
      parameters["cliente"] = "";
      parameters["producto"] = "";
      parameters["chofer"] = "";
      parameters["vehiculo"] = "";
    }

    tblData = $("#data").DataTable({
      responsive: true,
      autoWidth: false,
      destroy: true,
      deferRender: true,
      processing: true,
      serverSide: true,
      paging: true,
      ordering: true,
      searching: true,
      // stateSave: true,      Salva la seleccion de longitud de pagina lengthMenu
      lengthMenu: [
        [10, 25, 50, 100, -1],
        [10, 25, 50, 100, "Todos"],
      ],
      pagingType: "full_numbers",
      pageLength: 10,
      ajax: {
        url: pathname,
        type: "POST",
        data: parameters,
        //Sin este da error de length
        // dataSrc: ""
      },
      order: [[0, "desc"]],
      dom: "Blfrtip",
      buttons: [
        {
          extend: "excelHtml5",
          text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
          titleAttr: "Excel",
          className: "btn btn-success btn-flat btn-xs",
        },
        {
          extend: "pdfHtml5",
          text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
          titleAttr: "PDF",
          className: "btn btn-danger btn-flat btn-xs",
          download: "open",
          orientation: "landscape",
          pageSize: "A4",
          customize: function (doc) {
            doc.styles = {
              header: {
                fontSize: 18,
                bold: true,
                alignment: "center",
              },
              subheader: {
                fontSize: 13,
                bold: true,
              },
              quote: {
                italics: true,
              },
              small: {
                fontSize: 8,
              },
              tableHeader: {
                bold: true,
                fontSize: 11,
                color: "white",
                fillColor: "#2d4154",
                alignment: "center",
              },
            };
            doc.content[1].table.widths = columns;
            doc.content[1].margin = [0, 35, 0, 0];
            doc.content[1].layout = {};
            doc["footer"] = function (page, pages) {
              return {
                columns: [
                  {
                    alignment: "left",
                    text: ["Fecha de creación: ", { text: current_date }],
                  },
                  {
                    alignment: "right",
                    text: [
                      "página ",
                      { text: page.toString() },
                      " de ",
                      { text: pages.toString() },
                    ],
                  },
                ],
                margin: 20,
              };
            };
          },
        },
      ],
      columns: [
        { data: "id" },
        { data: "nro_ticket" },
        { data: "fec_entrada" },
        { data: "cliente_destino" },
        { data: "transporte_vehiculo" },
        { data: "chofer" },
        { data: "producto" },
        { data: "tiempo_descarga" },
        { data: "peso_entrada" },
        { data: "peso_salida" },
        { data: "peso_neto" },
        { data: "id" },
      ],
      columnDefs: [
        {
          targets: [-2, -3, -4],
          class: "text-right",
          orderable: false,
          render: function (data, type, row) {
            return data;
          },
        },
        {
          targets: [-1],
          class: "text-center",
          orderable: false,
          render: function (data, type, row) {
            var buttons = "";
            if (row.peso_salida == 0) {
              buttons +=
                '<a href="/bascula/movimiento/update/' +
                row.id +
                '/" id="btnSalida" class="btn btn-warning btn-flat" data-toggle="tooltip" title="Salida Báscula">SALIDA <i class="fas fa-truck"></i></a>';
            } else {
              btnClass = "btn btn-secondary btn-flat disabled_print";
              if (!row.fec_impresion) {
                btnClass = "btn btn-dark btn-flat";
              }
              // alert(btnClass)
              buttons +=
                '<a href="/bascula/movimiento/print/' +
                row.id +
                '/" id="btnPrint" target="_blank"  class="' +
                btnClass +
                '" data-toggle="tooltip" title="Imprimir Ticket Báscula"><i class="fas fa-print"></i></a>';
            }
            if ($('input[name="usu_change_movimiento"]').val() == "SI") {
              buttons +=
                '<a href="' +
                pathname +
                "/update/" +
                row.id +
                '/" class="btn btn-warning btn-flat mt-1 "><i class="fas fa-edit"></i></a> ';
            }

            return buttons;
          },
        },
      ],
      initComplete: function (settings, json) {},
    });
    //ESTO EVITA UN ERROR AL INTENTAR DESCARGAR CON EL BUTTON PDF
    $.each(tblData.settings()[0].aoColumns, function (key, value) {
      columns.push(value.sWidthOrig);
    });
  },
};

$(function () {
  current_date = new moment().format("YYYY-MM-DD");

  select_transporte = $('select[name="transporte"]');
  select_cliente = $('select[name="cliente"]');
  select_destino = $('select[name="destino"]');
  select_producto = $('select[name="producto"]');
  select_chofer = $('select[name="chofer"]');
  select_vehiculo = $('select[name="vehiculo"]');

  input_daterange = $('input[name="date_range"]');

  input_daterange
    .daterangepicker({
      language: "auto",
      startDate: new Date(),
      locale: {
        format: "YYYY-MM-DD",
      },
    })
    .on("apply.daterangepicker", function (ev, picker) {
      // getData('filter');
      movimiento.list(false);
    });

  $(".btnFilter").on("click", function () {
    movimiento.list(false);
  });

  $(".btnSearchAll").on("click", function () {
    // getData(true);
    movimiento.list(true);
  });

  /////////////////////////////
  //   EVENTO PRINT TICKET   //
  /////////////////////////////

  $("#data tbody").on("click", "#btnPrint", function (e) {
    e.preventDefault();
    var parameters = {
      // Indicamos con esta variable que estamos imprimiendo por primera vez el ticket
      print_ticket: true,
    };
    var url = $(this).attr("href");
    $.ajax({
      url: url,
      data: parameters,
      method: "GET",
      // dataType: 'json',
      // processData: false,
      // contentType: false,
      success: function (request) {
        console.log(request);
        if (!request.hasOwnProperty("info")) {
          //En esta llamada sin parametros se va a actualizar el estado de la impresion
          window.open(url, "_blank").focus();
          return false;
        }
        message_warning(request.info);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        message_error(errorThrown + " " + textStatus);
      },
    });
  });

  /////////////////////////////
  //   EVENTO TIPO SALIDA   //
  /////////////////////////////

  $("#data tbody").on("click", "#btnSalida", function (e) {
    e.preventDefault();
    var url = $(this).attr("href");
    var parameters = {
      tipo_salida: true,
    };

    Swal.fire({
      title: "Seleccione el Tipo de Salida",
      showDenyButton: true,
      showCancelButton: true,
      confirmButtonText: `Camión Lleno`,
      denyButtonText: `Camión Vacío`,
      cancelButtonText: `Cancelar`,
    }).then((result) => {
      /* Read more about isConfirmed, isDenied below */
      if (result.isConfirmed) {
        //   Swal.fire('Saliendo Camion Lleno', '', 'success')
        parameters["tipo_salida"] = true;
        location.href = url + "lleno";
      } else if (result.isDenied) {
        //   Swal.fire('Saliendo Camion Vacio', '', 'info')
        parameters["tipo_salida"] = false;
        location.href = url + "vacio";
      }
    });
  });

  $(document).ready(function () {
    movimiento.list(false);
  });
});
