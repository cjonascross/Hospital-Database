#We are importing all the info from the DB file 
from Hospital_DB import Patient
from Hospital_DB import Doctor
from Hospital_DB import Room
from Hospital_DB import Condition 
from Hospital_DB import Medicine 
from Hospital_DB import Bill
from Hospital_DB import Inventory
from Hospital_DB import Plan
from Hospital_DB import Policy

#This file has its own Hospital class for the data 
class Hospital:
    def __init__(self):
        self.__patients = []
        self.__next_patient_id = 1
        self.__inventory = []             
        self.__next_inventory_id = 1      
        self.__bills = []

def patients(self):
        return self.__patients

  def inventory(self):
        return self.__inventory

#These are functions for the database from the Python side connecting to the GUI

def add_patient(self, Patient_name, Condition_name, Age, Policy_Number, Ins_company):
    def add_patient(self, Patient_name, Condition_name, Age, Policy_Number, Ins_company):
        # Basic validation for input 
        if not Patient_name:
            raise ValueError("Patient name is required.")
        if not isinstance(Age, int) or Age < 0:
            raise ValueError("Age must be a non-negative integer.")
        patient = Patient(self.__next_patient_id, Patient_name, Condition_name, Age, Policy_Number, Ins_company):
        self.__patients.append(patient)
        self.__next_patient_id += 1
        return patient

def add_inventory(self, Inventory_name, Room_name, Medicine_name):
    if not Inventory_name:
            raise ValueError("Inventory name is required.")

        item = Inventory(self.__next_inventory_id, Inventory_name,
                         Room_name, Medicine_name)
        self.__inventory.append(item)
        self.__next_inventory_id += 1
        return item


def add_payment(self, Bill_ID, Total_cost):
        # Find the bill
        bill = next((b for b in self.__bills if b.Bill_ID == Bill_ID), None)
        if bill is None:
            raise ValueError(f"No bill found with ID {Bill_ID}.")

        payment_amount = round(Total_cost * .10, 2)   # 10% upfront

        bill.Paid = bill.Paid + payment_amount
        balance = round(bill.Total_cost - bill.Paid, 2)
        return payment_amount, balance
