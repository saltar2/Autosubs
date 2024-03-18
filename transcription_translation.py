import torch,os,deepl_tr,deepgram_tr,silero,spacy_nlp,srt,denoiser
from tqdm import tqdm


def main(audio_path,language):

    transcription=True
    transcription_mode=2 # mode 2 deepgram 
    translation=True
    denoise=True
    better_formating=False
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

    if not os.path.exists(audio_path): 
        raise ValueError("Input audio not found. Is your audio_path correct?"+audio_path)
            

    out_path = os.path.splitext(audio_path)[0] + ".srt"
    out_path_pre = os.path.splitext(audio_path)[0] #+ ".transcription.srt"
    audio_nombre=os.path.splitext(os.path.basename(audio_path))[0]

    if(transcription):
        audio_path2=audio_path
        if(denoise):
            audio_path2=out_path_pre+"_denoised.wav"
            audio_nombre+="_denoised"
            denoiser.denoise(audio_path,audio_path2)
        u=silero.silero_vad(audio_path2,vad_threshold,chunk_threshold)#u es la lista de chunks procesados por silero
        subs=[]
        
        try:
            if(transcription_mode==2):
                subs=deepgram_tr.deepgram_tr(u,model_size,audio_nombre,language)
                model_size=".deepgram_"+model_size

                lan2=deepl_tr.translate_language_name(language)
                out_path_pre=out_path_pre+"."+lan2+model_size+ "_transcription.srt"
                with open(out_path_pre, "w", encoding="utf8") as f:
                    f.write(srt.compose(subs))
                print("(Untranslated subs saved to", out_path_pre, ")")

            if(translation):
                out_path_deepl=deepl_tr.deepl_tr(subs,out_path,language,deepl_target_lang,model_size)
                if(better_formating):
                    out_path_formated=out_path_deepl.split(".srt")[0]
                    out_path_formated=out_path_formated+"_formated.srt"
                    spacy_nlp.dividir_lineas_v2(out_path_deepl,out_path_formated)

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

if __name__ == '__main__':
    main()

