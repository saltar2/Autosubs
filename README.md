# Autosubs
## Secciones
[Requisitos de Software](#Requisitos-de-Software)  
[Claves APIs](#claves-de-api)  
[Example videos](#descarga-del-video-a-procesar)  
[Formatos soportados](#formatos-soportados)  
[Ejecucion docker](#despliegue-con-docker)  
[Idioma](#idioma-preferido-de-audio)  
[Postprocesado](#postprocesado-con-spacy)  
[Openai](#llm)


## Requisitos de Software

Para ejecutar Autosubs, necesitarás tener instalado lo siguiente en tu sistema:

- **Docker:** Debes poder lanzar, construir instancias con docker y tambien servicios con docker compose

## Claves de API

Autosubs requiere las siguientes claves API para su funcionamiento:

- **Deepgram:** Necesitarás una clave API de Deepgram para la transcripción de audio a texto. Puedes obtenerla de forma gratuita en [deepgram.com](https://www.deepgram.com/).
  
- **DeepL:** Si deseas traducir el texto transcrito a otro idioma, necesitarás una clave API de DeepL. Puedes obtenerla de forma gratuita en [deepl.com](https://www.deepl.com/).

- **Openai:** Se hara uso del modelo mas reciente gpt-4o ya que los modelos opensource no proporcionaban una respuesta satisfactoria o tienen requirimientos altos para su ejecucion en local. Ej llama3 7b y gemini. Para obtencion de esta clave se necesita añadir un credito minimo de 5 dolares para alcanzar el tier1 y desbloquear el modelo gpt-4o. 

Para configurar Autosubs, crea un archivo `.env` en el subdirectorio backend del proyecto con las siguientes variables `CHATGPT_API` ,`DEEPL_KEY` y `DEEPGRAM_KEY` y añade tus claves API correspondientes, sin comillas.

## Descarga del Video a Procesar

Antes de ejecutar Autosubs, asegúrate de descargar el video que deseas procesar. Puedes hacerlo ejecutando el siguiente comando:

    python3 -m pip install gdown && python3 download_drive.py


<a name='Formatos-soportados'></a>
## Formatos soportados
### Formatos de videos soportados

".mp4", ".avi", ".mkv", ".mov", ".m4v", ".mts", ".wmv", ".mpg", ".flv"

### Formatos de audio soportados

"aac", "mp3", "flac"

## Despliegue con Docker

Ejecutar Autosubs con docker, sigue estos pasos:

        docker compose up --build

Acceso a la web:

        http://localhost:5000


## Idioma preferido de audio

English

Ademas ahora al no indicar de forma explicita el idioma podria detectar cualquiera de los idiomas que soportan los modelos.
 https://developers.deepgram.com/docs/models-languages-overview   
Busca en Advanced functionality y veras como funciona la seleccion de idioma -> https://developers.deepgram.com/docs/language-detection   

## Postprocesado con spacy

Para verificar mofologia de palabras usa esta web: https://data.cervantesvirtual.com/analizador  

Se ha intendado probar el codigo desarrollado por el CiTIUS pero esta dando mejores resultados en el analisis con spacy y es mas facil de usar.
https://github.com/citiususc/linguakit?tab=readme-ov-file  
En concreto este es el comando util para mi caso -> ./Linguakit/linguakit dep  es file -fa 
Spacy es usado para reconocer los signos de puntuacion y Freeling para el reconocimiento morfologico de palabras -> https://nlp.lsi.upc.edu/freeling/

## LLM 

Se hace uso de la api de openai para por un lado detectar posibles errores en la transcripcion comparando 2 archivos SRT con la transcripcion de los modelos nova-2 y whisper-large , ambos hosted en deepgram. 
Por otro lado, si el usuario lo desea se puede dejar en manos del LLM la correccion de los errores identificados antes. El resultado puede no ser satisfactorio dado que falta contexto (ej: audio del video). En todo caso para ambos se devolvera un txt con los errores identificados. La correccion por LLM será opcional.

## Bugs



