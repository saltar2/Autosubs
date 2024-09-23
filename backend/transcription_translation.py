import os,deepl_tr as deepl_tr,deepgram_tr as deepgram_tr,silero as silero,formater as formater,srt,denoiser as denoiser,concurrent.futures,time#,whisper_cpp as whisper_tr
import exceptions,llm_detector as llmdct
from tqdm import tqdm

def process_frag(i,aud_name):
    name=f"vad_chunks/{aud_name}.wav"
    with open(name, "rb") as f:
        #"vad_chunks/{aud_name}_d.wav"
        denoiser.denoise(f,i,name)

def main(audio_path,language,queue_event,llm_dtc:bool,llm_crt:bool):#version para no web
    #raise Exception('Error custom')
    transcription=True
    transcription_mode=2 # mode 2 deepgram #mode 1 whisper.ccp

    llm_detection_hallucinations=llm_dtc
    llm_correction=llm_crt

    translation=True

    denoise=True
    denoise_ant=False# false indica que no se hace denoise antes de trocear el audio sino despues, true indica lo contrario

    better_formating=True
    ####deepgram models
    # si usas otro modelo mira max workers en deepgram_tr.py
    model_size="nova-2"
    model2='whisper-large'
    #model_size="base"
    #model_size="enhaced"

    #whisper-deepgram
    #model_size="whisper-large"

    # @markdown Advanced settings:
    vad_threshold = 0.27  # @param {type:"number"} umbral de decision si hay audio de 0 a 1
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
        queue_event.put('Cortando audio ...')
        
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
            queue_event.put('Atenuando ruido del audio ...')
            with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
                 futures=[executor.submit(process_frag,i, f"{audio_nombre}_{i}") for i in range(len(u))]
                 for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                     pass

        final_subs=[]
        
        try:
            if(transcription_mode==2):
                queue_event.put('Transcribiendo audio ...')
                time.sleep(1)
                
                '''subs=deepgram_tr.deepgram_tr(u,model_size,audio_nombre,language)#nova model
                    final_subs=subs
                    #model_size=".deepgram_"+model_size
                    model2='whisper-large'
                    other_subs=deepgram_tr.deepgram_tr(u,model2,audio_nombre,language)#whisper model
                    #final_subs=other_subs'''
                if llm_detection_hallucinations:
                    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                        future_whisper = executor.submit(deepgram_tr.deepgram_tr, u, model2, audio_nombre, language)
                        future_nova = executor.submit(deepgram_tr.deepgram_tr, u, model_size, audio_nombre, language)
                        
                            
                        subs = future_nova.result()
                        other_subs = future_whisper.result()
                        final_subs=subs
                else:
                    subs=deepgram_tr.deepgram_tr(u,model_size,audio_nombre,language)
                    final_subs=subs
                '''out_path_pre=out_path_pre+"."+language+"."+model_size+ "_transcription.srt"
                with open(out_path_pre, "w", encoding="utf8") as f:
                    f.write(srt.compose(other_subs))'''


                if llm_detection_hallucinations:
                    queue_event.put('Revisando transcripcion ...')
                    text_correction=llmdct.revisar_sub(subs,language,other_subs)
                    if llm_correction:
                        subs_revised=llmdct.split_and_correct_srt(subs,text_correction)
                        final_subs=subs_revised

                subs_before_translation= subs_revised if llm_correction else subs
            '''elif transcription_mode==1:
                subs=whisper_tr.transcribe_whisper_cpp(u,audio_nombre)
                final_subs=subs
                raise exceptions.CustomError('Not implemented yet')'''
            if(translation):
                queue_event.put('Traduciendo subtitulos ...')
                
                mid_subs=deepl_tr.deepl_tr(subs_before_translation,language,deepl_target_lang)
                final_subs=mid_subs
                if(better_formating):
                    #out_path_formated=out_path_deepl.split(".srt")[0]
                    #out_path_formated=out_path_formated+"_formated.srt"
                    
                    queue_event.put('Formateando subtitulos ...')
                    
                    final_subs=formater.dividir_lineas_v2(mid_subs)

        except Exception:
            raise 

        finally:
            # Eliminar todos los archivos en la carpeta vad_chunks
            for filename in os.listdir("vad_chunks"):
                file_path = os.path.join("vad_chunks", filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"No se pudo eliminar {file_path}: {e}")
            queue_event.put('FIN')
        
        return final_subs,text_correction if llm_detection_hallucinations else None

if __name__ == '__main__':
    main()

