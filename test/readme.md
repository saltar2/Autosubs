¡¡¡ EN EL REPOSITORIO SE PROBEE LAS REFERENCIAS, HIPOTESIS , AUDIOS Y SCRIPTS USADOS PARA EL TESTING, ES POSIBLE QUE HALLA QUE HACER ALGUNA MODIFICACION A LOS SCRIPTS PARA QUE FUNCIONEN EN TU PC DEBIDO A QUE USO RUTAS LOCALES.!!!


Para probar la aplicacion se han desactivado las funciones de formateo, traducción, detección y/o mejora con gpt-4o.
A continuacion se procedera a extraer datasets de audios publicos y en mi caso he elegido 4 idiomas sin ningun criterio en particular. https://commonvoice.mozilla.org/en/datasets . los idiomas son ingles, italiano, ruso y japones. se ha intentado elegir datasets que contengan aproximadamente los mismos minutos de audio con transcripciones validadas. 

Ingles -> Common Voice Delta Segment 17.0 
Italiano -> Common Voice Delta Segment 15.0
Japones -> Common Voice Corpus 4
Ruso -> Common Voice Delta Segment 10.0

una vez extraidos los idiomas en distintos directorios se veran unos archivos tsv con informacion de las trasncripciones. los unicos audios que nos interesan son los que esten el el archivo validate.tsv por ende se eliminara cualquier otro audio que no este en ese archivo (remove_clips.py). Lo que nos deja con :

Ingles -> 172,9 minutos
Italiano -> 106,99 minutos
Japones -> 183.1 minutos
Ruso -> 93,38 minutos

Dependiendo de la version de los datasets puede que vengan con un archivo llamado clip_durations.tsv. es algo que nos interesa ya que alverga las duraciones de los clips y por ello se incluye un script para generar dicha informacion si el dataset no la proporciona (generate_clips_duration.py). Por ultimo tambien se proporciona un script para ver la duracion total de los audios seleccionados (durations.py).

En pro de obtener un mejor rendimiento a la hora de sacar partido a las caracteristicas de la aplicacion que he desarrolado me he propuesto pasarle a la aplicacion un unico audio con todos los audios conbinados ,añadiendo un silencio de 1,25 segundos. La justificacion para esto es que si seleccionaba todos los clips y se los pasaba estos eran de duraciones tan cortas (2-10 segundos) que añadia un overhead a la aplicacion cada vez que cambiaba de audio dandonos un promedio de por cada minuto que duraba el audio se usaban 2 minutos para procesar dicho audio.

En cambio al juntar los audios en un unico archivo , incluso añadiendo silencios y aumentando su longitud en duracion, el beneficio obtenido es mucho mas que merecido. Por poner un caso concreto para el idioma ruso los 93,38 minutos tardaron aproximadamente 180 minutos, pero con un unico audio tardo 22,33 minutos. A pesar de que en el audio se ha añadido 1254*1,25 = 1567,5 segundos osea 26,125 minutos extras. La cifra de 1254 son la cantidad de audios despues de borrar todos los audios que no coincidian con los criterios ya explicados antes.

De igual forma para los demas idiomas los resultados fueron los siguientes:
Italiano -> 24,28 minutos
Japones -> 43,41 minutos
Ingles -> 20,5 minutos

Una vez obtenidas las trasncripciones lo siguiente que tenemos que hacer es meter dichas transcripciones en un archivo .nlp (nlp_converter.py) , se generaran un archivo con las transcripciones de referencia \[input\] y otro con las transcripciones hipotesis \[output\].

Para calcular el WER se hara uso de la herramienta fstalign -> https://github.com/revdotcom/fstalign  y siguiendo como referencia este tutorial https://www.rev.com/blog/resources/how-to-test-speech-recognition-engine-asr-accuracy-and-word-error-rate descargaremos la imagen docker, copiaremos los ficheros npl a un contenedor con la imagen de la herramienta corriendo o bien se pueden montar como volumenes. En mi caso , he usado este comando ya que tambien habia descargado los datos de testing que proporcionaban en el tutorial->  docker run -v E:\FSTAlign\speech-datasets\earnings21\output\:/fstalign/outputs -v E:\FSTAlign\speech-datasets\earnings21\transcripts\:/fstalign/references --name fstaling -it revdotcom/fstalign. Por ultimo ejecutamos la herramienta de una forma similar a esta -> ./build/fstalign wer --ref references/mi/en/input_en.nlp --hyp outputs/mi/en/output_en.nlp (dependiendo de donde montes o copies los ficheros). El comando anterior procesara ambos ficheros nlp y nos devolvera por consola el WER obtenido.


Los WER obtenidos para los idiomas seleccionados son:
Ingles -> 8,5%
Italiano -> 10,53%
Ruso -> 13,64%
Japones -> 56,13%

Aun no se porque en concreto el japones tiene un WER tan malo pero los textos estan normalizados, asique probablemente sea un problema del modelo.

Como se mejoran estas metricas? haciendole al modelo fine-turing.

MODELO USADO PARA LAS TRANSCRIPCIONES DE HIPOTESIS -> deepgram  nova-2
