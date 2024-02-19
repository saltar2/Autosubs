from tqdm import tqdm
import srt,datetime,subprocess

#------------------------------------------------------------------------------------------
# Run Whisper on each audio chunk
def whisper_tr(u,model,max_attempts,language,audio_nombre,task="transcribe"):

    print("Running Whisper...")

    subs = []
    segment_info = []
    sub_index = 1
    for i in tqdm(range(len(u))):
        for x in range(max_attempts):
            result = model.transcribe(
                "vad_chunks/" + f"{audio_nombre}_{i}" + ".wav", task=task, language=language, initial_prompt=None
            )
            # Break if result doesn't end with severe hallucinations
            if len(result["segments"]) == 0:
                break
            elif result["segments"][-1]["end"] < u[i][-1]["chunk_end"] + 8.0:
                break
            elif x+1 < max_attempts:
                print("Retrying chunk", i)
        
        
        timestamping(subs,result["segments"],segment_info,u,i,sub_index)

    #with open("segment_info.json", "w", encoding="utf8") as f:
    #    json.dump(segment_info, f, indent=4)
    return subs

def whisper_c(u,max_attempts,audio_nombre):
    print("Running Whisper JAX...")

    subs = []
    segment_info = []
    sub_index = 1
    for i in tqdm(range(len(u))):
        for x in range(max_attempts):
            aud_name="vad_chunks/" + f"{audio_nombre}_{i}" + ".wav"
            mod="./whisper.cpp/models/ggml-model-whisper-large-q5_0.bin"
            full_command=f"./whisper.cpp/main -m {mod} -f {aud_name} -np -l ja"
            '''result = model(
                "vad_chunks/" + f"{audio_nombre}_{i}" + ".wav"
            )'''
            process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Get the output and error (if any)
            output, error = process.communicate()

            if error:
                raise Exception(f"Error processing audio: {error.decode('utf-8')}")

            # Process and return the output string
            decoded_str = output.decode('utf-8').strip()
            processed_str = decoded_str.replace('[BLANK_AUDIO]', '').strip()
            result=processed_str

            # Break if result doesn't end with severe hallucinations
            if len(result["segments"]) == 0:
                break
            elif result["segments"][-1]["end"] < u[i][-1]["chunk_end"] + 8.0:
                break
            elif x+1 < max_attempts:
                print("Retrying chunk", i)
        
        
        timestamping(subs,result["segments"],segment_info,u,i,sub_index)

    #with open("segment_info.json", "w", encoding="utf8") as f:
    #    json.dump(segment_info, f, indent=4)
    return subs

def timestamping(subs,result,segment_info,u,i,sub_index):
    for r in result:
            # Skip audio timestamped after the chunk has ended
            if r["start"] > u[i][-1]["chunk_end"]:
                continue
            # Keep segment info for debugging
            del r["tokens"]
            segment_info.append(r)
            # Skip if log prob is low or no speech prob is high
            if r["avg_logprob"] < -1.0 or r["no_speech_prob"] > 0.7:
                continue
            # Set start timestamp
            start = r["start"] + u[i][0]["offset"]
            for j in range(len(u[i])):
                if (
                    r["start"] >= u[i][j]["chunk_start"]
                    and r["start"] <= u[i][j]["chunk_end"]
                ):
                    start = r["start"] + u[i][j]["offset"]
                    break
            # Prevent overlapping subs
            if len(subs) > 0:
                last_end = datetime.timedelta.total_seconds(subs[-1].end)
                if last_end > start:
                    subs[-1].end = datetime.timedelta(seconds=start)
            # Set end timestamp
            end = u[i][-1]["end"] + 0.5
            for j in range(len(u[i])):
                if r["end"] >= u[i][j]["chunk_start"] and r["end"] <= u[i][j]["chunk_end"]:
                    end = r["end"] + u[i][j]["offset"]
                    break
            # Add to SRT list
            subs.append(
                srt.Subtitle(
                    index=sub_index,
                    start=datetime.timedelta(seconds=start),
                    end=datetime.timedelta(seconds=end),
                    content=r["text"].strip(),
                )
            )
            sub_index += 1

