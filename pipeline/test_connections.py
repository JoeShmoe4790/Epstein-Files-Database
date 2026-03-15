import anthropic
import pyodbc
from config import ANTHROPIC_API_KEY, DB_CONNECTION

# Test Claude API
print("Testing Claude API...")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say 'API connection successful' and nothing else."}]
)
print(message.content[0].text)

# Test SQL Server
print("\nTesting SQL Server...")
conn = pyodbc.connect(DB_CONNECTION)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sys.databases WHERE name = 'EpsteinFiles'")
row = cursor.fetchone()
print(f"Database found: {row[0]}")
conn.close()

print("\nAll connections working!")
