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
                    $.ajax({
                        url: 'ajax/addarticle/',
                        type: 'POST',
                        data: {
                            'codigo': codigo,
                            'csrfmiddlewaretoken': token
                        },
                        dataType: 'json',
                        success: function(data) {
                            if (data['exito'] == true) {
                                Swal.fire({
                                    title: 'Éxito en el guardado',
                                    text: "El ítem ha sido guardado en el carrito" +
                                        " con éxito. Puedes seguir comprando!",
                                    type: 'info',
                                    showCancelButton: false,
                                    confirmButtonText: 'Aceptar'
                                })
                            } else {
                                Swal.fire({
                                    title: 'Fracaso en el guardado',
                                    text: "El ítem no ha sido guardado en el carrito." +
                                        " Intente nuevamente.",
                                    type: 'warning',
                                    showCancelButton: false,
                                    confirmButtonText: 'Aceptar'
                                })
                            }
                        }
                    })
                }
            })
        }
    })
};

function EliminarItemCarrito(codigo) {
    Swal.fire({
        title: '¿Seguro que deseas eliminar el artículo?',
        text: "Podrás volver a ingresarlo al carrito cuando desees.",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        var token = $('input[name="csrfmiddlewaretoken"]').val();
        $.ajax({
            url: 'ajax/removearticle/',
            type: 'POST',
            data: {
                'codigo': codigo,
                'csrfmiddlewaretoken': token
            },
            dataType: 'json',
            success: function(data) {
                if (data['exito'] == true) {
                    Swal.fire('Eliminado con éxito');
                    setTimeout(function() {
                        window.location.reload(false);
                    }, 500);
                } else {
                    Swal.fire('Error al eliminar');
                }
            }
        })
    })

};

$('.ui.dropdown')
    .dropdown();

function Buscar() {
    $("#formulario").submit()
}