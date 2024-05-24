var scrollTimeout;
var autoScrollEnabled = true;
var languagesLoaded = false;
var eventSource= null;
var isDarkMode = false;
var num_batches=0;
var actual_batch=0;
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
                var actual_batch_percent=(response.progress/100)*(1/num_batches);
                var total_batch_percent=actual_batch_percent+((actual_batch-1)/num_batches);
                updateProgressBar((total_batch_percent*100).toFixed(2));

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
        //console.log('Evento SSE recibido del servidor:', event.data);
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
function toggleBackground() {
    var body = $('body');
    var textElements = $('body, h1, h2, h3, h4, h5, h6, p, label, input, select, option');
    var sse_mesages = $('#messages');
    var detailedInfoBox = $('#messageBox');
    var uploadForm = $('#uploadForm');
    var fileinput= $('#fileInput');
    var langselect=$('#languageSelect');
    var footer= $('footer');
    var nav=$('navbar');

    if (isDarkMode) {
        // Cambiar a modo claro
        body.css('background-color', '#fff');
        textElements.css('color', '#333');
        sse_mesages.css('color', '#333');
        detailedInfoBox.css('background-color', '#fff'); // Cambiar el color de fondo de "informacion detallada"
        uploadForm.css('background-color', '#fff'); // Cambiar el color de fondo del formulario de carga
        fileinput.css('background-color', '#fff');
        langselect.css('background-color', '#fff');
        footer.css('background-color', '#fff');
        nav.css('background-color', '#d5cbec');
        isDarkMode = false;
    } else {
        // Cambiar a modo oscuro
        body.css('background-color', '#333');
        textElements.css('color', '#fff');
        sse_mesages.css('color', '#fff');
        detailedInfoBox.css('background-color', '#333'); // Cambiar el color de fondo de "informacion detallada"
        uploadForm.css('background-color', '#333'); // Cambiar el color de fondo del formulario de carga
        fileinput.css('background-color', '#333');
        langselect.css('background-color', '#333');
        footer.css('background-color', '#333');
        nav.css('background-color', '#00d1b2');
        isDarkMode = true;
    }
}
function sendBatchRequest(batches,batch_index,language,llmOption){
    if(batch_index<num_batches){
        var formData= new FormData()
        for(let file of batches[batch_index]){
            formData.append('file',file)
        }
        actual_batch=batch_index+1;
        console.log("batch: ",actual_batch," total: ",num_batches)
        
        //formData.append('file',batches[i])
        formData.append('language',language)
        formData.append('llm_option',llmOption)
        formData.append('batch_number',actual_batch)
        formData.append('total_batches',num_batches)
        
        
        

        $.ajax({
            type: 'POST',
            url: '/upload',
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            
            success: function(response) {
                // Ocultar la información de progreso de todos los archivos
                if( (batch_index+1)== num_batches){
                    $('#progressBar').addClass('is-hidden');
                    $('#progressText').addClass('is-hidden');
        
                    updateProgressBar(0);
                    $('.counter').hide();
                    $("#progressText_time_final").removeClass("is-hidden"); // Mostrar el elemento
                    $("#totalTime").text(response.total_time.toFixed(2)); // Actualizar el tiempo total
        
                    // Mostrar el botón de descarga del ZIP
                    $('#h2_name').removeClass('is-hidden');
                    $('#downloadLink').removeClass('is-hidden').attr('href', response.zip_url);
                    // activar el botón de submit
                    $('#submitButton').prop('disabled', false);
                    // Detener la llamada a la función updateProgress
                    
                    //eventSource.close()
                    //console.log('Conexión SSE cerrada');
                    if (autoScrollEnabled) {
                        scrollToBottom();
                    }
                }else {
                    sendBatchRequest(batches,batch_index+1,language,llmOption)
                }
                
            },
            error: function(xhr, status, error) {
                // Mostrar un mensaje de error al usuario
                alert(xhr.responseText);
                // Desactivar el botón de submit
                $('#submitButton').prop('disabled', false);
            }
        });
    }
    
}
// Cuando se envía el formulario
$('#uploadForm').submit(function(event) {
    event.preventDefault();
    updateProgressBar(0)
    // Desactivar el botón de submit
    $('#submitButton').prop('disabled', true);

    //var formData = new FormData($(this)[0]);
    $('#progressBar').removeClass('is-hidden');
    $('#progressText').removeClass('is-hidden');
    $("#progressText_time_final").addClass('is-hidden');
    $('#h2_name').addClass('is-hidden');
    $('#downloadLink').addClass('is-hidden');

    var files = $('#fileInput')[0].files;
    var language = $('#languageSelect').val();
    var llmOption = $('#llm_option').is(':checked') ? 'yes' : 'no';
    var batchSize = 100; // Define el tamaño de cada lote
    var batches = [];
    var totalFiles = files.length;
    
    var totalBatches = Math.ceil(totalFiles / batchSize);

    for (let i = 0; i < totalFiles; i += batchSize) {
        batches.push([...files].slice(i, i + batchSize));
    }
    num_batches=totalBatches;

    var messageBox = document.getElementById('messages');
    messageBox.innerHTML = '';
    document.getElementById('messages').addEventListener('scroll', handleScroll);

    if (eventSource == null){
        receiveSSE();
    }

    sendBatchRequest(batches,0,language,llmOption)     
    
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
    $('#toggleBackgroundButton').click(function() {
        toggleBackground();
    });

});

