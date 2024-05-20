CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'Qq12345';

CREATE TABLE PhoneNumbers (
    ID SERIAL PRIMARY KEY,
    PhoneNumber VARCHAR(32)
);

CREATE TABLE Emails (
    ID SERIAL PRIMARY KEY,
    Email VARCHAR(100)
);

INSERT INTO PhoneNumbers (PhoneNumber) VALUES
('89995556235'),
('83476378633'),
('89161606677');

INSERT INTO Emails (Email) VALUES
('yav@edu.ru'),
('123@bim.bam.com'),
('biba@boba.ru');