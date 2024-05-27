import remove_clips as remove_clips,generate_clips_duration as generate_clips,durations as durations,os

lan="th"
base_dir="test\\langs"

if __name__=='__main__':
    remove_clips.delete_not_validated(os.path.join(base_dir,lan))
    generate_clips.generate_clip_info(lan,base_dir)
    durations.get_durations(os.path.join(base_dir,lan),lan)
