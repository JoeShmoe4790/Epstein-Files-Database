-- =============================================
-- Epstein Files Database
-- Author: Daniel Shabo
-- Date: March 2026
-- Description: SQL practice project modeling
-- public figure connections and events
-- =============================================

USE EpsteinFiles;

-- People Table
CREATE TABLE People (
    PersonID INT IDENTITY(1,1) PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Nationality VARCHAR(50),
    Occupation VARCHAR(100),
    Status VARCHAR(20),
    DateOfBirth DATE,
    Notes TEXT
);

-- Locations Table
CREATE TABLE Locations (
    LocationID INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(50),
    Country VARCHAR(50),
    State VARCHAR(50),
    Description TEXT
);

-- Connections Table
CREATE TABLE Connections (
    ConnectionID INT IDENTITY(1,1) PRIMARY KEY,
    Person1ID INT FOREIGN KEY REFERENCES People(PersonID),
    Person2ID INT FOREIGN KEY REFERENCES People(PersonID),
    ConnectionType VARCHAR(100),
    DateEstablished DATE,
    Notes TEXT
);

-- Events Table
CREATE TABLE Events (
    EventID INT IDENTITY(1,1) PRIMARY KEY,
    EventDate DATE,
    LocationID INT FOREIGN KEY REFERENCES Locations(LocationID),
    EventType VARCHAR(100),
    Description TEXT
);

-- Event Participants Table
CREATE TABLE EventParticipants (
    ParticipantID INT IDENTITY(1,1) PRIMARY KEY,
    EventID INT FOREIGN KEY REFERENCES Events(EventID),
    PersonID INT FOREIGN KEY REFERENCES People(PersonID),
    Role VARCHAR(100),
    Notes TEXT
);

-- Flight Logs Table
CREATE TABLE FlightLogs (
    FlightID INT IDENTITY(1,1) PRIMARY KEY,
    FlightDate DATE,
    DepartureLocation VARCHAR(100),
    ArrivalLocation VARCHAR(100),
    PersonID INT FOREIGN KEY REFERENCES People(PersonID),
    Notes TEXT
);
SELECT TOP 10 * FROM People;