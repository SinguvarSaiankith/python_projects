import tkinter as tk
from tkinter import messagebox
import random
import string
import pyperclip


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("400x400")

        self.length_label = tk.Label(root, text="Password Length:", font=('arial', 12))
        self.length_label.pack(pady=10)

        self.length_entry = tk.Entry(root, font=('arial', 12), width=5)
        self.length_entry.pack(pady=5)

        self.include_uppercase = tk.BooleanVar()
        self.include_uppercase_check = tk.Checkbutton(root, text="Include Uppercase Letters",
                                                      variable=self.include_uppercase, font=('arial', 12))
        self.include_uppercase_check.pack(pady=5)

        self.include_lowercase = tk.BooleanVar()
        self.include_lowercase_check = tk.Checkbutton(root, text="Include Lowercase Letters",
                                                      variable=self.include_lowercase, font=('arial', 12))
        self.include_lowercase_check.pack(pady=5)

        self.include_numbers = tk.BooleanVar()
        self.include_numbers_check = tk.Checkbutton(root, text="Include Numbers", variable=self.include_numbers,
                                                    font=('arial', 12))
        self.include_numbers_check.pack(pady=5)

        self.include_special = tk.BooleanVar()
        self.include_special_check = tk.Checkbutton(root, text="Include Special Characters",
                                                    variable=self.include_special, font=('arial', 12))
        self.include_special_check.pack(pady=5)

        self.generate_button = tk.Button(root, text="Generate Password", command=self.generate_password,
                                         font=('arial', 12, 'bold'))
        self.generate_button.pack(pady=20)

        self.password_entry = tk.Entry(root, font=('arial', 12), width=30)
        self.password_entry.pack(pady=10)

        self.copy_button = tk.Button(root, text="Copy to Clipboard", command=self.copy_to_clipboard,
                                     font=('arial', 12, 'bold'))
        self.copy_button.pack(pady=10)

    def generate_password(self):
        length = self.length_entry.get()

        if not length.isdigit():
            messagebox.showerror("Error", "Password length must be a number")
            return

        length = int(length)
        if length <= 0:
            messagebox.showerror("Error", "Password length must be greater than 0")
            return

        characters = ""

        if self.include_uppercase.get():
            characters += string.ascii_uppercase
        if self.include_lowercase.get():
            characters += string.ascii_lowercase
        if self.include_numbers.get():
            characters += string.digits
        if self.include_special.get():
            characters += string.punctuation

        if not characters:
            messagebox.showerror("Error", "Select at least one character set")
            return

        password = ''.join(random.choice(characters) for _ in range(length))
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def copy_to_clipboard(self):
        password = self.password_entry.get()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Success", "Password copied to clipboard")
        else:
            messagebox.showerror("Error", "No password to copy")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
