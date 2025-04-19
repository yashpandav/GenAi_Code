from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    # Initialize the API
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    
    try:
        # Get any manually created transcript
        manual_transcript = transcript_list.find_manually_created_transcript(["en", "en-US", "en-GB"])
        print(f"Found manually created transcript in {manual_transcript.language} ({manual_transcript.language_code})")
        return manual_transcript.fetch()
    except:
        # If no manual transcript exists, look for auto-generated ones
        try:
            # Get any auto-generated transcript
            auto_transcript = transcript_list.find_generated_transcript([])
            print(f"Found auto-generated transcript in {auto_transcript.language} ({auto_transcript.language_code})")
            
            # If not in English, translate it to English
            if auto_transcript.language_code != 'en':
                print(f"Translating from {auto_transcript.language} to English...")
                translated = auto_transcript.translate('en')
                return translated.fetch()
            else:
                return auto_transcript.fetch()
        except Exception as e:
            print(f"Error: {e}")
            return None

# Example usage
video_id = "UWCB_ZAAiKM"
transcript = get_transcript(video_id)

if transcript:
    # Print the first few entries of the transcript
    print("\nTranscript preview:")
    print(transcript)
else:
    print("No transcript available")