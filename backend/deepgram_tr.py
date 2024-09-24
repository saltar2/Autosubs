import exceptions
import configparser,concurrent.futures,time,srt,datetime,deepgram as d,json,os
from tqdm import tqdm

config=configparser.ConfigParser()
config.read('.env')

def process_chunk(chunk_index,aud_name, dg_client, size,language):#funcion peticion a la api
    #lan=language_codes[language]
    for retry in range(4):
        try:
            with open(f"vad_chunks/{aud_name}.wav", "rb") as f:
                source = {'buffer': f, 'mimetype': 'audio/wav'}
                #options = {"model": size, "language": lan, "utterances": True,"smart_format": True, "timeout": 600}
                options = {"model": size, "detect_language": True, "utterances": True, "timeout": 300, "diarize" : True,"smart_format":True}
                response = dg_client.transcription.sync_prerecorded(source, options)
                time.sleep(2)
            if len(response["results"]["utterances"]) > 0:
                break
        except Exception as e:
            print(f"Intento {retry + 1} fallido para chunk {chunk_index}. Error: {e}")
            if retry < 3:
                print(f"Reintentando en 40 segundos...")
                time.sleep(40)
            else:
                print(f"Se alcanzó el número máximo de reintentos para chunk {chunk_index}. Terminando.")
                #raise Exception('Revisa la peticion a la api o el status de la api')
                raise exceptions.CustomError('Revisa la peticion a la api o el status de la api')
    return chunk_index,response

def merge_subs(subs):
  merged_subs = []
  current_sub = None

  for sub in subs:
    # If no current subtitle or current subtitle ends before this one starts
    if not current_sub or (current_sub.end.total_seconds() <= sub.start.total_seconds()):
        current_sub = sub  # Create a copy to avoid modifying original
        merged_subs.append(current_sub)
    # If subtitles overlap, update current subtitle with the later end time
    elif current_sub.start.total_seconds() < sub.start.total_seconds() < current_sub.end.total_seconds():
        current_sub.end = max(current_sub.end, sub.end)

        prop=sub.proprietary#actual sub
        speaker=current_sub.proprietary#before sub

        if prop==speaker:
            merged_subs[-1].content=current_sub.content +' ' + sub.content  # Combine content
        else: #diferentes speakers
            merged_subs[-1].content = "-"+current_sub.content+ ' -' + sub.content
            merged_subs[-1].proprietary += speaker
        
  return merged_subs

