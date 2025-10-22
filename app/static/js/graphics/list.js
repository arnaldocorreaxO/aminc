function get_list(args) {
  var solicitud_prestamo = {
    list: function () {
      $("#data").DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        info: false,
        ordering: false,
        // processing: true,
        // serverSide: true,
        paging: false,
        // ordering: true,
        searching: false,
        // stateSave: true,      Salva la seleccion de longitud de pagina lengthMenu
        // lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
        // pagingType: "full_numbers",
        // pageLength: 10,
        ajax: {
          url: pathname,
          type: "POST",
          data: {
            // 'producto': args[7],
            sucursal: args[5],
            fecha: args[2],
            action: "list",
          },
          dataSrc: "",
          headers: {
            "X-CSRFToken": csrftoken,
          },
        },
        order: [[0, "asc"]],
        columns: [
          { data: "fec_solicitud" },
          { data: "cliente" },
          { data: "tipo_prestamo" },
          { data: "monto_solicitado" },
          { data: "estado" },
        ],
        columnDefs: [
          {
            targets: [0, -2],
            class: "text-center",
            render: function (data, type, row) {
              return data;
            },
          },
          {
            targets: [-1],
            class: "text-center",
            render: function (data, type, row) {
              switch (data.toUpperCase()) {
                case "PENDIENTE":
                  badge_class = "warning";
                  break;
                case "APROBADO":
                  badge_class = "success";
                  break;
                case "RECHAZADO":
                  badge_class = "danger";
                  break;
                default:
                  badge_class = "light";
                  break;
              }
              badge = `<span class="badge badge-${badge_class}">  ${data} </span>`;
              return badge;
            },
          },
        ],
        initComplete: function (settings, json) {},
      });
    },
  };

  // <span class="badge badge-success">Success</span>

  $(function () {
    $(document).ready(function () {
      solicitud_prestamo.list();
    });
  });
}
