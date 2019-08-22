function confirmarCierreSesion() {
    Swal.fire({
        title: '¿Seguro que deseas cerrar sesión?',
        text: "Tus ítem guardados en el carrito de compras no se perderán.",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Cerrar sesión',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.value) {
            location.href = "/logout/"
        }
    })
};

function Consultar(codigo) {
    var token = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url: 'ajax/getarticle/',
        type: 'POST',
        data: {
            'codigo': codigo,
            'csrfmiddlewaretoken': token
        },
        dataType: 'json',
        success: function(data) {
            Swal.fire({
                title: data.nombre,
                html: '<img class="ui centered circular small image" src="' + data.image + '"><br/>' +
                    '<strong>Nombre: </strong>' + data.nombre + '<br/>' +
                    '<strong>Descripción: </strong>' + data.descripcion + '<br/>' +
                    '<strong>Precio: </strong>' + data.precio,
                showConfirmButton: true,
                confirmButtonText: 'Añadir al Carrito',
                showCancelButton: true,
                cancelButtonText: 'Salir'
            }).then((result) => {
                if (result.value) {
                    Swal.fire('AÑADIDO POLIEDRO!!!');
                }
            })
        }
    })
};