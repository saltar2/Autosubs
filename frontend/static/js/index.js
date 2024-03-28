function downloadSubtitles() {
    var downloadUrl = $('#downloadLink').attr('href');
    window.location.href = downloadUrl;
  }
  
  $(document).ready(function() {
    // Objeto para almacenar el progreso de cada archivo
    var fileUploadProgress = {};
  
    // Función para actualizar la barra de progreso de un archivo
    function updateProgressBar(fileName, percentComplete) {
      var progress = $(`.progress-bar[data-file-name="${fileName}"]`);
      var counter = $(`.counter[data-file-name="${fileName}"]`);
  
      // Actualiza el texto del contador y el ancho de la barra de progreso
      counter.text(Math.round(percentComplete) + '%');
      progress.css('width', percentComplete + '%');
    }
  
    // Ocultar la información de progreso al cargar la página
    $('.progress-container').hide();
    $('.counter').hide();
  
    // Crear una nueva instancia de EventSource para escuchar eventos SSE
    var eventSource = new EventSource('/upload');
  
    // Manejar eventos SSE recibidos del servidor
    eventSource.onmessage = function(event) {
      var data = JSON.parse(event.data);
      var fileName = data.fileName;
      var progress = parseInt(data.progress);
  
      // Actualizar la barra de progreso del archivo correspondiente
      updateProgressBar(fileName, progress);
  
      // Ocultar la información de progreso si la carga ha finalizado
      if (progress === 100) {
        $(`.progress-container[data-file-name="${fileName}"]`).hide();
      }
    };
  
    // Cerrar la conexión SSE cuando la página se cierre o se recargue
    $(window).on('beforeunload', function() {
      eventSource.close();
    });
  
    // Cuando se envía el formulario
    $('#uploadForm').submit(function(event) {
      event.preventDefault();
      var formData = new FormData($(this)[0]);
      var progressContainers = $('.progress-container'); // Seleccionar todos los contenedores de progreso
  
      // Mostrar la información de progreso de todos los archivos
      progressContainers.show();
      $('.counter').show();
  
      $.ajax({
        type: 'POST',
        url: '/upload',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function(response) {
          // Ocultar la información de progreso de todos los archivos
          progressContainers.hide();
          $('.counter').hide();
  
          // Mostrar el botón de descarga del ZIP
          $('#downloadLink').removeClass('is-hidden').attr('href', response);
        },
        error: function(xhr, status, error) {
          // Mostrar un mensaje de error al usuario
          alert('Ha ocurrido un error al subir los archivos. Inténtalo de nuevo más tarde.');
        }
      });
    });
  });