import os,ffmpeg,torch,concurrent.futures


#------------------------ Run VAD
def silero_vad(audio_path,vad_threshold,chunk_threshold):
    print("Encoding audio...")
    if not os.path.exists("vad_chunks"):
        os.mkdir("vad_chunks")
    ffmpeg.input(audio_path).output(
        "vad_chunks/silero_temp.wav",
        ar="16000",
        ac="1",
        acodec="pcm_s16le",
        map_metadata="-1",
        fflags="+bitexact",
    ).overwrite_output().run(quiet=True)

    
    torch.set_num_threads(1)
    model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad", model="silero_vad", onnx=False
    )
    print("Running VAD...")
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

    # Generate VAD timestamps
    VAD_SR = 16000
    wav = read_audio("vad_chunks/silero_temp.wav", sampling_rate=VAD_SR)
    t = get_speech_timestamps(wav, model, sampling_rate=VAD_SR, threshold=vad_threshold,min_speech_duration_ms=400)

    # Add a bit of padding, and remove small gaps
    for i in range(len(t)):
        t[i]["start"] = max(0, t[i]["start"] - 4800)  # 0.3s head
        t[i]["end"] = min(wav.shape[0] - 16, t[i]["end"] + 11200)  # 0.7s tail
        if i > 0 and t[i]["start"] < t[i - 1]["end"]:
            t[i]["start"] = t[i - 1]["end"]  # Remove overlap

    # If breaks are longer than chunk_threshold seconds, split into a new audio file
    # This'll effectively turn long transcriptions into many shorter ones
    #basicamente si hay un silencio mayor que chunk_threshold corta ahi 
    u = [[]]
    for i in range(len(t)):
        if i > 0 and t[i]["start"] > t[i - 1]["end"] + (chunk_threshold * VAD_SR):
            u.append([])
        u[-1].append(t[i])

    # Merge speech chunks
    audio_filename = os.path.splitext(os.path.basename(audio_path))[0]
    '''for i in range(len(u)):
        output_filename=f"vad_chunks/{audio_filename}_{i}.wav"
        save_audio(
            output_filename,
            collect_chunks(u[i], wav),
            sampling_rate=VAD_SR,
        )'''

    def save_chunk(i, chunk):
        output_filename = f"vad_chunks/{audio_filename}_{i}.wav"
        save_audio(output_filename, collect_chunks(chunk, wav), sampling_rate=VAD_SR)

    # Save audio chunks using ThreadPoolExecutor for parallelism
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(save_chunk, i, chunk) for i, chunk in enumerate(u)]
        for future in futures:
            future.result()  # Ensure all tasks are completed

    os.remove("vad_chunks/silero_temp.wav")

    # Convert timestamps to seconds
    for i in range(len(u)):
        offset = 0.0
        for j in range(len(u[i])):
            u[i][j]["start"] /= VAD_SR#valor absoluto
            u[i][j]["end"] /= VAD_SR#valor absoluto

            if j == 0:
                offset = u[i][j]["start"]
                
            u[i][j]["offset"] = offset

            u[i][j]["chunk_start"] = u[i][j]["start"]-offset#valor relativo al fragmento de audio

            u[i][j]["chunk_end"] = u[i][j]["end"]-offset#valor relativo al fragmento de audio
    
    return u

''' for i in range(len(u)):
        time = 0.0
        offset = 0.0
        for j in range(len(u[i])):
            u[i][j]["start"] /= VAD_SR#valor absoluto
            u[i][j]["end"] /= VAD_SR#valor absoluto
            u[i][j]["chunk_start"] = time#valor relativo al fragmento de audio
            time += u[i][j]["end"] - u[i][j]["start"]#valor relativo al fragmento de audio
            u[i][j]["chunk_end"] = time
            if j == 0:
                offset += u[i][j]["start"]
            else:
                offset += u[i][j]["start"] - u[i][j - 1]["end"]
            u[i][j]["offset"] = offset'''