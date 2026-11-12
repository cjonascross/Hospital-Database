
import mysql.connector

# Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="coursework",
    database="hospital_db"
)

mycursor = mydb.cursor()

# --------------------------------
# 1. DOCTOR DATA
# --------------------------------

doctors = [
    (1, "Dr. Smith", "Emergency", 100000),
    (2, "Dr. Johnson", "Cardiology", 150000),
    (3, "Dr. Williams", "Neurology", 145000),
    (4, "Dr. Brown", "Pediatrics", 120000),
    (5, "Dr. Davis", "Orthopedics", 140000),
    (6, "Dr. Miller", "Dermatology", 130000),
    (7, "Dr. Wilson", "Oncology", 160000),
    (8, "Dr. Moore", "General Medicine", 125000),
    (9, "Dr. Taylor", "Pulmonology", 138000),
    (10, "Dr. Anderson", "Gastroenterology", 142000),
    (11, "Dr. Thomas", "Emergency", 110000),
    (12, "Dr. Jackson", "Cardiology", 155000)
]

mycursor.executemany("""
INSERT IGNORE INTO Doctor
(Doctor_ID, Doctor_Name, Dept_Name, Salary)
VALUES (%s, %s, %s, %s)
""", doctors)


# --------------------------------
# 2. ROOM DATA
# --------------------------------

rooms = [
    ("ER-101", "Emergency"),
    ("ER-102", "Emergency"),
    ("CAR-201", "Cardiology"),
    ("CAR-202", "Cardiology"),
    ("NEU-301", "Neurology"),
    ("PED-401", "Pediatrics"),
    ("ORT-501", "Orthopedics"),
    ("DER-601", "Dermatology"),
    ("ONC-701", "Oncology"),
    ("GEN-801", "General Medicine"),
    ("PUL-901", "Pulmonology"),
    ("GAS-1001", "Gastroenterology")
]

mycursor.executemany("""
INSERT IGNORE INTO Room
(Room_Name, Dept_Name)
VALUES (%s, %s)
""", rooms)


# --------------------------------
# 3. CONDITION DATA
# --------------------------------

conditions = [
    ("Flu", "Runny nose and fever", "General Medicine"),
    ("Diabetes", "High blood sugar", "General Medicine"),
    ("Hypertension", "High blood pressure", "Cardiology"),
    ("Asthma", "Shortness of breath", "Pulmonology"),
    ("Migraine", "Severe headaches", "Neurology"),
    ("Pneumonia", "Cough and chest pain", "Pulmonology"),
    ("Fracture", "Broken bone and pain", "Orthopedics"),
    ("Allergies", "Sneezing and itching", "Dermatology"),
    ("Anemia", "Fatigue and weakness", "General Medicine"),
    ("Gastroenteritis", "Stomach pain and nausea", "Gastroenterology"),
    ("Heart Disease", "Chest pain and fatigue", "Cardiology"),
    ("Skin Infection", "Redness and swelling", "Dermatology")
]

mycursor.executemany("""
INSERT IGNORE INTO Conditions
(Condition_Name, Symptom, Dept_Name)
VALUES (%s, %s, %s)
""", conditions)


# --------------------------------
# 4. PLANS DATA
# --------------------------------

plans = [
    ("BCBS", "Full Coverage", True, 400),
    ("BCBS", "Basic Coverage", True, 1000),
    ("Aetna", "Premium", True, 500),
    ("Aetna", "Standard", False, 1500),
    ("Cigna", "Gold Plan", True, 600),
    ("Cigna", "Silver Plan", False, 1200),
    ("UnitedHealth", "Complete", True, 300),
    ("UnitedHealth", "Essential", False, 1800),
    ("Humana", "Premium Care", True, 700),
    ("Humana", "Basic Care", False, 2000),
    ("Kaiser", "HMO Plus", True, 500),
    ("Kaiser", "HMO Basic", True, 1000)
]

mycursor.executemany("""
INSERT IGNORE INTO Plans
(Ins_Company, Plan, In_Network, Deductible)
VALUES (%s, %s, %s, %s)
""", plans)


# --------------------------------
# 5. MEDICINE DATA
# --------------------------------

medicines = [
    ("Tamiflu", "Flu symptoms", "Flu"),
    ("Metformin", "Blood sugar control", "Diabetes"),
    ("Lisinopril", "Blood pressure", "Hypertension"),
    ("Albuterol", "Breathing problems", "Asthma"),
    ("Sumatriptan", "Headaches", "Migraine"),
    ("Amoxicillin", "Bacterial infection", "Pneumonia"),
    ("Ibuprofen", "Pain and inflammation", "Fracture"),
    ("Cetirizine", "Allergy symptoms", "Allergies"),
    ("Ferrous Sulfate", "Iron deficiency", "Anemia"),
    ("Ondansetron", "Nausea", "Gastroenteritis"),
    ("Atorvastatin", "Cholesterol control", "Heart Disease"),
    ("Cephalexin", "Skin infection", "Skin Infection")
]

mycursor.executemany("""
INSERT IGNORE INTO Medicine
(Medicine_Name, Symptom, Condition_Name)
VALUES (%s, %s, %s)
""", medicines)


# --------------------------------
# 6. PATIENT DATA
# --------------------------------
# Policy_Num starts as NULL because
# policies are created after patients.

