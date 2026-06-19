from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password.1",
        database="CoffeeShopDB"
    )


def display_table(table_name):
    if table_name == "Select a Table":
        return

    tree.delete(*tree.get_children())

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    tree["columns"] = columns
    tree["show"] = "headings"

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    for row in rows:
        tree.insert("", END, values=row)

    cursor.close()
    conn.close()


def add_record():
    table_name = selected_table.get()
    if table_name == "Select a Table":
        messagebox.showwarning("Warning", "Please select a table first.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
    cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    conn.close()

    add_win = Toplevel()
    add_win.title(f"Add Record - {table_name}")
    add_win.geometry("400x500")
    add_win.resizable(False, False)

    Label(add_win, text=f"Add New Record to {table_name}", font=("Arial", 13, "bold")).pack(pady=10)

    entries = {}
    form_frame = Frame(add_win)
    form_frame.pack(pady=5, padx=20, fill=X)

    for col in columns:
        row_frame = Frame(form_frame)
        row_frame.pack(fill=X, pady=3)
        Label(row_frame, text=col, width=20, anchor="w", font=("Arial", 10)).pack(side=LEFT)
        entry = Entry(row_frame, width=25)
        entry.pack(side=LEFT)
        entries[col] = entry

    def submit_add():
        values = [entries[col].get() for col in columns]
        if any(v.strip() == "" for v in values):
            messagebox.showwarning("Warning", "Please fill in all fields.", parent=add_win)
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            placeholders = ", ".join(["%s"] * len(columns))
            col_names = ", ".join(columns)
            cursor.execute(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", values)
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Record added successfully.", parent=add_win)
            add_win.destroy()
            display_table(table_name)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=add_win)

    Button(add_win, text="Submit", width=15, command=submit_add).pack(pady=15)


def delete_record():
    table_name = selected_table.get()
    if table_name == "Select a Table":
        messagebox.showwarning("Warning", "Please select a table first.")
        return

    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a row to delete.")
        return

    row_values = tree.item(selected[0])["values"]
    columns = tree["columns"]
    primary_key_col = columns[0]
    primary_key_val = row_values[0]

    confirm = messagebox.askyesno("Confirm Delete", f"Delete record where {primary_key_col} = {primary_key_val}?")
    if not confirm:
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE {primary_key_col} = %s", (primary_key_val,))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Record deleted successfully.")
        display_table(table_name)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def update_record():
    table_name = selected_table.get()
    if table_name == "Select a Table":
        messagebox.showwarning("Warning", "Please select a table first.")
        return

    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a row to update.")
        return

    row_values = tree.item(selected[0])["values"]
    columns = tree["columns"]
    primary_key_col = columns[0]
    primary_key_val = row_values[0]

    update_win = Toplevel()
    update_win.title(f"Update Record - {table_name}")
    update_win.geometry("400x500")
    update_win.resizable(False, False)

    Label(update_win, text=f"Update Record in {table_name}", font=("Arial", 13, "bold")).pack(pady=10)

    entries = {}
    form_frame = Frame(update_win)
    form_frame.pack(pady=5, padx=20, fill=X)

    for col, val in zip(columns, row_values):
        row_frame = Frame(form_frame)
        row_frame.pack(fill=X, pady=3)
        Label(row_frame, text=col, width=20, anchor="w", font=("Arial", 10)).pack(side=LEFT)
        entry = Entry(row_frame, width=25)
        entry.insert(0, val)
        if col == primary_key_col:
            entry.config(state="disabled")
        entry.pack(side=LEFT)
        entries[col] = entry

    def submit_update():
        set_parts = []
        values = []
        for col in columns:
            if col == primary_key_col:
                continue
            set_parts.append(f"{col} = %s")
            values.append(entries[col].get())
        values.append(primary_key_val)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            set_clause = ", ".join(set_parts)
            cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {primary_key_col} = %s", values)
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Record updated successfully.", parent=update_win)
            update_win.destroy()
            display_table(table_name)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=update_win)

    Button(update_win, text="Update", width=15, command=submit_update).pack(pady=15)


def open_dashboard():
    global tree
    global selected_table

    dashboard = Toplevel()
    dashboard.title("Coffee Shop Database Management System")
    dashboard.geometry("1200x650")

    Label(
        dashboard,
        text="COFFEE SHOP DATABASE MANAGEMENT SYSTEM",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    Label(dashboard, text="Choose a Table", font=("Arial", 12)).pack()

    selected_table = StringVar()

    combo = ttk.Combobox(
        dashboard,
        textvariable=selected_table,
        state="readonly",
        width=30
    )
    combo["values"] = (
        "Product", "Customer", "Employee", "Supplier",
        "Inventory", "Sales", "Sales_Details", "Product_Recipe"
    )
    combo.set("Select a Table")
    combo.pack(pady=10)

    # Button row
    btn_frame = Frame(dashboard)
    btn_frame.pack(pady=10)

    Button(btn_frame, text="Show Data", width=12,
           command=lambda: display_table(selected_table.get())).pack(side=LEFT, padx=5)
    Button(btn_frame, text="Add", width=12,
           command=add_record).pack(side=LEFT, padx=5)
    Button(btn_frame, text="Update", width=12,
           command=update_record).pack(side=LEFT, padx=5)
    Button(btn_frame, text="Delete", width=12,
           command=delete_record).pack(side=LEFT, padx=5)

    # Treeview Frame
    tree_frame = Frame(dashboard)
    tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    x_scroll = Scrollbar(tree_frame, orient=HORIZONTAL)
    y_scroll = Scrollbar(tree_frame, orient=VERTICAL)
    x_scroll.pack(side=BOTTOM, fill=X)
    y_scroll.pack(side=RIGHT, fill=Y)

    tree = ttk.Treeview(tree_frame)
    tree.pack(fill=BOTH, expand=True)

    x_scroll.config(command=tree.xview)
    y_scroll.config(command=tree.yview)
    tree.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)


def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "1234":
        result_label.config(text="Login Successful", fg="green")
        open_dashboard()
    else:
        result_label.config(text="Invalid Username or Password", fg="red")


root = Tk()
root.title("Coffee Shop Login")
root.geometry("400x300")
root.resizable(False, False)

Label(root, text="COFFEE SHOP LOGIN", font=("Arial", 18, "bold")).pack(pady=20)
Label(root, text="Username", font=("Arial", 12)).pack()
username_entry = Entry(root, width=30)
username_entry.pack(pady=5)
Label(root, text="Password", font=("Arial", 12)).pack()
password_entry = Entry(root, show="*", width=30)
password_entry.pack(pady=5)
Button(root, text="Login", width=15, command=login).pack(pady=15)
result_label = Label(root, text="", font=("Arial", 10))
result_label.pack()

root.mainloop()