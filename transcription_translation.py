import torch, whisper,os,deepl_tr,deepgram_tr,silero
from tqdm import tqdm


def main(audio_path,language):

    transcription=True
    transcription_mode=2 # mode 2 deepgram 

    translation=True
    ####deepgram models
    model_size="nova-2"
    #model_size="base"
    #model_size="enhaced"


    # @markdown Advanced settings:
    vad_threshold = 0.2  # @param {type:"number"} umbral de decision si hay audio
    chunk_threshold = 2.5  # @param {type:"number"} maxima longitud de silencio
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
    out_path_pre = os.path.splitext(audio_path)[0] + ".transcription.srt"
    audio_nombre=os.path.splitext(os.path.basename(audio_path))[0]

    if(transcription):
        u=silero.silero_vad(audio_path,vad_threshold,chunk_threshold)#u es la lista de chunks procesados por silero
        subs=[]

        try:
            if(transcription_mode==2):
                subs=deepgram_tr.deepgram_tr(u,model_size,audio_nombre,language)
                model_size=".deepgram_"+model_size

            if(translation):
                out_path_deepl=deepl_tr.deepl_tr(subs,out_path_pre,out_path,language,deepl_target_lang,model_size)
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

