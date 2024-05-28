# Audio Transcription and Testing Repository
## Contenido del directorio test
Se incluyen los scripts usados para parsear y generar los archivos necesarios para su testeo y este readme con las explicaciones pertinentes.
Organizados por idiomas en la carpeta langs se incluyen los clips usados y el audio unido en el zip salida_{lan}.zip, los archivos de validated.tsv y clip_durations.tsv que contienen la información de las transcripciones y duraciones de los clips, el archivo salida_{lan}.es.srt que contiene la transcripción de todos los audios en conjunto, los archivos input_{lan}.nlp y output_{lan}.nlp que contienen las transcripciones de referencia e hipótesis.

## Proceso de Extracción de Datasets

Se han extraído datasets de audios públicos [Common Voice Mozilla](https://commonvoice.mozilla.org/en/datasets) en seis idiomas seleccionados sin ningún criterio en particular. Los idiomas son inglés, italiano, ruso, japonés, coreano y español. Se eligieron datasets que contienen aproximadamente la misma cantidad de minutos de audio con transcripciones validadas:

- **Inglés**: Common Voice Delta Segment 17.0
- **Italiano**: Common Voice Delta Segment 15.0
- **Japonés**: Common Voice Corpus 4
- **Ruso**: Common Voice Delta Segment 10.0
- **Coreano**: Common Voice Corpus 17.0
- **Español**: Common Voice Corpus 2

### Minutos de Audio por Idioma

- **Inglés**: 172.9 minutos
- **Italiano**: 106.99 minutos
- **Japonés**: 183.1 minutos
- **Ruso**: 93.38 minutos
- **Coreano**: 97.58 minutos
- **Español**: 119.8 minutos

## Preprocesamiento de Datos

### Eliminación de Audios No Validados

Se deben eliminar todos los audios que no estén en el archivo `validate.tsv`. Esto se realiza utilizando el script `remove_clips.py`.

### Generación de Duraciones de Clips

Dependiendo de la versión de los datasets, pueden venir con un archivo llamado `clip_durations.tsv` que contiene las duraciones de los clips. Si el dataset no proporciona esta información, se incluye un script `generate_clips_duration.py` para generarla.

### Cálculo de la Duración Total de los Audios

Se proporciona un script `durations.py` para calcular la duración total de los audios seleccionados.

### Reducción de Minutos de Audios

Para el caso concreto del español, los datasets proporcionados o eran muy extensos o muy reducidos, por lo que se eligió uno con una extensión superior pero luego se eliminaron audios hasta dejar solo 120 minutos de audios válidos. Para eso está el script `reduce_durations.py`, que genera 2 archivos: `validated_reduced.tsv` y `clip_durations_reduced.tsv`. Para terminar se volvería a ejecutar el archivo `script.py`, que engloba los otros 3 ejecutables mencionados en los apartados anteriores (`remove_clips.py`, `generate_clips_duration.py`, `durations.py`). Para no crear un script específico para este caso, simplemente se comentan y descomentan las líneas -> 10, 11 y 21, 22 en `remove_clips.py` y 9, 10 en `durations.py`.

## Optimización del Procesamiento de Audio

Para mejorar el rendimiento de la aplicación, se combinan todos los clips de audio en un único archivo, añadiendo un silencio de 1.25 segundos entre cada clip. Esto reduce significativamente el overhead causado por procesar múltiples archivos cortos.

### Justificación

Procesar cada clip de audio individualmente resultaba ineficiente debido a la corta duración de los clips (2-10 segundos), lo que generaba un overhead considerable cada vez que se cambiaba de audio. En promedio, procesar un minuto de audio tomaba 2 minutos debido a este overhead.

### Solución

La solución fue combinar todos los audios en un único archivo, añadiendo silencios de 1.25 segundos entre cada clip. Aunque esto incrementó la duración total del archivo, el beneficio en términos de rendimiento fue significativo. Por ejemplo, para el idioma ruso, los 93.38 minutos de audio tardaron aproximadamente 180 minutos en procesarse individualmente, pero combinados en un único archivo, el tiempo de procesamiento se redujo a 22.33 minutos. Esto incluye los 1567.5 segundos (26.125 minutos) adicionales de silencio añadido entre los 1254 clips.

El scrip usado para unir en un solo audio es `juntar_clips.py`

### Ejemplo de Resultados

- **Ruso**: 93.38 minutos procesados en 22.33 minutos (comparado con 180 minutos antes de la optimización).

Combinar los audios en un solo archivo, incluso con la adición de silencios, demuestra ser una estrategia efectiva para mejorar el rendimiento general de la aplicación. De esta forma se aprovecha el paralelismo en algunas funciones como transcribir o atenuar el ruido del audio.


### Tiempos de Procesamiento

- **Ruso**: 22.33 minutos 
- **Italiano**: 24.28 minutos
- **Japonés**: 43.41 minutos
- **Inglés**: 20.5 minutos
- **Coreano**: 10.9 minutos
- **Español**: 14.76 minutos

## Generación de Transcripciones

Una vez obtenidas las transcripciones, se convierten en archivos `.nlp` utilizando el script `nlp_converter.py`. Se generan dos archivos: uno con las transcripciones de referencia (`[input]`) y otro con las transcripciones hipótesis (`[output]`). Para el caso del español se debe modificar esta línea -> `text = parse_validate_tsv(os.path.join(base_route, language, 'validated.tsv'))` y modificar 'validated.tsv' por 'validated_reduced.tsv'.

## Cálculo del WER
¿Qué es WER? -> [WER](https://es.wikipedia.org/wiki/Word_Error_Rate)
Para calcular el Word Error Rate (WER), se utiliza la herramienta [fstalign](https://github.com/revdotcom/fstalign). Sigue este [tutorial](https://www.rev.com/blog/resources/how-to-test-speech-recognition-engine-asr-accuracy-and-word-error-rate) para configurar y usar la herramienta.

### Comando para Ejecutar FSTAlign

```sh
docker run -v E:\Autosubs\test\langs\:/fstalign/outputs -it revdotcom/fstalign

./build/fstalign wer --ref outputs/en/input_en.nlp --hyp outputs/en/output_en.nlp
./build/fstalign wer --ref outputs/it/input_it.nlp --hyp outputs/it/output_it.nlp
./build/fstalign wer --ref outputs/ru/input_ru.nlp --hyp outputs/ru/output_ru.nlp
./build/fstalign wer --ref outputs/ja/input_ja.nlp --hyp outputs/ja/output_ja.nlp
./build/fstalign wer --ref outputs/ko/input_ko.nlp --hyp outputs/ko/output_ko.nlp
./build/fstalign wer --ref outputs/es/input_es.nlp --hyp outputs/es/output_es.nlp

```

### Resultados de WER

- **Inglés**: 8,5%
- **Italiano**: 10,53%
- **Español**: 13,25%
- **Ruso**: 13,64%
- **Coreano**: 29,6%
- **Japonés**: 56,13%



*Nota*: El WER para japonés es notoriamente más alto, probablemente debido a un problema con el modelo de transcripción.

## Mejora de las Métricas

Para mejorar estas métricas, se puede realizar un fine-tuning del modelo.

## Modelo Usado

- **Modelo para las transcripciones de hipótesis**: Deepgram Nova-2



