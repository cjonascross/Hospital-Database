#These are the classes for the database with the getter and setter functions 
class Patient:
    def __init__(self, Patient_ID, Patient_name, Room_name, Doctor_name, Condition_name, Age, Policy_Number, Ins_company):
        self.__Patient_ID = Patient_ID
        self.__Patient_name = Patient_name
        self.__Room_name = Room_name
        self.__Doctor_name = Doctor_name
        self.__Condition_name = Condition_name
        self.__Age = Age
        self.__Policy_number = Policy_Number
        self.__ Ins_company

    def get_patient_id(self):
        return self.__Patient_ID
    def get_name(self):
        return self.__Patient_name
    def get_room(self):
        return self.__Room_name
    def get_doctor(self):
        return self.__Doctor_name
    def get_conditon(self):
        return self.__Condition_name
    def get_age(self):
        return self.__Age
    def get_policy(self):
        return self.__Policy_Number
    def get_insure(self):
        return self.__Ins_company
        

class Doctor:
    def __init__(self, Doctor_ID, Doctor_name, Dept_name, Salary):
        self.__Doctor_ID = Doctor_ID
        self.__Doctor_name = Doctor_name
        self.__Dept_name = Dept_name
        self.__Salary = Salary
 
    @property
    def Doctor_ID(self):
        return self.__Doctor_ID
 
    @Doctor_ID.setter
    def Doctor_ID(self, value):
        self.__Doctor_ID = value
 
    @property
    def Doctor_name(self):
        return self.__Doctor_name
 
    @Doctor_name.setter
    def Doctor_name(self, value):
        self.__Doctor_name = value
 
    @property
    def Dept_name(self):
        return self.__Dept_name
 
    @Dept_name.setter
    def Dept_name(self, value):
        self.__Dept_name = value
 
    @property
    def Salary(self):
        return self.__Salary
 
    @Salary.setter
    def Salary(self, value):
        self.__Salary = value
 
 
class Room:
    def __init__(self, Room_name, Dept_name):
        self.__Room_name = Room_name
        self.__Dept_name = Dept_name
 
    @property
    def Room_name(self):
        return self.__Room_name
 
    @Room_name.setter
    def Room_name(self, value):
        self.__Room_name = value
 
    @property
    def Dept_name(self):
        return self.__Dept_name
 
    @Dept_name.setter
    def Dept_name(self, value):
        self.__Dept_name = value
 
 
class Condition:
    def __init__(self, Condition_name, Symptom, Dept_name):
        self.__Condition_name = Condition_name
        self.__Symptom = Symptom
        self.__Dept_name = Dept_name
 
    @property
    def Condition_name(self):
        return self.__Condition_name
 
    @Condition_name.setter
    def Condition_name(self, value):
        self.__Condition_name = value
 
    @property
    def Symptom(self):
        return self.__Symptom
 
    @Symptom.setter
    def Symptom(self, value):
        self.__Symptom = value
 
    @property
    def Dept_name(self):
        return self.__Dept_name
 
    @Dept_name.setter
    def Dept_name(self, value):
        self.__Dept_name = value
 
 
class Medicine:
    def __init__(self, Medicine_name, Symptom, Condition_name):
        self.__Medicine_name = Medicine_name
        self.__Symptom = Symptom
        self.__Condition_name = Condition_name
 
    @property
    def Medicine_name(self):
        return self.__Medicine_name
 
    @Medicine_name.setter
    def Medicine_name(self, value):
        self.__Medicine_name = value
 
    @property
    def Symptom(self):
        return self.__Symptom
 
    @Symptom.setter
    def Symptom(self, value):
        self.__Symptom = value
 
    @property
    def Condition_name(self):
        return self.__Condition_name
 
    @Condition_name.setter
    def Condition_name(self, value):
        self.__Condition_name = value
 
 
class Bill:
    def __init__(self, Bill_ID, Patient_ID, Total_cost, Paid):
        self.__Bill_ID = Bill_ID
        self.__Patient_ID = Patient_ID
        self.__Total_cost = Total_cost
        self.__Paid = Paid
 
    @property
    def Bill_ID(self):
        return self.__Bill_ID
 
    @Bill_ID.setter
    def Bill_ID(self, value):
        self.__Bill_ID = value
 
    @property
    def Patient_ID(self):
        return self.__Patient_ID
 
    @Patient_ID.setter
    def Patient_ID(self, value):
        self.__Patient_ID = value
 
    @property
    def Total_cost(self):
        return self.__Total_cost
 
    @Total_cost.setter
    def Total_cost(self, value):
        self.__Total_cost = value
 
    @property
    def Paid(self):
        return self.__Paid
 
    @Paid.setter
    def Paid(self, value):
        self.__Paid = value
 
 
class Inventory:
    def __init__(self, Inventory_ID, Inventory_name, Room_name, Medicine_name):
        self.__Inventory_ID = Inventory_ID
        self.__Inventory_name = Inventory_name
        self.__Room_name = Room_name
        self.__Medicine_name = Medicine_name
 
    @property
    def Inventory_ID(self):
        return self.__Inventory_ID
 
    @Inventory_ID.setter
    def Inventory_ID(self, value):
        self.__Inventory_ID = value
 
    @property
    def Inventory_name(self):
        return self.__Inventory_name
 
    @Inventory_name.setter
    def Inventory_name(self, value):
        self.__Inventory_name = value
 
    @property
    def Room_name(self):
        return self.__Room_name
 
    @Room_name.setter
    def Room_name(self, value):
        self.__Room_name = value
 
    @property
    def Medicine_name(self):
        return self.__Medicine_name
 
    @Medicine_name.setter
    def Medicine_name(self, value):
        self.__Medicine_name = value
 
 
class Plan:
    def __init__(self, Company, Plan, In_network, Deductable):
        self.__Company = Company
        self.__Plan = Plan
        self.__In_network = In_network
        self.__Deductable = Deductable
 
    @property
    def Company(self):
        return self.__Company
 
    @Company.setter
    def Company(self, value):
        self.__Company = value
 
    @property
    def Plan(self):
        return self.__Plan
 
    @Plan.setter
    def Plan(self, value):
        self.__Plan = value
 
    @property
    def In_network(self):
        return self.__In_network
 
    @In_network.setter
    def In_network(self, value):
        self.__In_network = value
 
    @property
    def Deductable(self):
        return self.__Deductable
 
    @Deductable.setter
    def Deductable(self, value):
        self.__Deductable = value
 
 
class Policy:
    def __init__(self, Policy_Number, Company, Plan, In_network, Deductable):
        self.__Policy_Number = Policy_Number
        self.__Company = Company
        self.__Plan = Plan
        self.__In_network = In_network
        self.__Deductable = Deductable
 
    @property
    def Policy_Number(self):
        return self.__Policy_Number
 
    @Policy_Number.setter
    def Policy_Number(self, value):
        self.__Policy_Number = value
 
    @property
    def Company(self):
        return self.__Company
 
    @Company.setter
    def Company(self, value):
        self.__Company = value
 
    @property
    def Plan(self):
        return self.__Plan
 
    @Plan.setter
    def Plan(self, value):
        self.__Plan = value
 
    @property
    def In_network(self):
        return self.__In_network
 
    @In_network.setter
    def In_network(self, value):
        self.__In_network = value
 
    @property
    def Deductable(self):
        return self.__Deductable
 
    @Deductable.setter
    def Deductable(self, value):
        self.__Deductable = value