def deepgram_tr(u, model_size,audio_nombre,language):
    auth_key = config.get('API_KEYS', 'DEEPGRAM_KEY')
    dg_client = d.Deepgram(auth_key)
    subs = []
    
    sub_index = 1
    #segment_info = []
    
    print(f"Running Deepgram {model_size}")
    #output = "deepgram_transcription_"+model_size+".json" #json donde se puede ver las transcripciones
    output2= "deepgram_transcription_"+model_size+"_complete.json" 
    #if(os.path.exists(output)):#borramos el archivo de la ejecucion anterior
    #    os.remove(output)
    if(os.path.exists(output2)):#borramos el archivo de la ejecucion anterior
        os.remove(output2)
    #all_results = {}#debug file
    all_results_completed={}
    workers=4 if str(model_size).__contains__('whisper') else 12
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:#para cambiar numero de workers mira esto -> https://developers.deepgram.com/docs/getting-started-with-pre-recorded-audio#rate-limits
        futures = [executor.submit(process_chunk,i, f"{audio_nombre}_{i}", dg_client, model_size,language) for i in range(len(u))]
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures),desc=f"Processing Items from {model_size}"):
            chunk_index,response = future.result()
            all_results_completed[chunk_index]=response

        sorted_results= dict(sorted(all_results_completed.items(), key=lambda item: int(item[0])))

        for c in tqdm(sorted_results,total=len(sorted_results)):#c tiene el numero del chunk index
            sub_res=sorted_results[c]["results"]["channels"][0]["alternatives"]#para el modelo de whisper si no hay transcripcion no existe una lista vacia pero para los modelos de deepgram si devuelve 
            if len(sub_res)>0:
                chunk_results=sorted_results[c]["results"]["channels"][0]["alternatives"][0]
            else:
                continue
            
            if chunk_results['transcript']!='':
                chunk=chunk_results["paragraphs"]["paragraphs"]
                for r in chunk:
                    speaker=str(r["speaker"])
                    for sen in r["sentences"]:
                        start = sen["start"]+u[c][0]["offset"]
                        end = sen["end"]+u[c][0]["offset"]
                        text = sen["text"]
                        

                        # Si la duración del subtítulo es menor a 1 segundo
                        if end - start < 1:
                            # Si hay subtítulos previos, intenta combinarlo con el último
                            if subs and start - subs[-1].end.total_seconds() < 0.09 and start > subs[-1].start.total_seconds():
                                # Si el margen de tiempo entre el final del subtítulo previo y el inicio del actual es menor a 0.09 segundos
                                #Se ha de comprobar que ambos textos correspondan al mismo speaker sino hay que añadir guiones
                                # Combina el texto con el subtítulo previo
                                prop=subs[-1].proprietary
                                if prop==speaker:
                                    subs[-1].content += ' ' + text.strip()
                                else: #diferentes speakers
                                    subs[-1].content = "-"+subs[-1].content+ ' -' + text.strip()
                                    subs[-1].proprietary += speaker
                                subs[-1].end = datetime.timedelta(seconds=end)
                                    
                            else :       
                            # Si no se puede combinar con el subtítulo anterior, se agrega el subtítulo actual como uno nuevo
                            # De esta forma puede aun solaparse con futuros subtitulos que aun esten por venir pero nunca con los anteriores
                            # Mas adelante se hara un merge si alguno se solapa
                                if subs:
                                    ant_end=subs[-1].end.total_seconds()

                                    diff_with_ant = start-ant_end
                                    # diff_with_next=end-next
                                    total = end-start
                                    fin = True
                                    margin = 0.05

                                    while fin:
                                        if diff_with_ant > margin:
                                            start -= margin
                                            diff_with_ant = start-ant_end
                                            total = end-start
                                            if total > 1:
                                                fin = False

                                        end += margin

                                        total = end-start
                                        if total > 1:
                                            fin = False

                                    subs.append(srt.Subtitle(
                                        index=sub_index,
                                        start=datetime.timedelta(seconds=start),
                                        end=datetime.timedelta(seconds=end),
                                        content=text.strip(),proprietary=speaker)
                                        )
                                    sub_index += 1
                                else:#caso primer subtitulo
                                    total = end-start
                                    fin = True
                                    margin = 0.05

                                    while fin:
                                        if start-margin >= 0:
                                            start -= margin
                                            total = end-start
                                            if total > 1:
                                                fin = False

                                        end += margin

                                        total = end-start
                                        if total > 1:
                                            fin = False
                                    subs.append(srt.Subtitle(
                                        index=sub_index,
                                        start=datetime.timedelta(seconds=start),
                                        end=datetime.timedelta(seconds=end),
                                        content=text.strip(),proprietary=speaker)
                                        )
                                    sub_index += 1
                        else:
                            # Si la duración del subtítulo es mayor o igual a 1 segundo, agrégalo como un nuevo subtítulo
                            subs.append(srt.Subtitle(
                                index=sub_index,
                                start=datetime.timedelta(seconds=start),
                                end=datetime.timedelta(seconds=end),
                                content=text.strip(),proprietary=speaker))
                            sub_index += 1       
    
    with open(output2,"a",encoding="utf-8") as out:
            
        out.write(json.dumps(sorted_results, indent=4))
      
    subs.sort(key=lambda x: x.start)
    for i, subtitle in enumerate(subs, start=1):
        subtitle.index = i
    subs=merge_subs(subs)
    return subs




