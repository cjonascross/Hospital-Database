
import hmac
import sys
from decimal import ROUND_HALF_UP, Decimal

import mysql.connector
from mysql.connector import Error as MySQLError
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "coursework",
    "database": "hospital_db",
}

# Login required when the program starts
LOGIN_USERNAME = "Hospital"
LOGIN_PASSWORD = "password"
MAX_LOGIN_ATTEMPTS = 3


PEDIATRIC_AGE_LIMIT = 18   


class NoFacilitiesError(ValueError):
    """Raised when no compatible doctor/room exists for a new patient."""

    def __init__(self):
        super().__init__("Proper Facilities not available. Try again later")


class HospitalDB:

    def __init__(self, config):
        self.__conn = mysql.connector.connect(**config, autocommit=True)

    def close(self):
        if self.__conn.is_connected():
            self.__conn.close()

    def __query(self, sql, params=()):
        cursor = self.__conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()

    def __execute(self, sql, params=()):
        cursor = self.__conn.cursor()
        try:
            cursor.execute(sql, params)
            self.__conn.commit()
        except MySQLError:
            self.__conn.rollback()
            raise
        finally:
            cursor.close()

    def __transaction(self, statements):
        """Run several (sql, params) statements as one transaction.
        Returns the number of rows affected by the last statement."""
        cursor = self.__conn.cursor()
        try:
            self.__conn.start_transaction()
            for sql, params in statements:
                cursor.execute(sql, params)
            self.__conn.commit()
            return cursor.rowcount
        except MySQLError:
            self.__conn.rollback()
            raise
        finally:
            cursor.close()

    def __next_id(self, table, column):
        return self.__query(f"SELECT COALESCE(MAX({column}), 0) + 1 FROM {table}")[0][0]

    def rooms(self):
        return [r[0] for r in self.__query("SELECT Room_Name FROM Room ORDER BY Room_Name")]

    def conditions(self):
        return [r[0] for r in self.__query("SELECT Condition_Name FROM Conditions ORDER BY Condition_Name")]

    def medicines(self):
        return [r[0] for r in self.__query("SELECT Medicine_Name FROM Medicine ORDER BY Medicine_Name")]

    def policies(self):
        return self.__query("SELECT Policy_Num, Ins_Company, Plan FROM Policy ORDER BY Policy_Num")

    def ins_companies(self):
        return [r[0] for r in self.__query("SELECT DISTINCT Ins_Company FROM Plans ORDER BY Ins_Company")]

    def assign_room_and_doctor(self, Condition_name, Age):
        """Pick a compatible room and doctor for a patient.

        Children (under PEDIATRIC_AGE_LIMIT) go to Pediatrics; everyone else
        goes to the department that treats their condition. Within that
        department, the doctor with the fewest patients and an empty room
        (one patient per room) are chosen. If every room is taken, or the
        department has no doctor, NoFacilitiesError is raised.
        Returns (Room_name, Doctor_ID, Doctor_name) or raises NoFacilitiesError.
        """
        if Age < PEDIATRIC_AGE_LIMIT:
            dept = "Pediatrics"
        else:
            rows = self.__query(
                "SELECT Dept_Name FROM Conditions WHERE Condition_Name = %s",
                (Condition_name,),
            )
            if not rows or not rows[0][0]:
                raise NoFacilitiesError()
            dept = rows[0][0]

        doctor = self.__query(
            """
            SELECT d.Doctor_ID, d.Doctor_Name
            FROM Doctor d
            LEFT JOIN Patient p ON p.Doctor_ID = d.Doctor_ID
            WHERE d.Dept_Name = %s
            GROUP BY d.Doctor_ID, d.Doctor_Name
            ORDER BY COUNT(p.Patient_ID), d.Doctor_ID
            LIMIT 1
            """,
            (dept,),
        )
        room = self.__query(
            """
            SELECT r.Room_Name
            FROM Room r
            WHERE r.Dept_Name = %s
              AND NOT EXISTS (SELECT 1 FROM Patient p WHERE p.Room_Name = r.Room_Name)
            ORDER BY r.Room_Name
            LIMIT 1
            """,
            (dept,),
        )
        if not doctor or not room:
            raise NoFacilitiesError()
        return room[0][0], doctor[0][0], doctor[0][1]

    def add_patient(self, Patient_name, Age, Condition_name,
                    Policy_Number, Ins_company):
        """Add a patient, automatically assigning a room and doctor.
        Returns (Patient_ID, Room_name, Doctor_name)."""
        if not Patient_name:
            raise ValueError("Patient name is required.")
        if not isinstance(Age, int) or Age < 0:
            raise ValueError("Age must be a non-negative integer.")
        if not Condition_name:
            raise ValueError("Condition is required.")

        Room_name, Doctor_ID, Doctor_name = self.assign_room_and_doctor(Condition_name, Age)

        patient_id = self.__next_id("Patient", "Patient_ID")
        self.__execute(
            """
            INSERT INTO Patient
            (Patient_ID, Patient_Name, Age, Room_Name, Doctor_ID,
             Condition_Name, Policy_Num, Ins_Company)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (patient_id, Patient_name, Age, Room_name, Doctor_ID,
             Condition_name, Policy_Number, Ins_company),
        )
        return patient_id, Room_name, Doctor_name

    def search_patients(self, text="", field="Name"):
        sql = """
            SELECT p.Patient_ID, p.Patient_Name, p.Age, p.Room_Name,
                   d.Doctor_Name, p.Condition_Name, p.Policy_Num, p.Ins_Company
            FROM Patient p
            LEFT JOIN Doctor d ON p.Doctor_ID = d.Doctor_ID
        """
        params = ()
        text = text.strip()
        if text:
            if field == "ID":
                if not text.isdigit():
                    raise ValueError("Patient ID must be a number.")
                sql += " WHERE p.Patient_ID = %s"
                params = (int(text),)
            else:
                column = {
                    "Name": "p.Patient_Name",
                    "Condition": "p.Condition_Name",
                    "Room": "p.Room_Name",
                    "Doctor": "d.Doctor_Name",
                    "Insurance": "p.Ins_Company",
                }[field]
                sql += f" WHERE {column} LIKE %s"
                params = (f"%{text}%",)
        sql += " ORDER BY p.Patient_ID"
        return self.__query(sql, params)

    def delete_patient(self, Patient_ID):
        deleted = self.__transaction([
            ("DELETE FROM Bill WHERE Patient_ID = %s", (Patient_ID,)),
            ("DELETE FROM Patient WHERE Patient_ID = %s", (Patient_ID,)),
        ])
        if deleted == 0:
            raise ValueError(f"No patient found with ID {Patient_ID}.")

    def add_inventory(self, Inventory_name, Room_name, Medicine_name, Cost):
        if not Inventory_name:
            raise ValueError("Inventory name is required.")
        if Cost < 0:
            raise ValueError("Cost cannot be negative.")
        cost = Decimal(str(Cost)).quantize(Decimal("0.01"), ROUND_HALF_UP)

        cursor = self.__conn.cursor()
        try:
            self.__conn.start_transaction()
            cursor.execute("SELECT COALESCE(MAX(Inventory_ID), 0) + 1 FROM Inventory FOR UPDATE")
            inventory_id = cursor.fetchone()[0]
            cursor.execute(
                """
                INSERT INTO Inventory
                (Inventory_ID, Inventory_Name, Room_Name, Medicine_Name, Cost)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (inventory_id, Inventory_name, Room_name, Medicine_name, cost),
            )

            patient_name = bill_id = None
            if Room_name and cost > 0:
                cursor.execute(
                    "SELECT Patient_ID, Patient_Name FROM Patient WHERE Room_Name = %s LIMIT 1",
                    (Room_name,),
                )
                patient = cursor.fetchone()
                if patient:
                    patient_id, patient_name = patient
                    cursor.execute(
                        "SELECT Bill_ID FROM Bill WHERE Patient_ID = %s "
                        "ORDER BY Bill_ID DESC LIMIT 1 FOR UPDATE",
                        (patient_id,),
                    )
                    bill = cursor.fetchone()
                    if bill:
                        bill_id = bill[0]
                        cursor.execute(
                            "UPDATE Bill SET Total_Cost = Total_Cost + %s WHERE Bill_ID = %s",
                            (cost, bill_id),
                        )
                    else:
                        cursor.execute("SELECT COALESCE(MAX(Bill_ID), 0) + 1 FROM Bill FOR UPDATE")
                        bill_id = cursor.fetchone()[0]
                        cursor.execute(
                            "INSERT INTO Bill (Bill_ID, Patient_ID, Total_Cost, Paid) "
                            "VALUES (%s, %s, %s, 0)",
                            (bill_id, patient_id, cost),
                        )
            self.__conn.commit()
        except MySQLError:
            self.__conn.rollback()
            raise
        finally:
            cursor.close()
        return inventory_id, patient_name, bill_id

    def search_inventory(self, text="", field="Name"):
        sql = "SELECT Inventory_ID, Inventory_Name, Room_Name, Medicine_Name, Cost FROM Inventory"
        params = ()
        text = text.strip()
        if text:
            if field == "ID":
                if not text.isdigit():
                    raise ValueError("Inventory ID must be a number.")
                sql += " WHERE Inventory_ID = %s"
                params = (int(text),)
            else:
                column = {
                    "Name": "Inventory_Name",
                    "Room": "Room_Name",
                    "Medicine": "Medicine_Name",
                }[field]
                sql += f" WHERE {column} LIKE %s"
                params = (f"%{text}%",)
        sql += " ORDER BY Inventory_ID"
        return self.__query(sql, params)

    def delete_inventory(self, Inventory_ID):
        deleted = self.__transaction([
            ("DELETE FROM Inventory WHERE Inventory_ID = %s", (Inventory_ID,)),
        ])
        if deleted == 0:
            raise ValueError(f"No inventory item found with ID {Inventory_ID}.")

    def search_bills(self, text="", field="Patient"):
        sql = """
            SELECT b.Bill_ID, b.Patient_ID, p.Patient_Name,
                   b.Total_Cost, b.Paid, b.Total_Cost - b.Paid AS Balance
            FROM Bill b
            LEFT JOIN Patient p ON b.Patient_ID = p.Patient_ID
        """
        params = ()
        text = text.strip()
        if text:
            if field in ("Bill ID", "Patient ID"):
                if not text.isdigit():
                    raise ValueError(f"{field} must be a number.")
                column = "b.Bill_ID" if field == "Bill ID" else "b.Patient_ID"
                sql += f" WHERE {column} = %s"
                params = (int(text),)
            else:
                sql += " WHERE p.Patient_Name LIKE %s"
                params = (f"%{text}%",)
        elif field == "Unpaid Only":
            sql += " WHERE b.Paid < b.Total_Cost"
        sql += " ORDER BY b.Bill_ID"
        return self.__query(sql, params)

    def get_bill(self, Bill_ID):
        """Return (Total_Cost, Paid) for a bill, or raise ValueError."""
        rows = self.__query("SELECT Total_Cost, Paid FROM Bill WHERE Bill_ID = %s", (Bill_ID,))
        if not rows:
            raise ValueError(f"No bill found with ID {Bill_ID}.")
        return rows[0]

    def add_payment(self, Bill_ID, Amount):
        """Apply a payment to a bill (MySQL version of Search.add_payment).
        Returns (payment_amount, new_balance)."""
        amount = Decimal(str(Amount)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        total, paid = self.get_bill(Bill_ID)
        balance = total - paid
        if balance <= 0:
            raise ValueError(f"Bill {Bill_ID} is already paid in full.")
        if amount > balance:
            raise ValueError(f"Payment of ${amount} is more than the "
                             f"remaining balance of ${balance}.")

        # The WHERE guard stops the bill being overpaid if it changed meanwhile
        updated = self.__transaction([(
            "UPDATE Bill SET Paid = Paid + %s WHERE Bill_ID = %s AND Paid + %s <= Total_Cost",
            (amount, Bill_ID, amount),
        )])
        if updated == 0:
            raise ValueError("The bill changed before the payment could be applied. Try again.")
        return amount, balance - amount


# ----------------------------------------------------------------------
# GUI helpers
# ----------------------------------------------------------------------
def make_table(headers):
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return table


def fill_table(table, rows):
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))


