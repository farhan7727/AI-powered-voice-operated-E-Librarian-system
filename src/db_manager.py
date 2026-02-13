import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()



class query_and_summary:
    def __init__(self):
        self.client=OpenAI(api_key=os.getenv("OPENAI_API"))
        self.DB_PATH = os.path.join(os.path.dirname(__file__), "../data/library.db")


    def __execute_query(self,query):
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            column_names = [description[0] for description in cursor.description]
            tex=[f"{column_names}"]
            for result in results:
                tex.append(f"{result}")

            tex=("\n".join(tex))
            return tex   
    
        except Exception as e:
            return {f"Error:"}
    def __generate_summary(self,book_data):
    

        prompt = f"""
        I have retrieved the following books from the database with the column details:
        {book_data}
        
        Please provide a short summary (approx 50-60 words total for each book) describing these specific books. 
        Mention the titles and authors. Keep it conversational as this will be read out by Text-To-Speech model.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini", #gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful librarian assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()

    def final_summary(self,sql_query):
        tex=self.__execute_query(sql_query)
        summary=self.__generate_summary(tex)
        print(summary)
        return summary