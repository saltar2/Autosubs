function downloadSubtitles() {
    var downloadUrl = $('#downloadLink').attr('href');
    window.location.href = downloadUrl;
}
// Función para actualizar la barra de progreso y el texto
function updateProgressBar(percentComplete) {
    var progressBar = $('#progressBar');
    var progressText = $('#progressText');

    // Actualiza el valor de la barra de progreso y el texto
    progressBar.val(percentComplete);
    progressText.text(percentComplete + '%');
}
function updateProgress() {
    $.ajax({
        type: 'GET',
        url: '/progress',  // Ruta en el servidor para obtener el progreso
        success: function(response) {
            if (response && response.progress !== undefined) {
                // Actualizar la barra de progreso en el frontend
                //console.log('Progreso recibido:', response.progress);
                updateProgressBar(response.progress);
                if (response.progress < 100) {
                    // Si el progreso no ha alcanzado el 100%, sigue comprobando
                    setTimeout(updateProgress, 2500);  // Revisa cada segundo
                } else {
                    // Cuando el progreso alcanza el 100%, oculta la barra de progreso
                    $('#progressBar').addClass('is-hidden');
                    $('#progressText').addClass('is-hidden');
                }
            }
        },
        error: function(xhr, status, error) {
            // Manejo de errores
        }
    });
}
// Cuando se envía el formulario
$('#uploadForm').submit(function(event) {
    event.preventDefault();

    // Desactivar el botón de submit
    $('#submitButton').prop('disabled', true);

    var formData = new FormData($(this)[0]);
    $('#progressBar').removeClass('is-hidden');
    $('#progressText').removeClass('is-hidden');

    $.ajax({
        type: 'POST',
        url: '/upload',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        /*xhrFields: {
            // Agregar esta opción para permitir eventos progresivos desde el servidor
            onprogress: function(e) {
                if (e.lengthComputable) {
                    // Calcular el porcentaje completo
                    var percentComplete = (e.loaded / e.total) * 100;
                    // Actualizar la barra de progreso y el texto
                    updateProgressBar(percentComplete);
                }
            }
        },*/
        
        success: function(response) {
            // Ocultar la información de progreso de todos los archivos
            
            $('#progressBar').addClass('is-hidden');
            $('#progressText').addClass('is-hidden');
            $('.counter').hide();

            // Mostrar el botón de descarga del ZIP
            $('#h2_name').removeClass('is-hidden');
            $('#downloadLink').removeClass('is-hidden').attr('href', response);
            // activar el botón de submit
            $('#submitButton').prop('disabled', false);
            // Detener la llamada a la función updateProgress
            clearTimeout(updateProgressTimeout);
            
            
        },
        error: function(xhr, status, error) {
            // Mostrar un mensaje de error al usuario
            alert('Ha ocurrido un error al subir los archivos. Inténtalo de nuevo más tarde.');
            // Desactivar el botón de submit
            $('#submitButton').prop('disabled', false);
        }
    });
    /*function callUpdateProgress() {
        updateProgress();
        setTimeout(callUpdateProgress, 1000); // Llama a esta función cada 200 milisegundos
    }
    callUpdateProgress();*/
    var updateProgressTimeout = setTimeout(updateProgress, 2500);
});


