import json

def encontrar_palabras_bajas_confianza(file, threshold_general,threshold_word):
    with open(file, "r") as json_file:
        data = json.load(json_file)
        palabras_bajas_confianza = []
        
        for key, value in data.items():
            for resultado in value:
                if(resultado["confidence"]<threshold_general):
                    for palabra in resultado["words"]:
                        if palabra["confidence"] < threshold_word:
                            palabras_bajas_confianza.append({
                                "start": palabra["start"],
                                "end": palabra["end"],
                                "confidence": palabra["confidence"],
                                "word": palabra["word"],
                                "transcript":resultado["transcript"],
                                "transcript_confidence":resultado["confidence"]
                            })
                    
    return palabras_bajas_confianza

# Cargar el JSON
file="deepgram_transcription_nova-2.json"

# Definir el umbral de confianza
umbral_confianza_palabra = 0.7
umbral_confianza_general = 0.92
# Encontrar palabras con confianza baja
palabras_bajas_confianza = encontrar_palabras_bajas_confianza(file, umbral_confianza_general,umbral_confianza_palabra)

# Imprimir las palabras encontradas
print("Palabras con confianza inferior a", umbral_confianza_palabra)
for palabra in palabras_bajas_confianza:
    print("Palabra:", palabra["word"])
    print("Inicio:", palabra["start"])
    print("Fin:", palabra["end"])
    print("Confianza:", palabra["confidence"])
    print("Transcripción:", palabra["transcript"])
    print("Confianza de la transcripción:", palabra["transcript_confidence"])
    print("--------------------")
