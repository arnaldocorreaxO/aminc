var persona = {
    list: function () {
        $('#data').DataTable({
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
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
            pagingType: "full_numbers",
            pageLength: 10,
            ajax: {
                url: pathname,
                type: 'POST',
                data: {
                    'action': 'search'
                },
                // dataSrc: "",
                headers: {
                    'X-CSRFToken': csrftoken
                },
            },
            order: [[0, 'asc']],
            columns: [
                { "data": "id" },
                { "data": "ci" },
                { "data": "nombre" },
                { "data": "apellido" },
                { "data": "edad" },
                { "data": "celular" },
                { "data": "id" },
            ],
            columnDefs: [
                {
                    targets: [1],
                    class: 'text-left',
                    orderable: true,
                    render: function (data, type, row) {
                        return formatoNumero(data)
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var buttons = '<a href="' + pathname + '/update/' + row.id + '/" class="btn btn-warning btn btn-xs btn-flat" data-toggle="tooltip" title="Editar"><i class="fas fa-edit"></i></a> ';
                        buttons += '<a href="' + pathname + '/delete/' + row.id + '/" type="button" class="btn btn-xs btn-danger btn btn-flat" data-toggle="tooltip" title="Eliminar"><i class="fas fa-trash-alt"></i></a>';
                        return buttons;
                    }
                },
            ],
            initComplete: function (settings, json) {

            }
        });
    }
};

$(function () {
    $(document).ready(function () {
        persona.list(false);
    });
});
