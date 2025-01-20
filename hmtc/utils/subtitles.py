import webvtt


  
    


def analyze_subtitle_density(vtt_file):
    vtt = webvtt.read(vtt_file)
    
    # Initialize variables
    subtitle_density = []
    last_end_time = 0
    talking_segments = []
    music_segments = []
    
    # Analyze each caption
    for caption in vtt:
        start_time = caption.start_in_seconds
        end_time = caption.end_in_seconds
        text = caption.text.strip()

        # Calculate the duration of the caption
        duration = end_time - start_time
        
        # If there is a gap between the last caption and the current one, record it
        if last_end_time < start_time:
            gap_duration = start_time - last_end_time
            subtitle_density.append((last_end_time, start_time, 0))  # No subtitles in this gap
            
            # Check if the gap is significant (e.g., more than 1 second)
            if gap_duration > 1:
                music_segments.append((last_end_time, start_time))  # Potential music segment

        # Record the current caption's density
        subtitle_density.append((start_time, end_time, len(text.split())))  # Count words as density
        last_end_time = end_time
        talking_segments.append((start_time, end_time, text))  # Record talking segment

    # Check for any remaining gap after the last caption
    if last_end_time < vtt[-1].end_in_seconds:
        gap_duration = vtt[-1].end_in_seconds - last_end_time
        if gap_duration > 1:
            music_segments.append((last_end_time, vtt[-1].end_in_seconds))  # Potential music segment

    return {
        "subtitle_density": subtitle_density,
        "talking_segments": talking_segments,
        "music_segments": music_segments,
    }

# Example usage
result = analyze_subtitle_density("hmtc/utils/temp/omegle_50.en.vtt")
#print("Subtitle Density:", result["subtitle_density"])
#print("Talking Segments:", result["talking_segments"])
print("Music Segments:", result["music_segments"])