from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector

# Color scheme and styling constants
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_card': '#0f3460',
    'bg_input': '#e8e8e8',
    'accent': '#e94560',
    'accent_hover': '#c73b54',
    'text_light': '#ffffff',
    'text_dark': '#2d3436',
    'text_muted': '#b0b0b0',
    'success': '#00b894',
    'danger': '#e17055',
    'warning': '#fdcb6e'
}

def setup_styles():
    """Configure ttk styles for modern look"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure Combobox
    style.configure('Custom.TCombobox',
                    fieldbackground=COLORS['bg_input'],
                    background=COLORS['bg_input'],
                    foreground=COLORS['text_dark'],
                    borderwidth=0,
                    focuscolor='none',
                    padding=8)
    
    style.map('Custom.TCombobox',
              fieldbackground=[('readonly', COLORS['bg_input'])],
              background=[('readonly', COLORS['bg_input'])])
    
    # Configure Treeview
    style.configure('Custom.Treeview',
                    background=COLORS['bg_input'],
                    foreground=COLORS['text_dark'],
                    fieldbackground=COLORS['bg_input'],
                    borderwidth=0,
                    rowheight=30)
    
    style.map('Custom.Treeview',
              background=[('selected', COLORS['accent'])],
              foreground=[('selected', COLORS['text_light'])])
    
    style.configure('Custom.Treeview.Heading',
                    background=COLORS['bg_secondary'],
                    foreground=COLORS['text_light'],
                    borderwidth=0,
                    padding=10,
                    font=('Segoe UI', 10, 'bold'))
    
    style.map('Custom.Treeview.Heading',
              background=[('active', COLORS['bg_card'])],
              foreground=[('active', COLORS['text_light'])])
    
    return style

def create_rounded_button(parent, text, command, **kwargs):
    """Create a modern rounded button"""
    btn = Button(
        parent,
        text=text,
        command=command,
        font=('Segoe UI', 10, 'bold'),
        relief='flat',
        borderwidth=0,
        cursor='hand2',
        **kwargs
    )
    return btn

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
        tree.column(col, width=120, anchor='center')

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
    add_win.geometry("450x600")
    add_win.resizable(False, False)
    add_win.configure(bg=COLORS['bg_secondary'])

    # Title Frame
    title_frame = Frame(add_win, bg=COLORS['bg_primary'], height=80)
    title_frame.pack(fill=X, pady=(0, 20))
    title_frame.pack_propagate(False)
    
    Label(title_frame, 
          text=f"➕ Add New Record", 
          font=("Segoe UI", 16, "bold"),
          fg=COLORS['text_light'],
          bg=COLORS['bg_primary']).pack(pady=20)
    
    Label(title_frame, 
          text=f"Table: {table_name}",
          font=("Segoe UI", 10),
          fg=COLORS['text_muted'],
          bg=COLORS['bg_primary']).pack()

    entries = {}
    form_frame = Frame(add_win, bg=COLORS['bg_secondary'])
    form_frame.pack(pady=5, padx=30, fill=X)

    for col in columns:
        row_frame = Frame(form_frame, bg=COLORS['bg_secondary'])
        row_frame.pack(fill=X, pady=8)
        
        label = Label(row_frame, 
                      text=col, 
                      width=20, 
                      anchor="w", 
                      font=("Segoe UI", 10, "bold"),
                      fg=COLORS['text_light'],
                      bg=COLORS['bg_secondary'])
        label.pack(side=LEFT)
        
        entry = Entry(row_frame, 
                      width=25,
                      font=("Segoe UI", 10),
                      relief='flat',
                      bg=COLORS['bg_input'],
                      fg=COLORS['text_dark'])
        entry.pack(side=LEFT, padx=(10, 0))
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

    btn_frame = Frame(add_win, bg=COLORS['bg_secondary'])
    btn_frame.pack(pady=25)
    
    submit_btn = create_rounded_button(
        btn_frame, 
        "✓ Submit", 
        submit_add,
        bg=COLORS['success'],
        fg='white',
        width=15,
        height=1
    )
    submit_btn.pack(side=LEFT, padx=5)
    
    cancel_btn = create_rounded_button(
        btn_frame,
        "✗ Cancel",
        add_win.destroy,
        bg=COLORS['danger'],
        fg='white',
        width=15,
        height=1
    )
    cancel_btn.pack(side=LEFT, padx=5)

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
    update_win.geometry("450x600")
    update_win.resizable(False, False)
    update_win.configure(bg=COLORS['bg_secondary'])

    # Title Frame
    title_frame = Frame(update_win, bg=COLORS['bg_primary'], height=80)
    title_frame.pack(fill=X, pady=(0, 20))
    title_frame.pack_propagate(False)
    
    Label(title_frame, 
          text=f"✏️ Update Record", 
          font=("Segoe UI", 16, "bold"),
          fg=COLORS['text_light'],
          bg=COLORS['bg_primary']).pack(pady=20)
    
    Label(title_frame, 
          text=f"Table: {table_name}",
          font=("Segoe UI", 10),
          fg=COLORS['text_muted'],
          bg=COLORS['bg_primary']).pack()

    entries = {}
    form_frame = Frame(update_win, bg=COLORS['bg_secondary'])
    form_frame.pack(pady=5, padx=30, fill=X)

    for col, val in zip(columns, row_values):
        row_frame = Frame(form_frame, bg=COLORS['bg_secondary'])
        row_frame.pack(fill=X, pady=8)
        
        label = Label(row_frame, 
                      text=col, 
                      width=20, 
                      anchor="w", 
                      font=("Segoe UI", 10, "bold"),
                      fg=COLORS['text_light'],
                      bg=COLORS['bg_secondary'])
        label.pack(side=LEFT)
        
        entry = Entry(row_frame, 
                      width=25,
                      font=("Segoe UI", 10),
                      relief='flat',
                      bg=COLORS['bg_input'],
                      fg=COLORS['text_dark'])
        entry.insert(0, val)
        if col == primary_key_col:
            entry.config(state="disabled", bg='#d0d0d0')
        entry.pack(side=LEFT, padx=(10, 0))
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

    btn_frame = Frame(update_win, bg=COLORS['bg_secondary'])
    btn_frame.pack(pady=25)
    
    update_btn = create_rounded_button(
        btn_frame,
        "✓ Update",
        submit_update,
        bg=COLORS['accent'],
        fg='white',
        width=15,
        height=1
    )
    update_btn.pack(side=LEFT, padx=5)
    
    cancel_btn = create_rounded_button(
        btn_frame,
        "✗ Cancel",
        update_win.destroy,
        bg=COLORS['danger'],
        fg='white',
        width=15,
        height=1
    )
    cancel_btn.pack(side=LEFT, padx=5)

def open_dashboard():
    global tree
    global selected_table

    dashboard = Toplevel()
    dashboard.title("Coffee Shop Database Management System")
    dashboard.geometry("1300x750")
    dashboard.configure(bg=COLORS['bg_secondary'])

    # Header
    header_frame = Frame(dashboard, bg=COLORS['bg_primary'], height=100)
    header_frame.pack(fill=X, pady=(0, 20))
    header_frame.pack_propagate(False)
    
    Label(
        header_frame,
        text="☕ COFFEE SHOP DATABASE MANAGEMENT SYSTEM",
        font=("Segoe UI", 20, "bold"),
        fg=COLORS['text_light'],
        bg=COLORS['bg_primary']
    ).pack(pady=30)
    
    # Control Panel
    control_frame = Frame(dashboard, bg=COLORS['bg_secondary'])
    control_frame.pack(pady=15, padx=20, fill=X)

    # Left side - Table selection
    left_frame = Frame(control_frame, bg=COLORS['bg_secondary'])
    left_frame.pack(side=LEFT, padx=10)
    
    Label(left_frame, 
          text="Select Table:", 
          font=("Segoe UI", 11, "bold"),
          fg=COLORS['text_light'],
          bg=COLORS['bg_secondary']).pack(side=LEFT, padx=(0, 10))

    selected_table = StringVar()
    combo = ttk.Combobox(
        left_frame,
        textvariable=selected_table,
        state="readonly",
        width=25,
        style='Custom.TCombobox'
    )
    combo["values"] = (
        "Product", "Customer", "Employee", "Supplier",
        "Inventory", "Sales", "Sales_Details", "Product_Recipe"
    )
    combo.set("Select a Table")
    combo.pack(side=LEFT)

    # Right side - Buttons
    btn_frame = Frame(control_frame, bg=COLORS['bg_secondary'])
    btn_frame.pack(side=RIGHT, padx=10)

    buttons = [
        ("📊 Show Data", COLORS['accent'], lambda: display_table(selected_table.get())),
        ("➕ Add", COLORS['success'], add_record),
        ("✏️ Update", COLORS['warning'], update_record),
        ("🗑️ Delete", COLORS['danger'], delete_record)
    ]

    for text, color, cmd in buttons:
        btn = create_rounded_button(
            btn_frame,
            text,
            cmd,
            bg=color,
            fg='white',
            width=12,
            height=1
        )
        btn.pack(side=LEFT, padx=4)

    # Treeview Frame
    tree_frame = Frame(dashboard, bg=COLORS['bg_secondary'])
    tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    x_scroll = Scrollbar(tree_frame, orient=HORIZONTAL)
    y_scroll = Scrollbar(tree_frame, orient=VERTICAL)
    x_scroll.pack(side=BOTTOM, fill=X)
    y_scroll.pack(side=RIGHT, fill=Y)

    tree = ttk.Treeview(
        tree_frame,
        style='Custom.Treeview',
        xscrollcommand=x_scroll.set,
        yscrollcommand=y_scroll.set
    )
    tree.pack(fill=BOTH, expand=True)

    x_scroll.config(command=tree.xview)
    y_scroll.config(command=tree.yview)

def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "1234":
        result_label.config(text="✓ Login Successful", fg=COLORS['success'])
        root.after(500, open_dashboard)
    else:
        result_label.config(text="✗ Invalid Username or Password", fg=COLORS['danger'])

# Main Login Window
root = Tk()
root.title("Coffee Shop Login")
root.geometry("450x400")
root.resizable(False, False)
root.configure(bg=COLORS['bg_secondary'])

# Setup styles
style = setup_styles()

# Login Container
login_frame = Frame(root, bg=COLORS['bg_primary'], relief='flat', bd=0)
login_frame.pack(expand=True, fill=BOTH, padx=30, pady=30)

# Title
Label(login_frame, 
      text="☕ COFFEE SHOP", 
      font=("Segoe UI", 22, "bold"),
      fg=COLORS['text_light'],
      bg=COLORS['bg_primary']).pack(pady=(20, 5))

Label(login_frame, 
      text="Login to Access Database", 
      font=("Segoe UI", 11),
      fg=COLORS['text_muted'],
      bg=COLORS['bg_primary']).pack(pady=(0, 30))

# Username
Label(login_frame, 
      text="Username", 
      font=("Segoe UI", 10, "bold"),
      fg=COLORS['text_light'],
      bg=COLORS['bg_primary'],
      anchor='w').pack(fill=X, padx=30, pady=(0, 5))

username_entry = Entry(login_frame, 
                       width=30,
                       font=("Segoe UI", 11),
                       relief='flat',
                       bg=COLORS['bg_input'],
                       fg=COLORS['text_dark'])
username_entry.pack(pady=(0, 15), padx=30, ipady=5)

# Password
Label(login_frame, 
      text="Password", 
      font=("Segoe UI", 10, "bold"),
      fg=COLORS['text_light'],
      bg=COLORS['bg_primary'],
      anchor='w').pack(fill=X, padx=30, pady=(0, 5))

password_entry = Entry(login_frame, 
                       show="*", 
                       width=30,
                       font=("Segoe UI", 11),
                       relief='flat',
                       bg=COLORS['bg_input'],
                       fg=COLORS['text_dark'])
password_entry.pack(pady=(0, 20), padx=30, ipady=5)

# Login Button
login_btn = create_rounded_button(
    login_frame,
    "🔑 Login",
    login,
    bg=COLORS['accent'],
    fg='white',
    width=20,
    height=2
)
login_btn.pack(pady=10)

# Result Label
result_label = Label(login_frame, 
                     text="", 
                     font=("Segoe UI", 10, "bold"),
                     fg=COLORS['text_light'],
                     bg=COLORS['bg_primary'])
result_label.pack(pady=10)

# Footer
Label(login_frame, 
      text="Default: admin / 1234", 
      font=("Segoe UI", 8),
      fg=COLORS['text_muted'],
      bg=COLORS['bg_primary']).pack(pady=(20, 5))

root.mainloop()