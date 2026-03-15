import json
import pyodbc
import sys
import os

sys.path.append(os.path.dirname(__file__))
from config import DB_CONNECTION

conn = pyodbc.connect(DB_CONNECTION)
cursor = conn.cursor()

# Load persons registry
with open('../Epstein-research-data/persons_registry.json', encoding='utf-8') as f:
    persons = json.load(f)

print(f"Importing {len(persons)} people...")

for p in persons:
    name = p.get('name', '')
    if not name or name.startswith('(b)'):
        continue
    parts = name.split(' ', 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else ''
    category = p.get('category', '')
    cursor.execute("""
        INSERT INTO People (FirstName, LastName, Occupation, Notes)
        VALUES (?, ?, ?, ?)
    """, first, last, category, str(p.get('sources', '')))

conn.commit()
print("People imported successfully")
conn.close()
# Load relationships
conn2 = pyodbc.connect(DB_CONNECTION)
cursor2 = conn2.cursor()

with open('../Epstein-research-data/knowledge_graph_relationships.json', encoding='utf-8') as f:
    relationships = json.load(f)

print(f"Importing {len(relationships)} relationships...")

for r in relationships:
    cursor2.execute("""
        INSERT INTO Connections (Person1ID, Person2ID, ConnectionType, Notes)
        VALUES (?, ?, ?, ?)
    """, 
    r.get('source_entity_id'),
    r.get('target_entity_id'),
    r.get('relationship_type'),
    str(r.get('metadata', ''))[:500]
    )

conn2.commit()
print("Relationships imported successfully")
conn2.close()