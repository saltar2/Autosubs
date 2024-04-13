var scrollTimeout;
var autoScrollEnabled = true;
var languagesLoaded = false;

function scrollToBottom() {
    var messageBox = document.getElementById('messages');
    messageBox.scrollTop = messageBox.scrollHeight;
}

function handleScroll() {
    clearTimeout(scrollTimeout);
    autoScrollEnabled = false;
    // Después de 2 segundos de inactividad en el scroll, reactiva el desplazamiento automático
    scrollTimeout = setTimeout(function() {
        autoScrollEnabled = true;
    }, 10000);
}

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
                updateProgressBar(response.progress);
                if (response.progress < 100) {

                } else {
                    // Cuando el progreso alcanza el 100%, oculta la barra de progreso
                    $('#progressBar').addClass('is-hidden');
                    $('#progressText').addClass('is-hidden');
                    updateProgressBar(0)
                }
            }
        },
        error: function(xhr, status, error) {
            // Manejo de errores
        }
    });
}
function toggleMessageBox() {
    var checkbox = $('#showMessagesCheckbox');
    var messageBox = $('#messageBox');
    if (checkbox.prop('checked')) {
        messageBox.removeClass('is-hidden');
    } else {
        messageBox.addClass('is-hidden');
    }
}

function receiveSSE() {
    var eventSource = new EventSource('/event'); // Ruta del endpoint SSE en tu servidor Flask
    eventSource.onopen = function() {
        console.log('Conexión SSE establecida');
        //var messageBox = document.getElementById('messages');
        //messageBox.innerHTML = '';
    };
    eventSource.onerror = function(event) {
        console.error('Error en la conexión SSE', event);
        eventSource.close();
    };
    eventSource.addEventListener('message', function(event) {
        console.log('Evento SSE recibido del servidor:', event.data);
        updateProgress();
        // Actualiza el contenido del cuadro de mensajes en la interfaz web
        var messageBox = document.getElementById('messages');
        messageBox.innerHTML += event.data + '<br>';
        if (autoScrollEnabled) {
            scrollToBottom();
        }
    });
    return eventSource;
}
// Cuando se envía el formulario
$('#uploadForm').submit(function(event) {
    event.preventDefault();

    // Desactivar el botón de submit
    $('#submitButton').prop('disabled', true);

    var formData = new FormData($(this)[0]);
    $('#progressBar').removeClass('is-hidden');
    $('#progressText').removeClass('is-hidden');

    var messageBox = document.getElementById('messages');
    messageBox.innerHTML = '';
    
    
    $.ajax({
        type: 'POST',
        url: '/upload',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        
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
            
            eventSource.close()
            console.log('Conexión SSE cerrada');
        },
        error: function(xhr, status, error) {
            // Mostrar un mensaje de error al usuario
            alert('Ha ocurrido un error al subir los archivos. Inténtalo de nuevo más tarde.');
            // Desactivar el botón de submit
            $('#submitButton').prop('disabled', false);
        }
    });
    var eventSource=receiveSSE();
    document.getElementById('messages').addEventListener('scroll', handleScroll);
});

//cargar idiomas si no se han cargado con la pagina
// Esperar a que el documento esté completamente cargado
$(document).ready(function() {
    // Variable para verificar si los idiomas ya se han cargado
    
    $('#showMessagesCheckbox').on('click', function() {
        // Llamar a la función para mostrar u ocultar el cuadro de mensajes
        toggleMessageBox();
    });
    
    // Evento para detectar cuando se selecciona un idioma por primera vez
    $('#languageSelect').on('click', function() {
        // Verificar si los idiomas ya se han cargado
        if (!languagesLoaded) {
            // Realizar la llamada a la API del backend para obtener los idiomas
            $.ajax({
                type: 'GET',
                url: '/language_codes', // Ruta en el servidor para obtener los códigos de idioma
                success: function(response) {
                    // Agregar los códigos de idioma al selector
                    for (var language in response) {
                        $('#languageSelect').append($('<option>', {
                            value: response[language][0],
                            text: language
                        }));
                    }
                    // Indicar que los idiomas se han cargado
                    languagesLoaded = true;
                },
                error: function(xhr, status, error) {
                    // Manejar errores si la solicitud falla
                    console.error('Error al obtener los códigos de idioma:', error);
                    // Mostrar un mensaje de error al usuario, por ejemplo:
                    alert('Ocurrió un error al obtener los códigos de idioma del servidor.');
                }
            });
        }
    });

});