patients = [
    (1, "Steve Smith", 30, "GEN-801", 8, "Flu", None, None),
    (2, "Sarah Miller", 45, "CAR-201", 2, "Hypertension", None, None),
    (3, "James Wilson", 52, "GEN-801", 8, "Diabetes", None, None),
    (4, "Emily Davis", 12, "PED-401", 4, "Asthma", None, None),
    (5, "Michael Brown", 38, "NEU-301", 3, "Migraine", None, None),
    (6, "Jessica Taylor", 67, "PUL-901", 9, "Pneumonia", None, None),
    (7, "David Anderson", 29, "ORT-501", 5, "Fracture", None, None),
    (8, "Ashley Thomas", 24, "DER-601", 6, "Allergies", None, None),
    (9, "Robert Jackson", 58, "GEN-801", 8, "Anemia", None, None),
    (10, "Olivia White", 33, "GAS-1001", 10, "Gastroenteritis", None, None),
    (11, "Daniel Harris", 61, "CAR-202", 12, "Heart Disease", None, None),
    (12, "Sophia Martin", 41, "DER-601", 6, "Skin Infection", None, None)
]

mycursor.executemany("""
INSERT IGNORE INTO Patient
(Patient_ID, Patient_Name, Age, Room_Name,
 Doctor_ID, Condition_Name, Policy_Num, Ins_Company)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", patients)


# --------------------------------
# 7. POLICY DATA
# --------------------------------

policies = [
    (1001, "BCBS", "Full Coverage", True, 1, 400),
    (1002, "BCBS", "Basic Coverage", True, 2, 1000),
    (1003, "Aetna", "Premium", True, 3, 500),
    (1004, "Aetna", "Standard", False, 4, 1500),
    (1005, "Cigna", "Gold Plan", True, 5, 600),
    (1006, "Cigna", "Silver Plan", False, 6, 1200),
    (1007, "UnitedHealth", "Complete", True, 7, 300),
    (1008, "UnitedHealth", "Essential", False, 8, 1800),
    (1009, "Humana", "Premium Care", True, 9, 700),
    (1010, "Humana", "Basic Care", False, 10, 2000),
    (1011, "Kaiser", "HMO Plus", True, 11, 500),
    (1012, "Kaiser", "HMO Basic", True, 12, 1000)
]

mycursor.executemany("""
INSERT IGNORE INTO Policy
(Policy_Num, Ins_Company, Plan, In_Network,
 Patient_ID, Deductible)
VALUES (%s, %s, %s, %s, %s, %s)
""", policies)


# Update each patient with their policy number
# and insurance company.

for policy in policies:
    mycursor.execute("""
    UPDATE Patient
    SET Policy_Num = %s, Ins_Company = %s
    WHERE Patient_ID = %s
    """, (policy[0], policy[1], policy[4]))


# --------------------------------
# 8. BILL DATA
# --------------------------------

bills = [
    (1, 1, 500, 100),
    (2, 2, 2500, 500),
    (3, 3, 1800, 900),
    (4, 4, 750, 250),
    (5, 5, 1200, 600),
    (6, 6, 5000, 1500),
    (7, 7, 3200, 1000),
    (8, 8, 450, 200),
    (9, 9, 900, 300),
    (10, 10, 650, 150),
    (11, 11, 7500, 2500),
    (12, 12, 1100, 500)
]

mycursor.executemany("""
INSERT IGNORE INTO Bill
(Bill_ID, Patient_ID, Total_Cost, Paid)
VALUES (%s, %s, %s, %s)
""", bills)


# --------------------------------
# 9. INVENTORY DATA
# --------------------------------

inventory = [
    (1, "Flu Shot Supplies", "GEN-801", "Tamiflu", 100),
    (2, "Diabetes Medication", "GEN-801", "Metformin", 80),
    (3, "Blood Pressure Medicine", "CAR-201", "Lisinopril", 60),
    (4, "Inhalers", "PUL-901", "Albuterol", 150),
    (5, "Migraine Medication", "NEU-301", "Sumatriptan", 90),
    (6, "Antibiotics", "PUL-901", "Amoxicillin", 75),
    (7, "Pain Medication", "ORT-501", "Ibuprofen", 40),
    (8, "Allergy Medicine", "DER-601", "Cetirizine", 55),
    (9, "Iron Supplements", "GEN-801", "Ferrous Sulfate", 35),
    (10, "Nausea Medication", "GAS-1001", "Ondansetron", 65),
    (11, "Heart Medication", "CAR-202", "Atorvastatin", 110),
    (12, "Skin Infection Medicine", "DER-601", "Cephalexin", 85)
]

mycursor.executemany("""
INSERT IGNORE INTO Inventory
(Inventory_ID, Inventory_Name, Room_Name,
 Medicine_Name, Cost)
VALUES (%s, %s, %s, %s, %s)
""", inventory)


# --------------------------------
# SAVE AND CLOSE
# --------------------------------

mydb.commit()

print("Successfully inserted hospital sample data!")

# Show number of records in every table
tables = [
    "Doctor", "Patient", "Room", "Conditions",
    "Medicine", "Bill", "Inventory", "Policy", "Plans"
]

for table in tables:
    mycursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = mycursor.fetchone()[0]
    print(table, ":", count, "records")

mycursor.close()
mydb.close()
