import anthropic
import pyodbc
from config import ANTHROPIC_API_KEY, DB_CONNECTION

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
conn = pyodbc.connect(DB_CONNECTION)
cursor = conn.cursor()

SCHEMA = """
Tables:
- People (PersonID, FirstName, LastName, Nationality, Occupation, Status, DateOfBirth, Notes)
- Connections (ConnectionID, Person1ID, Person2ID, ConnectionType, Notes)
- Locations (LocationID, Name, Type, Country, State, Description)
- Events (EventID, EventDate, LocationID, EventType, Description)
- EventParticipants (ParticipantID, EventID, PersonID, Role, Notes)
- FlightLogs (FlightID, FlightDate, DepartureLocation, ArrivalLocation, PersonID, Notes)
"""

def ask(question):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are a SQL expert. Given this schema:
{SCHEMA}
Convert this question to a single SQL Server query. Return ONLY the SQL, nothing else.
Question: {question}"""
        }]
    )
    
    sql = response.content[0].text.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    print(f"\nSQL: {sql}\n")
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        
        result = "\n".join([str(dict(zip(cols, row))) for row in rows[:10]])
        
        summary = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"Summarize these database results in plain English:\n{result}"
            }]
        )
        print("Answer:", summary.content[0].text)
    except Exception as e:
        print(f"Error: {e}")

print("Epstein Files Database Chat")
print("Type your question or 'quit' to exit\n")

while True:
    question = input("You: ")
    if question.lower() == 'quit':
        break
    ask(question)