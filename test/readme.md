# Audio Transcription and Testing Repository

## Descripción

Este repositorio proporciona las referencias, hipótesis, audios y scripts utilizados para el testing. Es posible que necesites modificar algunos scripts para que funcionen en tu PC debido a que se usan rutas locales.

Para probar la aplicación, se han desactivado las funciones de formateo, traducción, detección y/o mejora con GPT-4o.

## Proceso de Extracción de Datasets

Se han extraído datasets de audios públicos en cuatro idiomas seleccionados sin ningún criterio en particular. Los idiomas son inglés, italiano, ruso y japonés. Se eligieron datasets que contienen aproximadamente la misma cantidad de minutos de audio con transcripciones validadas:

- **Inglés**: Common Voice Delta Segment 17.0
- **Italiano**: Common Voice Delta Segment 15.0
- **Japonés**: Common Voice Corpus 4
- **Ruso**: Common Voice Delta Segment 10.0

### Minutos de Audio por Idioma

- **Inglés**: 172.9 minutos
- **Italiano**: 106.99 minutos
- **Japonés**: 183.1 minutos
- **Ruso**: 93.38 minutos

## Preprocesamiento de Datos

### Eliminación de Audios No Validados

Se deben eliminar todos los audios que no estén en el archivo `validate.tsv`. Esto se realiza utilizando el script `remove_clips.py`.

### Generación de Duraciones de Clips

Dependiendo de la versión de los datasets, pueden venir con un archivo llamado `clip_durations.tsv` que contiene las duraciones de los clips. Si el dataset no proporciona esta información, se incluye un script `generate_clips_duration.py` para generarla.

### Cálculo de la Duración Total de los Audios

Se proporciona un script `durations.py` para calcular la duración total de los audios seleccionados.

## Optimización del Procesamiento de Audio

Para mejorar el rendimiento de la aplicación, se combinan todos los clips de audio en un único archivo, añadiendo un silencio de 1.25 segundos entre cada clip. Esto reduce significativamente el overhead causado por procesar múltiples archivos cortos.

### Justificación

Procesar cada clip de audio individualmente resultaba ineficiente debido a la corta duración de los clips (2-10 segundos), lo que generaba un overhead considerable cada vez que se cambiaba de audio. En promedio, procesar un minuto de audio tomaba 2 minutos debido a este overhead.

### Solución

La solución fue combinar todos los audios en un único archivo, añadiendo silencios de 1.25 segundos entre cada clip. Aunque esto incrementó la duración total del archivo, el beneficio en términos de rendimiento fue significativo. Por ejemplo, para el idioma ruso, los 93.38 minutos de audio tardaron aproximadamente 180 minutos en procesarse individualmente, pero combinados en un único archivo, el tiempo de procesamiento se redujo a 22.33 minutos. Esto incluye los 1567.5 segundos (26.125 minutos) adicionales de silencio añadido entre los 1254 clips.

### Ejemplo de Resultados

- **Ruso**: 93.38 minutos procesados en 22.33 minutos (comparado con 180 minutos antes de la optimización).

Combinar los audios en un solo archivo, incluso con la adición de silencios, demuestra ser una estrategia efectiva para mejorar el rendimiento general de la aplicación.


### Tiempos de Procesamiento

- **Ruso**: 22.33 minutos 
- **Italiano**: 24.28 minutos
- **Japonés**: 43.41 minutos
- **Inglés**: 20.5 minutos

## Generación de Transcripciones

Una vez obtenidas las transcripciones, se convierten en archivos `.nlp` utilizando el script `nlp_converter.py`. Se generan dos archivos: uno con las transcripciones de referencia (`[input]`) y otro con las transcripciones hipótesis (`[output]`).

## Cálculo del WER

Para calcular el Word Error Rate (WER), se utiliza la herramienta [fstalign](https://github.com/revdotcom/fstalign). Sigue este [tutorial](https://www.rev.com/blog/resources/how-to-test-speech-recognition-engine-asr-accuracy-and-word-error-rate) para configurar y usar la herramienta.

### Comando para Ejecutar FSTAlign

```sh
docker run -v E:\FSTAlign\speech-datasets\earnings21\output\:/fstalign/outputs -v E:\FSTAlign\speech-datasets\earnings21\transcripts\:/fstalign/references --name fstaling -it revdotcom/fstalign
./build/fstalign wer --ref references/mi/en/input_en.nlp --hyp outputs/mi/en/output_en.nlp
```

### Resultados de WER

- **Inglés**: 8.5%
- **Italiano**: 10.53%
- **Ruso**: 13.64%
- **Japonés**: 56.13%

*Nota*: El WER para japonés es notoriamente más alto, probablemente debido a un problema con el modelo de transcripción.

## Mejora de las Métricas

Para mejorar estas métricas, se puede realizar un fine-tuning del modelo.

## Modelo Usado

- **Modelo para las transcripciones de hipótesis**: Deepgram Nova-2



