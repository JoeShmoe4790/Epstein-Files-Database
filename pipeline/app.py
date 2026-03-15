import streamlit as st
import anthropic
import pyodbc
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(__file__))
from config import ANTHROPIC_API_KEY, DB_CONNECTION

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SCHEMA = """
Tables and sample data:
- People (PersonID, FirstName, LastName, Occupation, Status, Notes)
  Example: PersonID=54, FirstName='Alan', LastName='Dershowitz', Occupation='legal'
- Connections (ConnectionID, Person1ID, Person2ID, ConnectionType, Notes)
  ConnectionType values: 'traveled_with', 'associated_with', 'friend', 'business_partner'
- FlightLogs (FlightID, FlightDate, PersonID, Notes)
  Notes contains travel partner info

Rules:
- Always filter out names starting with '(' or '*' using: FirstName NOT LIKE '(%' AND FirstName NOT LIKE '*%'
- Always use TOP 20 unless specified otherwise
- Keep queries simple - avoid complex subqueries
- For name searches use LIKE '%name%'
"""

PRESET_QUERIES = {
    "Most connected people": """
        SELECT TOP 20 p.FirstName, p.LastName, p.Occupation, COUNT(*) AS Connections
        FROM Connections c
        JOIN People p ON p.PersonID = c.Person1ID
        WHERE p.FirstName NOT LIKE '(%' AND p.FirstName NOT LIKE '*%'
        GROUP BY p.FirstName, p.LastName, p.Occupation
        ORDER BY Connections DESC
    """,
    "Most flights logged": """
        SELECT TOP 20 p.FirstName, p.LastName, COUNT(*) AS Flights
        FROM FlightLogs f
        JOIN People p ON p.PersonID = f.PersonID
        WHERE p.FirstName NOT LIKE '(%' AND p.FirstName NOT LIKE '*%'
        GROUP BY p.FirstName, p.LastName
        ORDER BY Flights DESC
    """,
    "People by category": """
        SELECT Occupation, COUNT(*) AS Total
        FROM People
        WHERE Occupation IS NOT NULL
        AND FirstName NOT LIKE '(%' AND FirstName NOT LIKE '*%'
        GROUP BY Occupation
        ORDER BY Total DESC
    """,
    "All legal figures": """
        SELECT TOP 20 FirstName, LastName, Occupation, Notes
        FROM People
        WHERE Occupation = 'legal'
        AND FirstName NOT LIKE '(%' AND FirstName NOT LIKE '*%'
        ORDER BY LastName
    """,
    "All political figures": """
        SELECT TOP 20 FirstName, LastName, Occupation, Notes
        FROM People
        WHERE Occupation = 'political'
        AND FirstName NOT LIKE '(%' AND FirstName NOT LIKE '*%'
        ORDER BY LastName
    """,
    "Most recent flights": """
        SELECT TOP 20 p.FirstName, p.LastName, f.FlightDate, f.Notes
        FROM FlightLogs f
        JOIN People p ON p.PersonID = f.PersonID
        WHERE p.FirstName NOT LIKE '(%' AND p.FirstName NOT LIKE '*%'
        ORDER BY f.FlightDate DESC
    """
}

def run_query(sql):
    conn = pyodbc.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    conn.close()
    return cols, rows

def ask(question):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are a SQL Server expert. Given this schema:
{SCHEMA}
Convert this question to a simple SQL Server query. Return ONLY the SQL, no backticks, no explanation.
Always filter out redacted names (starting with '(' or '*').
Always use TOP 20 unless the user specifies a number.
Question: {question}"""
        }]
    )
    
    sql = response.content[0].text.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def display_results(sql):
    try:
        cols, rows = run_query(sql)
        if rows:
            df = pd.DataFrame([list(row) for row in rows], columns=cols)
            st.dataframe(df, use_container_width=True)
            
            summary = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"Summarize these results in 2-3 sentences:\n{df.head(10).to_string()}"
                }]
            )
            st.markdown(summary.content[0].text)
        else:
            st.warning("No results found.")
        st.code(sql, language="sql")
    except Exception as e:
        st.error(f"Query error: {e}")
        st.code(sql, language="sql")

# UI
st.title("Epstein Files Database")
st.caption("Built from DOJ EFTA release — 1,614 people, 2,302 connections, 1,449 flight records")

tab1, tab2 = st.tabs(["Quick Queries", "Ask a Question"])

with tab1:
    st.subheader("Preset Queries")
    cols = st.columns(3)
    buttons = list(PRESET_QUERIES.keys())
    
    for i, label in enumerate(buttons):
        if cols[i % 3].button(label, use_container_width=True):
            st.session_state.preset = label

    if "preset" in st.session_state:
        st.markdown(f"### {st.session_state.preset}")
        display_results(PRESET_QUERIES[st.session_state.preset])

with tab2:
    st.subheader("Ask in Plain English")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "df" in message:
                st.dataframe(message["df"], use_container_width=True)

    if prompt := st.chat_input("e.g. who is connected to Alan Dershowitz?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Querying..."):
                sql = ask(prompt)
                st.code(sql, language="sql")
                try:
                    cols, rows = run_query(sql)
                    if rows:
                        df = pd.DataFrame([list(row) for row in rows], columns=cols)
                        st.dataframe(df, use_container_width=True)
                        summary = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=300,
                            messages=[{"role": "user", "content": f"Summarize in 2-3 sentences:\n{df.head(10).to_string()}"}]
                        )
                        answer = summary.content[0].text
                        st.markdown(answer)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "df": df
                        })
                    else:
                        st.warning("No results found.")
                except Exception as e:
                    st.error(f"Error: {e}")