function downloadSubtitles() {
    var downloadUrl = $('#downloadLink').attr('href');
    window.location.href = downloadUrl;
}

$(document).ready(function() {
    // Define una variable global para almacenar el número total de archivos
    var totalFiles = 0;

    // Define una variable global para mantener el número de archivos cargados
    var uploadedCount = 0;
    // Función para actualizar la barra de progreso y el número del porcentaje
    function updateProgressBar(percentComplete) {
        var progress = $('.progressbar .progress');
        var counter = $('.counter');

        // Actualiza el texto del contador y el ancho de la barra de progreso
        counter.text(Math.round(percentComplete) + '%');
        progress.css('width', percentComplete + '%');
    }

    // Ocultar la barra de progreso y el número del porcentaje al cargar la página
    $('.progressbar-container').hide();
    $('.counter').hide();

    // Cuando se envía el formulario
    $('#uploadForm').submit(function(event) {
        event.preventDefault();
        var formData = new FormData($(this)[0]);
        var progressContainer = $('.progressbar-container'); // Seleccione el contenedor de la barra de progreso animada

        // Muestra la barra de progreso y el número del porcentaje
        progressContainer.show();
        $('.counter').show();

        $.ajax({
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                // Configura la función de progreso
                xhr.upload.addEventListener('progress', function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = evt.loaded / evt.total * 100;
                        updateProgressBar(percentComplete); // Llama a la función para actualizar la barra de progreso animada
                    }
                }, false);
                return xhr;
            },
            type: 'POST',
            url: '/upload',
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            success: function(response) {
                // Oculta la barra de progreso y el número del porcentaje cuando la carga está completa
                progressContainer.hide();
                $('.counter').hide();

                // Muestra el botón de descarga del ZIP
                $('#downloadLink').removeClass('is-hidden').attr('href', response);
            },
            error: function(xhr, status, error) {
                // Maneja errores aquí
            }
        });
    });
});
