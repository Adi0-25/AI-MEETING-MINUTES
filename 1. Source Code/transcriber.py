from faster_whisper import WhisperModel
import torch
from functools import lru_cache

@lru_cache(maxsize=3)
def get_whisper_model(model_size='base'):
    # Detect GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Use float16 if on GPU for double speed, otherwise int8 for fast CPU inference
    compute_type = "float16" if device == "cuda" else "int8"
    
    return WhisperModel(model_size, device=device, compute_type=compute_type)

def transcribe_audio(audio_path, model_size='base'):
    model = get_whisper_model(model_size)
    
    # We use VAD filter to drop silent audio completely to strip dead air before inference.
    # condition_on_previous_text=False ensures each audio window is evaluated independently,
    # preventing auto-regressive hallucination loops on silent patches.
    # task='translate' ensures non-English audio is natively translated to English output.
    segments, info = model.transcribe(
        audio_path, 
        task='translate',
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        condition_on_previous_text=False,  # Prevents hallucination loops on silent audio
        initial_prompt="This is a formal corporate meeting recording. The speakers are discussing critical business topics."
    )
    
    full_text = []
    formatted_segments = []
    
    for segment in segments:
        full_text.append(segment.text.strip())
        formatted_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': segment.text.strip()
        })
        
    return {
        'text': " ".join(full_text).strip(),
        'language': 'en', # Force 'en' because task='translate' guarantees English text output
        'original_audio_language': info.language,
        'segments': formatted_segments
    }
