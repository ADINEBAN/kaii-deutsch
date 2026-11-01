import io
import soundfile as sf
import gradio as gr
from kokoro import KPipeline
import torch

# Initialize Kokoro German Pipeline ('d' for German / de)
pipeline = KPipeline(lang_code='d')

def tts(text, speed=0.95):
    if not text or not text.strip():
        return None
    
    # Generate audio segments with Thorsten German voice 'df_thorsten' or 'dm_thorsten'
    generator = pipeline(text.strip(), voice='dm_thorsten', speed=speed, split_pattern=r'\n+')
    all_audio = []
    
    for _, _, audio in generator:
        all_audio.append(audio)
    
    if not all_audio:
        return None
        
    combined = torch.cat(all_audio, dim=0).cpu().numpy()
    
    # Kokoro uses 24000 Hz sample rate
    return (24000, combined)

# Create Gradio API interface
demo = gr.Interface(
    fn=tts,
    inputs=[
        gr.Textbox(label="Văn bản tiếng Đức", value="Hallo! Willkommen bei KAII."),
        gr.Slider(minimum=0.5, maximum=1.5, value=0.95, label="Tốc độ đọc")
    ],
    outputs=gr.Audio(label="Giọng đọc Thorsten TTS", type="numpy"),
    title="KAII Thorsten-Voice Kokoro TTS Server",
    description="Máy chủ phát âm tiếng Đức giọng AI người thật cho ứng dụng học tiếng Đức KAII.",
    api_name="predict"
)

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860)

