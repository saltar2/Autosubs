var scrollTimeout;
var autoScrollEnabled = true;
var languagesLoaded = false;
var eventSource= null;
//var eventCondition = false;

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
    if (eventSource == null){
        eventSource = new EventSource('/event'); // Ruta del endpoint SSE en tu servidor Flask
    }
    
    eventSource.onopen = function() {
        console.log('Conexión SSE establecida');
        //var messageBox = document.getElementById('messages');
        //messageBox.innerHTML = '';
    };
    eventSource.onerror = function(event) {
        console.error('Error en la conexión SSE', event);
        eventSource.close();
        //receiveSSE()
    };
    eventSource.addEventListener("message", function(event) {
        console.log('Evento SSE recibido del servidor:', event.data);
        if(event.data != 'start'){
            updateProgress();
            // Actualiza el contenido del cuadro de mensajes en la interfaz web
            var messageBox = document.getElementById('messages');
            messageBox.innerHTML += event.data + '<br>';
            if (autoScrollEnabled) {
                scrollToBottom();
        }
        }
        
    });
}
function load_languages(){
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
            alert('Error con servidor backend. Imposible obtener lenguajes disponibles.');
        }
    });
}
// Cuando se envía el formulario
$('#uploadForm').submit(function(event) {
    event.preventDefault();
    updateProgressBar(0)
    // Desactivar el botón de submit
    $('#submitButton').prop('disabled', true);

    var formData = new FormData($(this)[0]);
    $('#progressBar').removeClass('is-hidden');
    $('#progressText').removeClass('is-hidden');

    var messageBox = document.getElementById('messages');
    messageBox.innerHTML = '';
    if (eventSource == null){
        receiveSSE();
    }
    
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
            
            //eventSource.close()
            //console.log('Conexión SSE cerrada');
            if (autoScrollEnabled) {
                scrollToBottom();
            }
        },
        error: function(xhr, status, error) {
            // Mostrar un mensaje de error al usuario
            alert(xhr.responseText);
            // Desactivar el botón de submit
            $('#submitButton').prop('disabled', false);
        }
    });
    //if (!eventCondition){
        
    //    eventCondition=true
    //}
     
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
    if ($('#languageSelect option').length > 1) {// si recargas la pagina las variables se restablecen
        // Si ya están cargados, no se hace nada
        languagesLoaded = true;
    }else{
        load_languages();
        receiveSSE();
    }
    
    
    // Evento para detectar cuando se selecciona un idioma por primera vez
    $('#languageSelect').on('click', function() {
        // Verificar si los idiomas ya se han cargado
        // Comprobar si los idiomas ya están cargados
        if ($('#languageSelect option').length > 1) {// si recargas la pagina las variables se restablecen
            // Si ya están cargados, no se hace nada
            languagesLoaded = true;
        }
        if (!languagesLoaded /*&& $('#languageSelect option').length ==0*/) {
            // Realizar la llamada a la API del backend para obtener los idiomas
            load_languages();
        }
        

    });

});