def fill_combo(combo, items, allow_none=True):
    combo.clear()
    if allow_none:
        combo.addItem("(none)", None)
    for text, data in items:
        combo.addItem(text, data)


def show_error(parent, exc):
    QMessageBox.critical(parent, "Error", str(exc))


def selected_row(parent, table, kind):
    """Return the values of the selected table row as a list of strings,
    or None (after warning the user) if nothing is selected."""
    row = table.currentRow()
    if row < 0 or not table.selectionModel().hasSelection():
        QMessageBox.warning(parent, "Nothing Selected",
                            f"Select a {kind} in the table first.")
        return None
    return [table.item(row, c).text() for c in range(table.columnCount())]


def confirm(parent, title, message):
    answer = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return answer == QMessageBox.StandardButton.Yes


# ----------------------------------------------------------------------
# Patient tab
# ----------------------------------------------------------------------
class PatientTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        # --- add form ---
        self.name_edit = QLineEdit()
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 130)
        self.condition_combo = QComboBox()
        self.policy_combo = QComboBox()
        self.ins_combo = QComboBox()
        self.policy_combo.currentIndexChanged.connect(self.policy_changed)

        add_btn = QPushButton("Add Patient")
        add_btn.clicked.connect(self.add_patient)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_form)

        form = QFormLayout()
        form.addRow("Name:", self.name_edit)
        form.addRow("Age:", self.age_spin)
        form.addRow("Condition:", self.condition_combo)
        form.addRow("Policy Number:", self.policy_combo)
        form.addRow("Insurance Company:", self.ins_combo)
        btns = QHBoxLayout()
        btns.addWidget(add_btn)
        btns.addWidget(clear_btn)
        form.addRow(btns)

        add_box = QGroupBox("Add New Patient")
        add_box.setLayout(form)

        # --- search ---
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search patients...")
        self.search_edit.returnPressed.connect(self.search)
        self.search_field = QComboBox()
        self.search_field.addItems(["Name", "ID", "Condition", "Room", "Doctor", "Insurance"])
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        show_all_btn = QPushButton("Show All")
        show_all_btn.clicked.connect(self.show_all)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_edit)
        search_row.addWidget(self.search_field)
        search_row.addWidget(search_btn)
        search_row.addWidget(show_all_btn)
        search_row.addWidget(delete_btn)

        self.table = make_table(["ID", "Name", "Age", "Room", "Doctor",
                                 "Condition", "Policy #", "Insurance"])

        search_layout = QVBoxLayout()
        search_layout.addLayout(search_row)
        search_layout.addWidget(self.table)
        search_box = QGroupBox("Search Patients")
        search_box.setLayout(search_layout)

        layout = QHBoxLayout(self)
        layout.addWidget(add_box, 1)
        layout.addWidget(search_box, 3)

        self.load_lookups()
        self.show_all()

    def load_lookups(self):
        try:
            fill_combo(self.condition_combo, [(c, c) for c in self.db.conditions()],
                       allow_none=False)
            fill_combo(self.policy_combo,
                       [(f"{num} - {comp} {plan}", (num, comp)) for num, comp, plan in self.db.policies()])
            fill_combo(self.ins_combo, [(c, c) for c in self.db.ins_companies()])
        except MySQLError as exc:
            show_error(self, exc)

    def policy_changed(self):
        # Selecting a policy automatically sets the matching insurance company
        data = self.policy_combo.currentData()
        if data:
            index = self.ins_combo.findData(data[1])
            if index >= 0:
                self.ins_combo.setCurrentIndex(index)

    def clear_form(self):
        self.name_edit.clear()
        self.age_spin.setValue(0)
        for combo in (self.condition_combo, self.policy_combo, self.ins_combo):
            combo.setCurrentIndex(0)

    def add_patient(self):
        policy = self.policy_combo.currentData()
        try:
            new_id, room, doctor = self.db.add_patient(
                self.name_edit.text().strip(),
                self.age_spin.value(),
                self.condition_combo.currentData(),
                policy[0] if policy else None,
                self.ins_combo.currentData(),
            )
        except NoFacilitiesError as exc:
            QMessageBox.warning(self, "Unavailable", str(exc))
            return
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        QMessageBox.information(
            self, "Patient Added",
            f"Patient added with ID {new_id}.\n\n"
            f"Assigned room: {room}\nAssigned doctor: {doctor}",
        )
        self.clear_form()
        self.show_all()

    def search(self):
        try:
            rows = self.db.search_patients(self.search_edit.text(), self.search_field.currentText())
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        fill_table(self.table, rows)
        if not rows:
            QMessageBox.information(self, "Search", "No matching patients found.")

    def refresh(self):
        # Re-run the current search so the table stays filtered after a delete
        try:
            fill_table(self.table, self.db.search_patients(
                self.search_edit.text(), self.search_field.currentText()))
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)

    def delete_selected(self):
        row = selected_row(self, self.table, "patient")
        if row is None:
            return
        patient_id, name = int(row[0]), row[1]
        if not confirm(self, "Delete Patient",
                       f"Delete patient {patient_id} ({name})?\n\n"
                       "Their bills will also be deleted. This cannot be undone."):
            return
        try:
            self.db.delete_patient(patient_id)
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
        self.refresh()

    def show_all(self):
        self.search_edit.clear()
        try:
            fill_table(self.table, self.db.search_patients())
        except MySQLError as exc:
            show_error(self, exc)


