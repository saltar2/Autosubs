import remove_clips as remove_clips,generate_clips_duration as generate_clips,durations as durations,os

lan="ru"
base_dir=rf'C:\Users\salva\Downloads\cv-corpus-17.0-delta-2024-03-15'

if __name__=='__main__':
    #remove_clips.delete_not_validated(os.path.join(base_dir,lan))
    #generate_clips.generate_clip_info(lan,base_dir)
    durations.get_durations(lan)
