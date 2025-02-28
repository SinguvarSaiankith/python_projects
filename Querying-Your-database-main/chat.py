import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
import pymysql
import pandas as pd
from sqlalchemy.sql import text  # Import SQL text for safe query execution

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "key.env")
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google API Key not found. Check if 'key.env' exists and is formatted correctly.")
    raise ValueError("Google API Key missing. Check if 'key.env' exists and is formatted correctly.")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)


# Function to initialize the database connection
def init_database(db_user: str, db_password: str, db_host: str, db_name: str):
    try:
        db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
        return db
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None


# Function to fetch table schema
def get_schema(db):
    try:
        return db.get_table_info()
    except Exception as e:
        st.error(f"❌ Failed to retrieve schema: {e}")
        return None


# Function to generate SQL query using Gemini
def get_sql_chain(schema, chat_history, question):
    prompt = f"""
    You are an SQL expert! Convert the following question into an optimized SQL query based on the schema:

    <SCHEMA>{schema}</SCHEMA>
    Conversation History: {chat_history}

    Example:
    - How many records are present? 
      SQL: SELECT COUNT(*) FROM users;

    - Show all users above 30 years old.
      SQL: SELECT * FROM users WHERE age > 30;

    Your Turn:
    Question: {question}
    SQL Query:
    """
    return prompt


# Function to generate SQL query response from Gemini API
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content([prompt, question])
        return response.text.strip()
    except Exception as e:
        st.error(f"❌ Error generating SQL query: {e}")
        return None


# Streamlit UI Setup
st.set_page_config(page_title="SQL Query Generator with LLM")
st.header("💡 Query Your Database with AI")

# Sidebar for Database Connection
with st.sidebar:
    st.subheader("Database Connection")
    db_host = st.text_input("Host", value="localhost", key="host")
    db_user = st.text_input("User", key="user")
    db_password = st.text_input("Password", type="password", key="password")
    db_name = st.text_input("Database", key="database")

    if st.button("🔗 Connect"):
        with st.spinner("Connecting to the database..."):
            db = init_database(db_user, db_password, db_host, db_name)
            if db:
                st.session_state.db = db
                st.success("✅ Connected to the database!")

# Check if DB is connected
if "db" in st.session_state and st.session_state.db:
    schema = get_schema(st.session_state.db)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [AIMessage("Hello! I'm a SQL assistant. Ask me anything about your database.")]

# Display chat messages
for message in st.session_state.chat_history:
    role = "ai" if isinstance(message, AIMessage) else "human"
    with st.chat_message(role):
        st.markdown(message.content)

# User Input
user_query = st.chat_input("💬 Type your query...")

if user_query and user_query.strip():
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("human"):
        st.markdown(user_query)

    if "db" in st.session_state and st.session_state.db:
        with st.chat_message("ai"):
            st.write("⏳ Generating SQL query...")

            prompt = get_sql_chain(schema, st.session_state.chat_history, user_query)
            sql_query = get_gemini_response(user_query, prompt)

            if sql_query:
                # Clean SQL Query
                clean_sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

                st.write(f"📝 Generated SQL Query:\n```sql\n{clean_sql_query}\n```")

                # Execute SQL Query safely
                try:
                    with st.session_state.db._engine.connect() as connection:
                        result = connection.execute(text(clean_sql_query))  # Using text() for safe execution
                        rows = result.fetchall()

                        if rows:
                            # Fetch column names dynamically
                            columns = result.keys()
                            df = pd.DataFrame(rows, columns=columns)

                            # Display DataFrame as a table
                            st.dataframe(df)
                        else:
                            st.write("⚠️ No data found for the given query.")

                    st.session_state.chat_history.append(AIMessage(content="✅ Query executed successfully."))

                except Exception as e:
                    st.error(f"❌ Error executing SQL query: {e}")
            else:
                st.error("❌ Failed to generate SQL query.")
