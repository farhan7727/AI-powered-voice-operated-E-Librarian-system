import gradio as gr
import time
import sounddevice as sd
from scipy.io.wavfile import write
from stt import Transcriber
from llm_query import LLM
from db_manager import query_and_summary
from tts import SpeechCreate

class GuiTTS(SpeechCreate):
    """
    Extends your SpeechCreate to generate the file WITHOUT playing it 
    on the server speakers (Pygame), so the Web UI can play it instead.
    """
    def generate_only(self, text):
        self._SpeechCreate__generate_audio(text)
        return self.output_path

class GuiTranscriber(Transcriber):
    """
    Extends your Transcriber to add a visual progress bar (counter) 
    for the UI while recording.
    """
    def input_audio_with_progress(self, progress_reporter):
        print(f"Recording for {self.DURATION} seconds...")
        
        recording = sd.rec(int(self.DURATION * self.FS), 
                           samplerate=self.FS,
                           channels=self.CHANNELS, 
                           dtype='float64')
        
        for i in range(self.DURATION):
            progress_reporter((i + 1) / self.DURATION, desc=f"Recording... {self.DURATION - i}s left")
            time.sleep(1)
            
        sd.wait() 
        write(self.audio_path, self.FS, recording)
        return self._Transcriber__transcribe_audio()


transcriber = GuiTranscriber()
llm = LLM()
db_manager = query_and_summary()
tts = GuiTTS()



def process_query(progress=gr.Progress()):
    """
    The main pipeline function triggered by the UI button.
    """
    # 1. Record & Transcribe
    user_text = transcriber.input_audio_with_progress(progress)
    if not user_text:
        yield "Error: No speech detected or transcription failed.", "", None
        return

    # Update Status: Transcribed
    status_log = f"User said: \"{user_text}\"\n\nGenerating SQL..."
    yield status_log, "", None

    # 2. LLM -> SQL
    sql_query = llm.text_to_sql(user_text)
    status_log += f"\nSQL Query: {sql_query}\n\nFetching Books..."
    yield status_log, "", None

    # 3. DB -> Summary
    summary = db_manager.final_summary(sql_query)
    status_log += f"\nSummary Generated."
    yield status_log, summary, None

    # 4. TTS -> Audio File
    status_log += f"\nSynthesizing Voice."
    yield status_log, summary, None
    audio_path = tts.speak(summary)
    status_log += f"\nReady for next query."
    yield status_log, summary, str(audio_path)

# Layout for gradio
with gr.Blocks(theme=gr.themes.Soft(), title="AI Librarian") as demo:
    
    gr.Markdown(
        """
        # AI-Powered Voice Librarian
        Click the button below to ask for book recommendations. The system will listen for 5 seconds.
        """
    )

    with gr.Row(variant="panel"):
        with gr.Column(scale=1):
            record_btn = gr.Button("Record Query (5s)", variant="primary", size="lg")
            
            log_box = gr.Textbox(label="Process Logs", lines=6, interactive=False)
        
        with gr.Column(scale=1):
            summary_box = gr.Textbox(label="Librarian's Answer", lines=6)
            
            audio_player = gr.Audio(label="Voice Response", type="filepath", autoplay=True)

    record_btn.click(
        fn=process_query,
        inputs=[],
        outputs=[log_box, summary_box, audio_player]
    )

if __name__ == "__main__":
    demo.launch()