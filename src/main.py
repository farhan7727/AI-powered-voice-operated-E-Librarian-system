from stt import Transcriber
from llm_query import LLM
from db_manager import query_and_summary
from tts import SpeechCreate

speech=SpeechCreate()
trans=Transcriber()
llm=LLM()
QaS=query_and_summary()

def main():
    user_text = trans.input_audio()
    print(f"User said: {user_text}")
    sql_query=llm.text_to_sql(user_text)
    print(sql_query)
    summary=QaS.final_summary(sql_query)
    speech.speak(summary)
    
    
if __name__=="__main__":
    main()