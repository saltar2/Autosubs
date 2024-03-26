import os,json, subprocess,backend.deepl_tr as dpl_tr

def extract_audio_ffmpeg_v2(input_dir,language):
  # Supported video extensions
  video_extensions = [".mp4", ".avi", ".mkv", ".mov", ".m4v", ".mts", ".wmv", ".mpg", ".flv"]

  # List video files
  video_files = [f for f in os.listdir(input_dir) if f.lower().endswith(tuple(video_extensions))]

  for video_file in video_files:
    video_path = os.path.join(input_dir, video_file)
    output_audio_path = os.path.join(input_dir, f"{os.path.splitext(video_file)[0]}.wav")

    # Use ffprobe to get track information
    ffprobe_cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", video_path]
    ffprobe_output = subprocess.check_output(ffprobe_cmd, universal_newlines=True)
    streams_info = json.loads(ffprobe_output)["streams"]

    # Select audio track based on language and format

    
    preferred_language=dpl_tr.translate_language_name(language)
    if preferred_language is None:#idioma predeterminado
        preferred_language = "eng"
        
    preferred_formats = ["aac", "mp3", "flac"]

    best_audio_stream = None
    for stream in streams_info:
      if stream["codec_type"] == "audio":
        # Check for preferred language
        if stream["tags"].get("language", "") == preferred_language:
          if stream["codec_name"] in preferred_formats:
            best_audio_stream = stream
            break
        # Otherwise, check for preferred format if no English track is found
        elif best_audio_stream is None and stream["codec_name"] in preferred_formats:
          best_audio_stream = stream

    best_audio_stream = None
    for stream in streams_info:
      if stream["codec_type"] == "audio":
        if stream["codec_name"] in preferred_formats:
          best_audio_stream = stream
          break

    # Extract audio if a suitable track is found
    if best_audio_stream:
      try:
        audio_stream_index = best_audio_stream["index"]
        audio_codec = best_audio_stream["codec_name"]

        # Extract audio to intermediate file using original codec
        intermediate_audio_path = os.path.join(input_dir, f"{os.path.splitext(video_file)[0]}_{audio_codec}.{audio_codec}")
        subprocess.run(["ffmpeg", "-i", video_path, "-vn", "-acodec", "copy", "-map", f"0:{audio_stream_index}","-y", intermediate_audio_path])

        # Convert intermediate file to WAV
        subprocess.run(["ffmpeg", "-i", intermediate_audio_path, "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2","-y", output_audio_path])

        # Remove intermediate file
        os.remove(intermediate_audio_path)

        print(f"Audio extracted from '{video_file}' and saved as '{output_audio_path}' (original format: {audio_codec})")
      except Exception as e:
        print(f"Error processing '{video_file}': {e}")
    else:
      print(f"No suitable audio track found in '{video_file}'")






'''def rename_files(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith(" ESP.wav"):
            # Construir el nuevo nombre de archivo eliminando " ESP"
            new_name = file_name[:-8] + ".wav"
            old_path = os.path.join(directory, file_name)
            new_path = os.path.join(directory, new_name)

            # Renombrar el archivo
            os.rename(old_path, new_path)
            print(f'Renamed: {file_name} -> {new_name}')'''



#comando para extraer audio de un video desde linea de comandos con ffmpeg.
''' ffmpeg -i '.\Avalanches_ Unpredictable, Inevitable, Fatal _ Deadly Disasters _ Free Documentary (192kbit_AAC).mkv'
 -vn -acodec copy 'Avalanches_ Unpredictable, Inevitable, Fatal _ Deadly Disasters _ Free Documentary (192kbit_AAC).wav' "" '''