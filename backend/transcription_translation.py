import torch,os,deepl_tr as deepl_tr,deepgram_tr as deepgram_tr,silero as silero,spacy_nlp as spacy_nlp,srt,denoiser as denoiser,concurrent.futures
from tqdm import tqdm

def process_frag(i,aud_name):
    with open(f"vad_chunks/{aud_name}.wav", "rb") as f:
        #"vad_chunks/{aud_name}_d.wav"
        denoiser.denoise(f,i,f)

def main(audio_path,language,event_generator):#version para no web

    transcription=True
    transcription_mode=2 # mode 2 deepgram 
    translation=True
    denoise=True
    denoise_ant=False# false indica que no se hace denoise antes de trocear el audio sino despues, true indica lo contrario
    better_formating=True
    ####deepgram models
    # si usas otro modelo mira max workers en deepgram_tr.py
    model_size="nova-2"
    #model_size="base"
    #model_size="enhaced"

    #whisper-deepgram
    #model_size="whisper-large"

    # @markdown Advanced settings:
    vad_threshold = 0.6  # @param {type:"number"} umbral de decision si hay audio de 0 a 1
    chunk_threshold = 0.1  # @param {type:"number"} maxima longitud de silencio entre fragmentos de audio
    deepl_target_lang = "ES"  
    max_attempts = 3  
    assert max_attempts >= 1
    assert vad_threshold >= 0.01
    assert chunk_threshold >= 0.1
    assert audio_path != ""
    assert language != ""
   

    #out_path = os.path.splitext(audio_path)[0] + ".srt"
    out_path_pre = os.path.splitext(audio_path)[0] #+ ".transcription.srt"
    audio_nombre=os.path.splitext(os.path.basename(audio_path))[0]

    if(transcription):
        yield from event_generator('Cortando audio')
        audio_path2=audio_path
        if(denoise and denoise_ant):
            audio_path2=out_path_pre+"_denoised.wav"
            audio_nombre+="_denoised"
            denoiser.denoise(audio_path,audio_path2)
        #print(audio_path2)
        u=silero.silero_vad(audio_path2,vad_threshold,chunk_threshold)#u es la lista de chunks procesados por silero
        if(denoise and denoise_ant==False):
            #procesamos los fragmentos para quitarles el ruido
            print("Denoising ...")
            with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
                 futures=[executor.submit(process_frag,i, f"{audio_nombre}_{i}") for i in range(len(u))]
                 for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                     pass

        subs=[]
        
        try:
            if(transcription_mode==2):
                yield from event_generator('Transcribiendo audio')
                subs=deepgram_tr.deepgram_tr(u,model_size,audio_nombre,language)
                #model_size=".deepgram_"+model_size

                #lan2=deepl_tr.translate_language_name(language)
                #out_path_pre=out_path_pre+"."+lan2+model_size+ "_transcription.srt"
                #with open(out_path_pre, "w", encoding="utf8") as f:
                #    f.write(srt.compose(subs))
                #print("(Untranslated subs saved to", out_path_pre, ")")

            if(translation):
                yield from event_generator('Traduciendo subtitulos')
                mid_subs=deepl_tr.deepl_tr(subs,language,deepl_target_lang)
                if(better_formating):
                    #out_path_formated=out_path_deepl.split(".srt")[0]
                    #out_path_formated=out_path_formated+"_formated.srt"
                    yield from event_generator('Formateando subtitulos')
                    final_subs=spacy_nlp.dividir_lineas_v2(mid_subs)

        except Exception as e:
            print(e)

        finally:
            # Eliminar todos los archivos en la carpeta vad_chunks
            for filename in os.listdir("vad_chunks"):
                file_path = os.path.join("vad_chunks", filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"No se pudo eliminar {file_path}: {e}")
        return final_subs

if __name__ == '__main__':
    main()

