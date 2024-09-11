import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import sqlite3
import csv
import re

class ContactBook:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Book")
        self.root.geometry("600x400")

        self.conn = sqlite3.connect('contacts.db')
        self.cursor = self.conn.cursor()
        self.create_table()

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self.create_widgets()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        # Labels and Entry Widgets
        tk.Label(self.root, text="Name").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Phone").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.phone_var).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Email").grid(row=2, column=0, padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.email_var).grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Address").grid(row=3, column=0, padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.address_var).grid(row=3, column=1, padx=10, pady=5)

        # Buttons
        tk.Button(self.root, text="Add Contact", command=self.add_contact).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Update Contact", command=self.update_contact).grid(row=4, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Delete Contact", command=self.delete_contact).grid(row=4, column=2, padx=10, pady=10)

        # Search
        tk.Label(self.root, text="Search").grid(row=5, column=0, padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.search_var).grid(row=5, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Search", command=self.search_contact).grid(row=5, column=2, padx=10, pady=5)

        # Listbox
        self.contacts_listbox = tk.Listbox(self.root, height=10, width=50)
        self.contacts_listbox.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
        self.contacts_listbox.bind('<<ListboxSelect>>', self.load_contact)

        # Export and Import
        tk.Button(self.root, text="Export Contacts", command=self.export_contacts).grid(row=7, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Import Contacts", command=self.import_contacts).grid(row=7, column=1, padx=10, pady=10)

        self.load_contacts()

    def load_contacts(self):
        self.contacts_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM contacts")
        contacts = self.cursor.fetchall()
        for contact in contacts:
            self.contacts_listbox.insert(tk.END, contact)

    def load_contact(self, event):
        selected_contact = self.contacts_listbox.get(tk.ACTIVE)
        self.name_var.set(selected_contact[1])
        self.phone_var.set(selected_contact[2])
        self.email_var.set(selected_contact[3])
        self.address_var.set(selected_contact[4])

    def add_contact(self):
        name = self.name_var.get()
        phone = self.phone_var.get()
        email = self.email_var.get()
        address = self.address_var.get()

        if not name or not phone or not email or not address:
            messagebox.showerror("Error", "All fields are required")
            return

        if not re.match(r"^[0-9]{10}$", phone):
            messagebox.showerror("Error", "Phone number must be exactly 10 digits")
            return

        if not email.endswith("@gmail.com"):
            messagebox.showerror("Error", "Email must end with @gmail.com")
            return

        self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)", (name, phone, email, address))
        self.conn.commit()
        self.load_contacts()
        self.clear_fields()

    def update_contact(self):
        selected_contact = self.get_selected_contact()
        if not selected_contact:
            return

        contact_id = selected_contact[0]
        name = self.name_var.get()
        phone = self.phone_var.get()
        email = self.email_var.get()
        address = self.address_var.get()

        if not name or not phone or not email or not address:
            messagebox.showerror("Error", "All fields are required")
            return

        if not re.match(r"^[0-9]{10}$", phone):
            messagebox.showerror("Error", "Phone number must be exactly 10 digits")
            return

        if not email.endswith("@gmail.com"):
            messagebox.showerror("Error", "Email must end with @gmail.com")
            return

        self.cursor.execute("UPDATE contacts SET name = ?, phone = ?, email = ?, address = ? WHERE id = ?", (name, phone, email, address, contact_id))
        self.conn.commit()
        self.load_contacts()
        self.clear_fields()

    def delete_contact(self):
        selected_contact = self.get_selected_contact()
        if not selected_contact:
            return

        contact_id = selected_contact[0]

        self.cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.conn.commit()
        self.load_contacts()
        self.clear_fields()

    def get_selected_contact(self):
        selected_contact_name = self.name_var.get()
        self.cursor.execute("SELECT * FROM contacts WHERE name = ?", (selected_contact_name,))
        contacts = self.cursor.fetchall()

        if len(contacts) == 0:
            messagebox.showerror("Error", "No contact found with this name")
            return None
        elif len(contacts) == 1:
            return contacts[0]
        else:
            contact_ids = [contact[0] for contact in contacts]
            selected_contact_id = simpledialog.askinteger("Select Contact", f"Multiple contacts found with the name {selected_contact_name}. Enter the ID of the contact you want to select:\n{contact_ids}")
            for contact in contacts:
                if contact[0] == selected_contact_id:
                    return contact
            messagebox.showerror("Error", "Invalid contact ID")
            return None

    def search_contact(self):
        search_term = self.search_var.get()
        self.contacts_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR address LIKE ?", (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        contacts = self.cursor.fetchall()
        for contact in contacts:
            self.contacts_listbox.insert(tk.END, contact)

    def export_contacts(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.cursor.execute("SELECT * FROM contacts")
            contacts = self.cursor.fetchall()
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Phone", "Email", "Address"])
                writer.writerows(contacts)
            messagebox.showinfo("Success", "Contacts exported successfully")

    def import_contacts(self):
        file_path = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)", (row['Name'], row['Phone'], row['Email'], row['Address']))
                self.conn.commit()
            self.load_contacts()
            messagebox.showinfo("Success", "Contacts imported successfully")

    def clear_fields(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBook(root)
    root.mainloop()