# ----------------------------------------------------------------------
# Inventory tab
# ----------------------------------------------------------------------
class InventoryTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        # --- add form ---
        self.name_edit = QLineEdit()
        self.room_combo = QComboBox()
        self.medicine_combo = QComboBox()
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 99_999_999.99)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setPrefix("$")

        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_inventory)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_form)

        form = QFormLayout()
        form.addRow("Item Name:", self.name_edit)
        form.addRow("Room:", self.room_combo)
        form.addRow("Medicine:", self.medicine_combo)
        form.addRow("Cost:", self.cost_spin)
        btns = QHBoxLayout()
        btns.addWidget(add_btn)
        btns.addWidget(clear_btn)
        form.addRow(btns)

        add_box = QGroupBox("Add Inventory Item")
        add_box.setLayout(form)

        # --- search ---
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search inventory...")
        self.search_edit.returnPressed.connect(self.search)
        self.search_field = QComboBox()
        self.search_field.addItems(["Name", "ID", "Room", "Medicine"])
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        show_all_btn = QPushButton("Show All")
        show_all_btn.clicked.connect(self.show_all)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_edit)
        search_row.addWidget(self.search_field)
        search_row.addWidget(search_btn)
        search_row.addWidget(show_all_btn)
        search_row.addWidget(delete_btn)

        self.table = make_table(["ID", "Item Name", "Room", "Medicine", "Cost"])

        search_layout = QVBoxLayout()
        search_layout.addLayout(search_row)
        search_layout.addWidget(self.table)
        search_box = QGroupBox("Search Inventory")
        search_box.setLayout(search_layout)

        layout = QHBoxLayout(self)
        layout.addWidget(add_box, 1)
        layout.addWidget(search_box, 3)

        self.load_lookups()
        self.show_all()

    def load_lookups(self):
        try:
            fill_combo(self.room_combo, [(r, r) for r in self.db.rooms()])
            fill_combo(self.medicine_combo, [(m, m) for m in self.db.medicines()])
        except MySQLError as exc:
            show_error(self, exc)

    def clear_form(self):
        self.name_edit.clear()
        self.room_combo.setCurrentIndex(0)
        self.medicine_combo.setCurrentIndex(0)
        self.cost_spin.setValue(0)

    def add_inventory(self):
        try:
            room = self.room_combo.currentData()
            new_id, patient, bill_id = self.db.add_inventory(
                self.name_edit.text().strip(),
                room,
                self.medicine_combo.currentData(),
                round(self.cost_spin.value(), 2),
            )
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        message = f"Inventory item added with ID {new_id}."
        if bill_id is not None:
            message += (f"\n\n${self.cost_spin.value():.2f} was billed to {patient} "
                        f"(room {room}) on bill {bill_id}.")
        elif room and self.cost_spin.value() > 0:
            message += f"\n\nRoom {room} has no patient, so nothing was billed."
        QMessageBox.information(self, "Item Added", message)
        self.clear_form()
        self.show_all()

    def search(self):
        try:
            rows = self.db.search_inventory(self.search_edit.text(), self.search_field.currentText())
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        fill_table(self.table, rows)
        if not rows:
            QMessageBox.information(self, "Search", "No matching inventory found.")

    def refresh(self):
        # Re-run the current search so the table stays filtered after a delete
        try:
            fill_table(self.table, self.db.search_inventory(
                self.search_edit.text(), self.search_field.currentText()))
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)

    def delete_selected(self):
        row = selected_row(self, self.table, "inventory item")
        if row is None:
            return
        inventory_id, name = int(row[0]), row[1]
        if not confirm(self, "Delete Inventory Item",
                       f"Delete inventory item {inventory_id} ({name})?\n\n"
                       "This cannot be undone."):
            return
        try:
            self.db.delete_inventory(inventory_id)
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
        self.refresh()

    def show_all(self):
        self.search_edit.clear()
        try:
            fill_table(self.table, self.db.search_inventory())
        except MySQLError as exc:
            show_error(self, exc)


