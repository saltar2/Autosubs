
import configparser,concurrent.futures,time,srt,datetime,deepgram as d,json
from tqdm import tqdm

config=configparser.ConfigParser()
config.read('.env')
language_codes = {
    "chinese": ["zh"],
    "danish": ["da"],
    "dutch": ["nl"],
    "english": ["en-US"],
    "flemish": ["nl"],
    "french": ["fr"],
    "german": ["de"],
    "hindi": ["hi"],
    "indonesian": ["id"],
    "italian": ["it"],
    "japanese": ["ja"],
    "korean": ["ko"],
    "norwegian": ["no"],
    "polish": ["pl"],
    "portuguese": ["pt"],
    "russian": ["ru"],
    "spanish": ["es"],
    "swedish": ["sv"],
    "tamasheq": ["taq"],
    "tamil": ["ta"],
    "turkish": ["tr"],
    "ukrainian": ["uk"]
}


def process_chunk(chunk_index,aud_name, dg_client, size,language):#funcion peticion a la api
    lan=language_codes[language]
    for retry in range(3):
        try:
            with open(f"vad_chunks/{aud_name}.wav", "rb") as f:
                source = {'buffer': f, 'mimetype': 'audio/wav'}
                options = {"model": size, "language": lan, "utterances": True, "timeout": 600}
                response = dg_client.transcription.sync_prerecorded(source, options)

            if len(response["results"]["utterances"]) > 0:
                break
        except Exception as e:
            print(f"Intento {retry + 1} fallido para chunk {chunk_index}. Error: {e}")
            if retry < 3:
                print(f"Reintentando en 60 segundos...")
                time.sleep(60)
            else:
                print(f"Se alcanzó el número máximo de reintentos para chunk {chunk_index}. Terminando.")
                raise Exception('Revisa la peticion a la api o el status de la api')

    return chunk_index, response["results"]["utterances"]



def deepgram_tr(u, model_size,audio_nombre,language):
    auth_key = config.get('API_KEYS', 'DEEPGRAM_KEY')
    dg_client = d.Deepgram(auth_key)
    subs = []
    sub_index = 1
    segment_info = []
    

    print("Running Deepgram")
    output = "deepgram_transcription_"+model_size+".json" #json donde se puede ver las transcripciones

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_chunk,i, f"{audio_nombre}_{i}", dg_client, model_size,language) for i in range(len(u))]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            chunk_index, chunk_results = future.result()
            
            for r in chunk_results:
                if r["start"] > u[chunk_index][-1]["chunk_end"]:
                    continue

                segment_info.append(r)#debug file
                

               # Set start timestamp
                start = r["start"] + u[chunk_index][0]["offset"]#el u es el valor del inicio del archivo de audio y r[start] es el offset de cuando empieza la transcripcion
                for j in range(len(u[chunk_index])):
                    if (
                        r["start"] >= u[chunk_index][j]["chunk_start"]
                        and r["start"] <= u[chunk_index][j]["chunk_end"]
                    ):
                        start = r["start"] + u[chunk_index][j]["offset"]
                        break

                # Set end timestamp
                end = u[chunk_index][-1]["end"] + 0.3
                for j in range(len(u[chunk_index])):
                    if r["end"] >= u[chunk_index][j]["chunk_start"] and r["end"] <= u[chunk_index][j]["chunk_end"]:
                        end = r["end"] + u[chunk_index][j]["offset"]
                        break

                # Add to SRT list
                subs.append(srt.Subtitle(
                        index=sub_index,
                        start=datetime.timedelta(seconds=start),
                        end=datetime.timedelta(seconds=end),
                        content=r["transcript"].strip(),))
                
                sub_index += 1
                
    with open(output, "w", encoding='utf-8') as out:
        out.write(json.dumps(segment_info, indent=4))

    return subs