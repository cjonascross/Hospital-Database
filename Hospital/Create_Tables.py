
import mysql.connector

# Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="coursework"
)

mycursor = mydb.cursor()

# Select database
mycursor.execute("CREATE DATABASE IF NOT EXISTS hospital_db")
mycursor.execute("USE hospital_db")

# 1. Doctor
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Doctor (
    Doctor_ID INT PRIMARY KEY,
    Doctor_Name VARCHAR(25),
    Dept_Name VARCHAR(25),
    Salary DECIMAL(10,2)
)
""")

# 2. Room
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Room (
    Room_Name VARCHAR(25) PRIMARY KEY,
    Dept_Name VARCHAR(25)
)
""")

# 3. Conditions
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Conditions (
    Condition_Name VARCHAR(25) PRIMARY KEY,
    Symptom VARCHAR(50),
    Dept_Name VARCHAR(25)
)
""")

# 4. Plans
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Plans (
    Ins_Company VARCHAR(25),
    Plan VARCHAR(25),
    In_Network BOOLEAN,
    Deductible DECIMAL(10,2),
    PRIMARY KEY (Ins_Company, Plan)
)
""")

# 5. Medicine
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Medicine (
    Medicine_Name VARCHAR(25) PRIMARY KEY,
    Symptom VARCHAR(50),
    Condition_Name VARCHAR(25),
    FOREIGN KEY (Condition_Name)
        REFERENCES Conditions(Condition_Name)
        ON DELETE SET NULL
)
""")

# 6. Patient
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Patient (
    Patient_ID INT PRIMARY KEY,
    Patient_Name VARCHAR(25),
    Age INT,
    Room_Name VARCHAR(25),
    Doctor_ID INT,
    Condition_Name VARCHAR(25),
    Policy_Num BIGINT,
    Ins_Company VARCHAR(25),

    FOREIGN KEY (Room_Name)
        REFERENCES Room(Room_Name)
        ON DELETE SET NULL,

    FOREIGN KEY (Doctor_ID)
        REFERENCES Doctor(Doctor_ID)
        ON DELETE SET NULL,

    FOREIGN KEY (Condition_Name)
        REFERENCES Conditions(Condition_Name)
        ON DELETE SET NULL
)
""")

# 7. Policy
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Policy (
    Policy_Num BIGINT PRIMARY KEY,
    Ins_Company VARCHAR(25),
    Plan VARCHAR(25),
    In_Network BOOLEAN,
    Patient_ID INT,
    Deductible DECIMAL(10,2),

    FOREIGN KEY (Patient_ID)
        REFERENCES Patient(Patient_ID)
        ON DELETE SET NULL,

    FOREIGN KEY (Ins_Company, Plan)
        REFERENCES Plans(Ins_Company, Plan)
        ON DELETE SET NULL
)
""")

# 8. Bill
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Bill (
    Bill_ID INT PRIMARY KEY,
    Patient_ID INT,
    Total_Cost DECIMAL(10,2),
    Paid DECIMAL(10,2),

    FOREIGN KEY (Patient_ID)
        REFERENCES Patient(Patient_ID)
)
""")

# 9. Inventory
mycursor.execute("""
CREATE TABLE IF NOT EXISTS Inventory (
    Inventory_ID INT PRIMARY KEY,
    Inventory_Name VARCHAR(30),
    Room_Name VARCHAR(25),
    Medicine_Name VARCHAR(25),
    Cost DECIMAL(10,2),

    FOREIGN KEY (Room_Name)
        REFERENCES Room(Room_Name)
        ON DELETE SET NULL,

    FOREIGN KEY (Medicine_Name)
        REFERENCES Medicine(Medicine_Name)
        ON DELETE SET NULL
)
""")

# Connect Patient to Policy
mycursor.execute("""
ALTER TABLE Patient
ADD CONSTRAINT fk_patient_policy
FOREIGN KEY (Policy_Num)
REFERENCES Policy(Policy_Num)
ON DELETE SET NULL
""")

mydb.commit()

# Display created tables
mycursor.execute("SHOW TABLES")

print("Hospital database tables:")

for table in mycursor.fetchall():
    print(table[0])

print("All 9 tables created successfully!")

mycursor.close()
mydb.close()
