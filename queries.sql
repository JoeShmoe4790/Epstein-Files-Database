USE EpsteinFiles;

-- Most connected people
SELECT p.FirstName, p.LastName, p.Occupation, COUNT(*) AS TotalConnections
FROM Connections c
JOIN People p ON p.PersonID = c.Person1ID
GROUP BY p.FirstName, p.LastName, p.Occupation
ORDER BY TotalConnections DESC;

-- Find all connections for a specific person
SELECT 
    p1.FirstName + ' ' + p1.LastName AS Person1,
    p2.FirstName + ' ' + p2.LastName AS Person2,
    c.ConnectionType,
    c.Notes
FROM Connections c
JOIN People p ON p.PersonID = c.Person1ID
JOIN People p1 ON p1.PersonID = c.Person1ID
JOIN People p2 ON p2.PersonID = c.Person2ID
WHERE p1.LastName = 'Dershowitz'
   OR p2.LastName = 'Dershowitz';

-- Count connections by type
SELECT ConnectionType, COUNT(*) AS Total
FROM Connections
GROUP BY ConnectionType
ORDER BY Total DESC;

-- People by category
SELECT Occupation, COUNT(*) AS Total
FROM People
WHERE Occupation IS NOT NULL
GROUP BY Occupation
ORDER BY Total DESC;