# ----------------------------------------------------------------------
# Billing tab
# ----------------------------------------------------------------------
UPFRONT_RATE = Decimal("0.10")   # "10% Payment" button, same as Search.add_payment


class BillingTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.bill_id = None   # bill currently selected in the table

        # --- payment form ---
        self.bill_label = QLabel("-")
        self.patient_label = QLabel("-")
        self.total_label = QLabel("-")
        self.paid_label = QLabel("-")
        self.balance_label = QLabel("-")
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 99_999_999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("$")

        self.upfront_btn = QPushButton("10% Payment")
        self.upfront_btn.clicked.connect(self.fill_upfront)
        self.full_btn = QPushButton("Pay Full Balance")
        self.full_btn.clicked.connect(self.fill_full)
        self.pay_btn = QPushButton("Apply Payment")
        self.pay_btn.clicked.connect(self.apply_payment)

        form = QFormLayout()
        form.addRow("Bill ID:", self.bill_label)
        form.addRow("Patient:", self.patient_label)
        form.addRow("Total Cost:", self.total_label)
        form.addRow("Paid:", self.paid_label)
        form.addRow("Balance:", self.balance_label)
        form.addRow("Payment Amount:", self.amount_spin)
        quick = QHBoxLayout()
        quick.addWidget(self.upfront_btn)
        quick.addWidget(self.full_btn)
        form.addRow(quick)
        form.addRow(self.pay_btn)

        pay_box = QGroupBox("Apply Payment")
        pay_box.setLayout(form)

        # --- search ---
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search bills...")
        self.search_edit.returnPressed.connect(self.search)
        self.search_field = QComboBox()
        self.search_field.addItems(["Patient", "Patient ID", "Bill ID", "Unpaid Only"])
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        show_all_btn = QPushButton("Show All")
        show_all_btn.clicked.connect(self.show_all)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_edit)
        search_row.addWidget(self.search_field)
        search_row.addWidget(search_btn)
        search_row.addWidget(show_all_btn)

        self.table = make_table(["Bill ID", "Patient ID", "Patient", "Total Cost", "Paid", "Balance"])
        self.table.itemSelectionChanged.connect(self.selection_changed)

        search_layout = QVBoxLayout()
        search_layout.addLayout(search_row)
        search_layout.addWidget(self.table)
        search_box = QGroupBox("Search Bills")
        search_box.setLayout(search_layout)

        layout = QHBoxLayout(self)
        layout.addWidget(pay_box, 1)
        layout.addWidget(search_box, 3)

        self.show_all()

    # --- selected bill -----------------------------------------------
    def selection_changed(self):
        row = self.table.currentRow()
        if row < 0 or not self.table.selectionModel().hasSelection():
            self.set_selected(None)
            return
        self.set_selected(int(self.table.item(row, 0).text()))

    def set_selected(self, bill_id):
        self.bill_id = bill_id
        self.amount_spin.setValue(0)
        if bill_id is None:
            for label in (self.bill_label, self.patient_label, self.total_label,
                          self.paid_label, self.balance_label):
                label.setText("-")
            enabled = False
        else:
            row = self.table.currentRow()
            values = [self.table.item(row, c).text() for c in range(self.table.columnCount())]
            self.bill_label.setText(values[0])
            self.patient_label.setText(f"{values[2]} (ID {values[1]})" if values[2] else values[1])
            self.total_label.setText(f"${values[3]}")
            self.paid_label.setText(f"${values[4]}")
            self.balance_label.setText(f"${values[5]}")
            enabled = Decimal(values[5]) > 0
        for widget in (self.amount_spin, self.upfront_btn, self.full_btn, self.pay_btn):
            widget.setEnabled(enabled)

    def fill_upfront(self):
        try:
            total, paid = self.db.get_bill(self.bill_id)
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        amount = min(total * UPFRONT_RATE, total - paid)
        self.amount_spin.setValue(float(amount.quantize(Decimal("0.01"), ROUND_HALF_UP)))

    def fill_full(self):
        try:
            total, paid = self.db.get_bill(self.bill_id)
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        self.amount_spin.setValue(float(total - paid))

    def apply_payment(self):
        if self.bill_id is None:
            QMessageBox.warning(self, "Nothing Selected", "Select a bill in the table first.")
            return
        bill_id = self.bill_id
        try:
            amount, balance = self.db.add_payment(bill_id, self.amount_spin.value())
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        message = f"Applied ${amount} to bill {bill_id}.\n\nRemaining balance: ${balance}"
        if balance == 0:
            message += "\n\nThis bill is now paid in full."
        QMessageBox.information(self, "Payment Applied", message)
        self.refresh(select_bill=bill_id)

    # --- searching ---------------------------------------------------
    def load(self, rows, select_bill=None):
        self.table.blockSignals(True)
        fill_table(self.table, rows)
        self.table.clearSelection()
        self.table.blockSignals(False)
        self.set_selected(None)
        if select_bill is not None:
            for r in range(self.table.rowCount()):
                if self.table.item(r, 0).text() == str(select_bill):
                    self.table.selectRow(r)   # triggers selection_changed
                    break

    def search(self):
        try:
            rows = self.db.search_bills(self.search_edit.text(), self.search_field.currentText())
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        self.load(rows)
        if not rows:
            QMessageBox.information(self, "Search", "No matching bills found.")

    def refresh(self, select_bill=None):
        # Re-run the current search, keeping the selected bill if there is one
        if select_bill is None:
            select_bill = self.bill_id
        try:
            rows = self.db.search_bills(self.search_edit.text(), self.search_field.currentText())
        except (ValueError, MySQLError) as exc:
            show_error(self, exc)
            return
        self.load(rows, select_bill)

    def show_all(self):
        self.search_edit.clear()
        self.search_field.setCurrentText("Patient")
        try:
            self.load(self.db.search_bills())
        except MySQLError as exc:
            show_error(self, exc)


