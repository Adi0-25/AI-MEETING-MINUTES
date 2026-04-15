import warnings
warnings.filterwarnings('ignore')

from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from functools import lru_cache

@lru_cache(maxsize=1)
def get_llm_pipeline():
    import torch
    model_id = "Qwen/Qwen1.5-0.5B-Chat"
    has_cuda = torch.cuda.is_available()
    device_id = 0 if has_cuda else -1
    torch_dtype = torch.float16 if has_cuda else torch.float32

    return pipeline(
        "text-generation",
        model=model_id,
        device=device_id,
        model_kwargs={"torch_dtype": torch_dtype, "low_cpu_mem_usage": True}
    )

@lru_cache(maxsize=2)
def get_translator(from_lang, to_lang):
    from transformers import MarianMTModel, MarianTokenizer
    model_name = f'Helsinki-NLP/opus-mt-{from_lang}-{to_lang}'
    return {
        'model': MarianMTModel.from_pretrained(model_name),
        'tokenizer': MarianTokenizer.from_pretrained(model_name)
    }

def translate(text, from_lang, to_lang):
    if from_lang == to_lang:
        return text
    
    try:
        translator = get_translator(from_lang, to_lang)
        tokenizer = translator['tokenizer']
        model = translator['model']
        
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        translated = model.generate(**inputs)
        return tokenizer.decode(translated[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Warning: Translation {from_lang} -> {to_lang} failed: {e}. Falling back.")
        return text

def summarize_text(text, original_lang='en', target_lang='en'):
    if not text or not text.strip():
        return {
            'professional_minutes': '',
            'language': target_lang
        }
    
    original_lang = original_lang[:2] if len(original_lang) > 2 else original_lang
    target_lang = target_lang[:2] if len(target_lang) > 2 else target_lang
    
    if original_lang != 'en':
        text = translate(text, original_lang, 'en')
    
    pipe = get_llm_pipeline()
    
    # --- SEMANTIC CHUNKING FOR LONG MEETINGS ---
    target_chunk_size = 6000
    
    if len(text) <= 8000:
        messages = [
            {"role": "system", "content": "You are a highly professional Executive Assistant. Your task is to read the provided meeting transcript and produce polished, formal Meeting Minutes."},
            {"role": "user", "content": f"Please generate professional Meeting Minutes from the following transcript. Format your response in Markdown with the following sections:\n\n# Meeting Minutes\n## Executive Summary\n## Key Discussion Points\n## Decisions Made\n## Action Items\n\nTranscript:\n{text}"}
        ]
    else:
        print(f"Transcript is {len(text)} chars long. Using semantic chunked summarization.")
        
        # Semantic chunking using regex boundaries
        import re
        sentences = re.split(r'(?<=[.?!])\s+|\n', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            if len(current_chunk) + len(sentence) < target_chunk_size:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
                
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i+1}/{len(chunks)}...")
            chunk_msg = [
                {"role": "system", "content": "You are an assistant. Extract the key discussion points, decisions, and action items from this part of the meeting."},
                {"role": "user", "content": f"Extract key points:\n{chunk}"}
            ]
            prompt = pipe.tokenizer.apply_chat_template(chunk_msg, tokenize=False, add_generation_prompt=True)
            outputs = pipe(prompt, max_new_tokens=250, do_sample=False)
            prompt_str = str(prompt)
            gen_text = str(outputs[0]["generated_text"]) # type: ignore
            chunk_summaries.append(gen_text[len(prompt_str):].strip())

        combined_summary = "\n\n---\n\n".join(chunk_summaries)
        combined_summary = combined_summary[:20000] # Safeguard for ultra-long combined contexts

        messages = [
            {"role": "system", "content": "You are a highly professional Executive Assistant. Your task is to read the provided compiled meeting notes and produce polished, formal Meeting Minutes."},
            {"role": "user", "content": f"Please generate professional Meeting Minutes from the following compiled notes. Format your response in Markdown with the following sections:\n\n# Meeting Minutes\n## Executive Summary\n## Key Discussion Points\n## Decisions Made\n## Action Items\n\nCompiled Notes:\n{combined_summary}"}
        ]

    prompt = pipe.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    outputs = pipe(
        prompt,
        max_new_tokens=500,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
    )
    
    prompt_str = str(prompt)
    gen_text = str(outputs[0]["generated_text"]) # type: ignore
    generated_text = gen_text[len(prompt_str):].strip()
    
    if target_lang != 'en':
        generated_text = translate(generated_text, 'en', target_lang)
    
    return {
        'professional_minutes': generated_text,
        'language': target_lang
    }

