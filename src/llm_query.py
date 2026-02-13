import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

class LLM:
    def __init__(self):
        self.openAI=OpenAI(api_key=os.getenv("OPENAI_API"))
        self.schema=DB_SCHEMA = """
                    Table: books
                    Columns:
                    - id (TEXT)
                    - book_title (TEXT)
                    - author_first_name (TEXT)
                    - author_last_name (TEXT)
                    - genre (TEXT)
                    - sub_genre (TEXT)
                    """
        
    def text_to_sql(self,user_query):

        system_prompt=f"""
            You are a SQL expert for a library database. 
            Schema: \n{self.schema}
        
            Rules:
            1. Generate a valid SQLite query based on the user's request.
            2. the name of the 'genre' present in the database are "fiction", "nonfiction", "philosophy", "science", and "tech".
            3. If the user asks for a specific topic (e.g., "tech" or "computer science"), search the 'sub_genre' only if any of the 'genre' from point 2 is not mentioned in the query, else if olny 'genre' from point 2 is given then search only 'genre' else search for both 'genre' and 'sub_genre' columns if both are given in the query using LIKE operators.        
            4. ALWAYS include "ORDER BY RANDOM() LIMIT 3" if the user asks for recommendations or a list of books.
            5. Output ONLY the raw SQL query. Do not wrap it in markdown (```sql). Do not add explanations.
            6. Case insensitive matching is preferred (use LOWER() or LIKE).
        """
        response = self.openAI.chat.completions.create(
        model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0
        )

        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        return sql_query