#!/usr/bin/env python3
"""
Test Entry widget behavior
"""

import tkinter as tk

def test_entry():
    root = tk.Tk()
    root.title("Entry Test")
    root.geometry("400x200")
    
    # Create entries
    tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(root, width=30)
    username_entry.grid(row=0, column=1, padx=10, pady=10)
    
    tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(root, width=30, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)
    
    # Test button
    def test_values():
        username = username_entry.get()
        password = password_entry.get()
        print(f"Username: '{username}', Password: '{password}'")
        result_label.config(text=f"Username: '{username}', Password: '{password}'")
    
    test_button = tk.Button(root, text="Test", command=test_values)
    test_button.grid(row=2, column=0, columnspan=2, pady=10)
    
    result_label = tk.Label(root, text="Enter values and click Test")
    result_label.grid(row=3, column=0, columnspan=2, pady=10)
    
    # Pre-fill some values for testing
    username_entry.insert(0, "test_user")
    password_entry.insert(0, "test_pass")
    
    root.mainloop()

if __name__ == "__main__":
    test_entry() 