# ----------------------------------------------------------------------
# Main window
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Hospital Database")
        self.resize(1200, 600)

        self.tabs = QTabWidget()
        self.tabs.addTab(PatientTab(db), "Patients")
        self.tabs.addTab(InventoryTab(db), "Inventory")
        self.tabs.addTab(BillingTab(db), "Billing")
        # Reload a tab's table when switching to it, so e.g. bills of a
        # patient deleted on the Patients tab disappear from Billing
        self.tabs.currentChanged.connect(lambda i: self.tabs.widget(i).refresh())
        self.setCentralWidget(self.tabs)

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


# ----------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Database - Login")
        self.attempts_left = MAX_LOGIN_ATTEMPTS

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Log In")
        buttons.accepted.connect(self.try_login)
        buttons.rejected.connect(self.reject)

        form = QFormLayout(self)
        form.addRow(QLabel("Please log in to continue."))
        form.addRow("Username:", self.username_edit)
        form.addRow("Password:", self.password_edit)
        form.addRow(self.error_label)
        form.addRow(buttons)
        self.setMinimumWidth(320)

    def try_login(self):
        # compare_digest takes the same time whether or not the text matches
        user_ok = hmac.compare_digest(self.username_edit.text(), LOGIN_USERNAME)
        pass_ok = hmac.compare_digest(self.password_edit.text(), LOGIN_PASSWORD)
        if user_ok and pass_ok:
            self.accept()
            return
        self.attempts_left -= 1
        if self.attempts_left <= 0:
            QMessageBox.critical(self, "Login Failed", "Too many failed attempts. Exiting.")
            self.reject()
            return
        self.error_label.setText(f"Incorrect username or password. "
                                 f"{self.attempts_left} attempt(s) left.")
        self.password_edit.clear()
        self.password_edit.setFocus()


def login():
    """Show the login dialog. Returns True if the user logged in."""
    app = QApplication.instance() or QApplication(sys.argv)
    return LoginDialog().exec() == QDialog.DialogCode.Accepted


def main(require_login=True):
    app = QApplication.instance() or QApplication(sys.argv)
    if require_login and not login():
        sys.exit(0)
    try:
        db = HospitalDB(DB_CONFIG)
    except MySQLError as exc:
        QMessageBox.critical(None, "Database Error",
                             f"Could not connect to MySQL:\n{exc}\n\n"
                             "Make sure MySQL is running and you have run "
                             "Create_Tables.py and Insert_Data.py.")
        sys.exit(1)

    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
