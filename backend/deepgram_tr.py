
import configparser,concurrent.futures,time,srt,datetime,deepgram as d,json,os
from tqdm import tqdm

config=configparser.ConfigParser()
config.read('.env')



def process_chunk(chunk_index,aud_name, dg_client, size,language):#funcion peticion a la api
    #lan=language_codes[language]
    for retry in range(3):
        try:
            with open(f"vad_chunks/{aud_name}.wav", "rb") as f:
                source = {'buffer': f, 'mimetype': 'audio/wav'}
                #options = {"model": size, "language": lan, "utterances": True,"smart_format": True, "timeout": 600}
                options = {"model": size, "detect_language": True, "utterances": True, "timeout": 600, "diarize" : True,"smart_format":True}
                response = dg_client.transcription.sync_prerecorded(source, options)

            if len(response["results"]["utterances"]) > 0:
                break
        except Exception as e:
            print(f"Intento {retry + 1} fallido para chunk {chunk_index}. Error: {e}")
            if retry < 3:
                print(f"Reintentando en 40 segundos...")
                time.sleep(40)
            else:
                print(f"Se alcanzó el número máximo de reintentos para chunk {chunk_index}. Terminando.")
                raise Exception('Revisa la peticion a la api o el status de la api')

    return chunk_index,response



def deepgram_tr(u, model_size,audio_nombre,language):
    auth_key = config.get('API_KEYS', 'DEEPGRAM_KEY')
    dg_client = d.Deepgram(auth_key)
    subs = []
    sub_index = 1
    #segment_info = []
    

    print("Running Deepgram")
    output = "deepgram_transcription_"+model_size+".json" #json donde se puede ver las transcripciones
    output2= "deepgram_transcription_"+model_size+"_complete.json" 
    if(os.path.exists(output)):#borramos el archivo de la ejecucion anterior
        os.remove(output)
    if(os.path.exists(output2)):#borramos el archivo de la ejecucion anterior
        os.remove(output2)
    all_results = {}#debug file
    all_results_completed={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=14) as executor:#para cambiar numero de workers mira esto -> https://developers.deepgram.com/docs/getting-started-with-pre-recorded-audio#rate-limits
        futures = [executor.submit(process_chunk,i, f"{audio_nombre}_{i}", dg_client, model_size,language) for i in range(len(u))]

        #completed_futures, _ = concurrent.futures.wait(futures)

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            chunk_index,response = future.result()

            chunk_results=response["results"]["channels"][0]["alternatives"][0]
            all_results_completed[chunk_index]=response
            if chunk_results['transcript']!='':
                chunk_results=chunk_results["paragraphs"]["paragraphs"]
                for r in chunk_results:
                    for sen in r["sentences"]:
                        start = sen["start"]+ u[chunk_index][0]["offset"]
                        end= sen["end"]+ u[chunk_index][0]["offset"]
                        trans=sen["text"]

                        subs.append(srt.Subtitle(
                            index=sub_index,
                            start=datetime.timedelta(seconds=start),
                            end=datetime.timedelta(seconds=end),
                            content=trans.strip(),))
                    
                        sub_index += 1
            
        # Ordenar all_results por las claves (chunk_index)
        
        sorted_results2 = dict(sorted(all_results_completed.items(), key=lambda item: int(item[0])))
    
        with open(output2,"a",encoding="utf-8") as out2:
            
            out2.write(json.dumps(sorted_results2, indent=4))
      
    subs.sort(key=lambda x: x.start)
    for i, subtitle in enumerate(subs, start=1):
        subtitle.index = i
    return subs


