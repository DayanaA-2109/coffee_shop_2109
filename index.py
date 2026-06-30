from tkinter import *
from tkinter import ttk, messagebox, font
import mysql.connector
from datetime import datetime
import threading
import time

# ============================================
# GLOBAL VARIABLES
# ============================================
tree = None
selected_table = None
status_bar = None
loading_overlay = None
dashboard_window = None
current_user = None
login_time = None


# ============================================
# DATABASE CONNECTION
# ============================================
def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Password.1",
            database="CoffeeShopDB",
            connection_timeout=10
        )
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to connect to database:\n{str(e)}")
        return None


# ============================================
# LOADING ANIMATION
# ============================================
class LoadingOverlay:
    def __init__(self, parent):
        self.parent = parent
        self.frame = Frame(parent, bg='white', bd=2, relief=SOLID)
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=200, height=100)

        self.label = Label(
            self.frame,
            text="⏳ Loading...",
            font=("Segoe UI", 14, "bold"),
            bg='white',
            fg='#667eea'
        )
        self.label.pack(expand=True)

        # Animated dots
        self.dots = 0
        self.animate()

    def animate(self):
        if self.frame.winfo_exists():
            self.dots = (self.dots + 1) % 4
            dots_text = "." * self.dots
            self.label.config(text=f"⏳ Loading{dots_text}")
            self.parent.after(500, self.animate)

    def destroy(self):
        self.frame.destroy()


# ============================================
# TOAST NOTIFICATION (Custom Tkinter Toast)
# ============================================
class Toast:
    def __init__(self, parent, message, type="info"):
        self.parent = parent

        # Colors based on type
        colors = {
            "success": {"bg": "#48bb78", "fg": "white"},
            "error": {"bg": "#fc8181", "fg": "white"},
            "info": {"bg": "#667eea", "fg": "white"},
            "warning": {"bg": "#ed8936", "fg": "white"}
        }

        color_set = colors.get(type, colors["info"])

        self.frame = Frame(parent, bg=color_set["bg"], bd=0, relief=FLAT)
        self.frame.place(relx=0.5, rely=0.95, anchor=CENTER)

        # Add shadow effect
        shadow = Frame(parent, bg='gray', bd=0)
        shadow.place(relx=0.5, rely=0.955, anchor=CENTER,
                     width=len(message) * 8 + 40, height=45)
        shadow.lower()

        Label(
            self.frame,
            text=message,
            font=("Segoe UI", 11, "bold"),
            bg=color_set["bg"],
            fg=color_set["fg"],
            padx=20,
            pady=10
        ).pack()

        # Auto-dismiss after 3 seconds
        parent.after(3000, self.dismiss)

    def dismiss(self):
        if self.frame.winfo_exists():
            self.frame.destroy()


# ============================================
# ENHANCED TABLE DISPLAY WITH STYLING
# ============================================
def display_table(table_name):
    global tree, status_bar

    if table_name == "Select a Table" or not table_name:
        return

    if tree is None:
        return

    # Show loading animation
    loading = LoadingOverlay(dashboard_window)
    dashboard_window.update()

    # Simulate async loading
    def load_data():
        try:
            conn = get_connection()
            if not conn:
                loading.destroy()
                return

            cursor = conn.cursor()

            # Get table data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            # Update treeview in main thread
            dashboard_window.after(0, lambda: update_treeview(columns, rows, table_name))

            cursor.close()
            conn.close()

            # Update status bar
            dashboard_window.after(0, lambda: update_status(f"Loaded {len(rows)} records from {table_name}", "success"))

        except mysql.connector.Error as e:
            dashboard_window.after(0, lambda: Toast(dashboard_window, f"Error: {str(e)}", "error"))
        finally:
            dashboard_window.after(0, loading.destroy)

    # Run in thread to prevent UI freezing
    threading.Thread(target=load_data, daemon=True).start()


def update_treeview(columns, rows, table_name):
    global tree

    tree.delete(*tree.get_children())

    # Configure columns
    tree["columns"] = columns
    tree["show"] = "headings"

    # Enhanced column styling
    for col in columns:
        tree.heading(col, text=col, anchor=CENTER)
        # Adjust column width based on content
        max_width = max(
            len(str(col)) * 10,
            max([len(str(row[idx])) for idx, row in enumerate(rows) if row], default=0) * 8
        )
        tree.column(col, width=min(max(120, max_width), 300), anchor=CENTER, minwidth=80)

    # Insert data with alternating colors
    for idx, row in enumerate(rows):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        tree.insert("", END, values=row, tags=(tag,))

    # Configure row colors
    tree.tag_configure('evenrow', background='#f7fafc')
    tree.tag_configure('oddrow', background='white')


def update_status(message, type="info"):
    global status_bar
    if status_bar:
        colors = {
            "success": "#48bb78",
            "error": "#fc8181",
            "info": "#667eea",
            "warning": "#ed8936"
        }
        status_bar.config(text=f"  {message}", bg=colors.get(type, "#667eea"), fg="white")
        # Reset after 5 seconds
        dashboard_window.after(5000, lambda: status_bar.config(text="  Ready", bg="#667eea"))


# ============================================
# DASHBOARD WITH ENHANCED UI
# ============================================
def open_dashboard():
    global tree, selected_table, status_bar, dashboard_window, login_time

    dashboard_window = Toplevel()
    dashboard_window.title("☕ Coffee Shop Database Management System")
    dashboard_window.geometry("1400x750")
    dashboard_window.configure(bg='#f0f4f8')
    dashboard_window.resizable(True, True)

    # Set icon (if available)
    try:
        dashboard_window.iconbitmap('coffee.ico')
    except:
        pass

    # Store login time
    login_time = datetime.now()

    # ===== HEADER WITH GRADIENT =====
    header_frame = Frame(
        dashboard_window,
        bg='#667eea',
        height=80,
        relief=FLAT
    )
    header_frame.pack(fill=X, side=TOP)
    header_frame.pack_propagate(False)

    # Gradient effect using multiple frames
    for i in range(10):
        gradient_frame = Frame(
            header_frame,
            bg=f'#{int(102 - i * 3):02x}{int(126 - i * 3):02x}{int(234 - i * 3):02x}',
            height=8
        )
        gradient_frame.pack(fill=X, side=TOP)

    # Header content
    content_frame = Frame(header_frame, bg='#667eea')
    content_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Title with emoji
    title_label = Label(
        content_frame,
        text="☕ COFFEE SHOP DATABASE MANAGEMENT SYSTEM",
        font=("Segoe UI", 20, "bold"),
        bg='#667eea',
        fg='white',
        anchor=W
    )
    title_label.pack(side=LEFT)

    # User info on right
    user_frame = Frame(content_frame, bg='#667eea')
    user_frame.pack(side=RIGHT)

    Label(
        user_frame,
        text=f"👤 {current_user}",
        font=("Segoe UI", 12),
        bg='#667eea',
        fg='white'
    ).pack(side=LEFT, padx=10)

    logout_btn = Button(
        user_frame,
        text="🚪 Logout",
        font=("Segoe UI", 10, "bold"),
        bg='white',
        fg='#667eea',
        padx=15,
        pady=5,
        cursor='hand2',
        relief=FLAT,
        command=lambda: logout(dashboard_window)
    )
    logout_btn.pack(side=LEFT, padx=10)

    # Hover effect for logout button
    def on_enter(e):
        logout_btn.config(bg='#edf2f7')

    def on_leave(e):
        logout_btn.config(bg='white')

    logout_btn.bind('<Enter>', on_enter)
    logout_btn.bind('<Leave>', on_leave)

    # ===== CONTROLS SECTION =====
    controls_frame = Frame(dashboard_window, bg='white', padx=20, pady=15)
    controls_frame.pack(fill=X, side=TOP, pady=(10, 0), padx=20)
    controls_frame.pack_propagate(False)
    controls_frame.config(height=60)

    # Left controls
    left_controls = Frame(controls_frame, bg='white')
    left_controls.pack(side=LEFT)

    Label(
        left_controls,
        text="📊 Select Table:",
        font=("Segoe UI", 12, "bold"),
        bg='white',
        fg='#2d3748'
    ).pack(side=LEFT, padx=(0, 10))

    # Enhanced combobox
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Custom.TCombobox',
                    fieldbackground='white',
                    background='white',
                    foreground='#2d3748',
                    font=('Segoe UI', 11),
                    padding=5)
    style.map('Custom.TCombobox',
              fieldbackground=[('readonly', 'white')],
              selectbackground=[('readonly', '#667eea')],
              selectforeground=[('readonly', 'white')])

    selected_table = StringVar()
    combo = ttk.Combobox(
        left_controls,
        textvariable=selected_table,
        state="readonly",
        width=25,
        style='Custom.TCombobox',
        font=("Segoe UI", 11)
    )

    combo["values"] = (
        "Product",
        "Customer",
        "Employee",
        "Supplier",
        "Inventory",
        "Sales",
        "Sales_Details",
        "Product_Recipe"
    )
    combo.set("Select a Table")
    combo.pack(side=LEFT, padx=5)

    # Buttons with modern styling
    def create_styled_button(parent, text, command, bg_color, hover_color):
        btn = Button(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg='white',
            padx=20,
            pady=8,
            relief=FLAT,
            cursor='hand2',
            command=command
        )
        btn.pack(side=LEFT, padx=5)

        def on_enter(e):
            btn.config(bg=hover_color)

        def on_leave(e):
            btn.config(bg=bg_color)

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        return btn

    create_styled_button(
        controls_frame,
        "📊 Show Data",
        lambda: display_table(selected_table.get()),
        '#667eea',
        '#5a67d8'
    )

    create_styled_button(
        controls_frame,
        "🔄 Refresh",
        lambda: refresh_data(),
        '#48bb78',
        '#38a169'
    )

    create_styled_button(
        controls_frame,
        "📋 Export CSV",
        lambda: export_csv(),
        '#ed8936',
        '#dd6b20'
    )

    create_styled_button(
        controls_frame,
        "📈 Statistics",
        lambda: show_statistics(),
        '#9f7aea',
        '#805ad5'
    )

    # ===== TABLE FRAME =====
    table_frame = Frame(dashboard_window, bg='white', bd=1, relief=SOLID)
    table_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Scrollbars with custom styling
    x_scroll = Scrollbar(table_frame, orient=HORIZONTAL, troughcolor='#edf2f7')
    y_scroll = Scrollbar(table_frame, orient=VERTICAL, troughcolor='#edf2f7')

    x_scroll.pack(side=BOTTOM, fill=X)
    y_scroll.pack(side=RIGHT, fill=Y)

    # Enhanced Treeview
    tree = ttk.Treeview(
        table_frame,
        xscrollcommand=x_scroll.set,
        yscrollcommand=y_scroll.set,
        selectmode='extended',
        height=20
    )
    tree.pack(fill=BOTH, expand=True)

    x_scroll.config(command=tree.xview)
    y_scroll.config(command=tree.yview)

    # Bind double-click to view details
    tree.bind('<Double-1>', on_row_double_click)
    tree.bind('<Button-3>', show_context_menu)  # Right-click context menu

    # ===== STATUS BAR =====
    status_frame = Frame(dashboard_window, bg='#667eea', height=30)
    status_frame.pack(fill=X, side=BOTTOM)
    status_frame.pack_propagate(False)

    status_bar = Label(
        status_frame,
        text="  Ready",
        font=("Segoe UI", 9),
        bg='#667eea',
        fg='white',
        anchor=W
    )
    status_bar.pack(side=LEFT, fill=X, expand=True)

    # Time display in status bar
    time_label = Label(
        status_frame,
        font=("Segoe UI", 9),
        bg='#667eea',
        fg='white'
    )
    time_label.pack(side=RIGHT, padx=10)

    def update_time():
        if dashboard_window.winfo_exists():
            current_time = datetime.now().strftime("%I:%M:%S %p")
            time_label.config(text=f"  🕐 {current_time}  ")
            dashboard_window.after(1000, update_time)

    update_time()

    # Show welcome toast
    Toast(dashboard_window, f"Welcome back, {current_user}! ☕", "success")


# ============================================
# CONTEXT MENU (Right-click functionality)
# ============================================
def show_context_menu(event):
    if not tree.selection():
        return

    menu = Menu(dashboard_window, tearoff=0, bg='white', fg='#2d3748')
    menu.add_command(label="📋 Copy Row", command=copy_row)
    menu.add_command(label="📊 View Details", command=view_row_details)
    menu.add_separator()
    menu.add_command(label="🔄 Refresh", command=refresh_data)
    menu.post(event.x_root, event.y_root)


def copy_row():
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])['values']
        row_text = '\t'.join(str(v) for v in values)
        dashboard_window.clipboard_clear()
        dashboard_window.clipboard_append(row_text)
        Toast(dashboard_window, "Row copied to clipboard!", "success")


def view_row_details():
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])['values']
        columns = tree["columns"]

        details = "\n".join(f"{col}: {val}" for col, val in zip(columns, values))
        messagebox.showinfo("Row Details", details)


def on_row_double_click(event):
    view_row_details()


# ============================================
# EXPORT TO CSV
# ============================================
def export_csv():
    if not tree:
        return

    from tkinter import filedialog
    import csv

    filename = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Export Data"
    )

    if not filename:
        return

    try:
        columns = tree["columns"]
        rows = []
        for item in tree.get_children():
            rows.append(tree.item(item)['values'])

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

        Toast(dashboard_window, f"Data exported to {filename}", "success")
    except Exception as e:
        Toast(dashboard_window, f"Export failed: {str(e)}", "error")


# ============================================
# STATISTICS
# ============================================
def show_statistics():
    if not tree or not tree.get_children():
        Toast(dashboard_window, "No data to analyze", "warning")
        return

    columns = tree["columns"]
    rows = []
    for item in tree.get_children():
        rows.append(tree.item(item)['values'])

    stats = f"📊 Table Statistics\n\n"
    stats += f"Total Records: {len(rows)}\n"
    stats += f"Total Columns: {len(columns)}\n"

    # Try to find numeric columns for stats
    for idx, col in enumerate(columns):
        numeric_values = []
        for row in rows:
            if idx < len(row):
                try:
                    val = float(row[idx])
                    numeric_values.append(val)
                except (ValueError, TypeError):
                    pass

        if numeric_values:
            stats += f"\n{col}:\n"
            stats += f"  - Count: {len(numeric_values)}\n"
            stats += f"  - Min: {min(numeric_values):.2f}\n"
            stats += f"  - Max: {max(numeric_values):.2f}\n"
            stats += f"  - Avg: {sum(numeric_values) / len(numeric_values):.2f}\n"

    messagebox.showinfo("Table Statistics", stats)


# ============================================
# REFRESH DATA
# ============================================
def refresh_data():
    if selected_table and selected_table.get() != "Select a Table":
        display_table(selected_table.get())
    else:
        Toast(dashboard_window, "Please select a table first", "warning")


# ============================================
# LOGOUT
# ============================================
def logout(window):
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        window.destroy()
        # Show login window again
        root.deiconify()
        Toast(root, "Logged out successfully", "info")


# ============================================
# ENHANCED LOGIN
# ============================================
def login():
    global current_user
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    # Show loading animation on login
    login_btn.config(text="⏳ Logging in...", state=DISABLED)
    root.update()

    # Simulate async login check
    def check_login():
        # In production, check against database
        if username == "admin" and password == "1234":
            current_user = username
            root.after(0, lambda: login_success())
        else:
            root.after(0, lambda: login_failed())

    threading.Thread(target=check_login, daemon=True).start()


def login_success():
    login_btn.config(text="Login", state=NORMAL)
    result_label.config(text="✅ Login Successful!", fg="#48bb78", font=("Segoe UI", 11, "bold"))

    # Hide login window
    root.withdraw()

    # Open dashboard
    open_dashboard()


def login_failed():
    login_btn.config(text="Login", state=NORMAL)
    result_label.config(text="❌ Invalid Username or Password", fg="#fc8181", font=("Segoe UI", 11, "bold"))

    # Shake animation
    for widget in [username_entry, password_entry]:
        widget.config(bg='#fff5f5')
        root.after(500, lambda: widget.config(bg='white'))


# ============================================
# KEYBOARD SHORTCUTS
# ============================================
def on_key_press(event):
    if event.keysym == 'Return' and event.widget in [username_entry, password_entry]:
        login()
    elif event.keysym == 'Escape':
        root.quit()


# ============================================
# MAIN APPLICATION
# ============================================
# ===== LOGIN WINDOW =====
root = Tk()
root.title("☕ Coffee Shop Login")
root.geometry("450x550")
root.configure(bg='#f0f4f8')
root.resizable(False, False)

# Center window on screen
root.eval('tk::PlaceWindow . center')

# ===== LOGIN FRAME =====
login_frame = Frame(root, bg='white', bd=2, relief=SOLID, padx=40, pady=40)
login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

# Logo
Label(
    login_frame,
    text="☕",
    font=("Segoe UI", 60),
    bg='white'
).pack(pady=(0, 5))

Label(
    login_frame,
    text="Coffee Shop",
    font=("Segoe UI", 24, "bold"),
    bg='white',
    fg='#2d3748'
).pack()

Label(
    login_frame,
    text="Database Management System",
    font=("Segoe UI", 12),
    bg='white',
    fg='#718096'
).pack(pady=(0, 30))

# Username
Label(
    login_frame,
    text="Username",
    font=("Segoe UI", 11, "bold"),
    bg='white',
    fg='#2d3748',
    anchor=W
).pack(fill=X, pady=(0, 5))

username_entry = Entry(
    login_frame,
    font=("Segoe UI", 12),
    bg='#f7fafc',
    relief=FLAT,
    bd=2,
    highlightthickness=2,
    highlightcolor='#667eea',
    highlightbackground='#e2e8f0'
)
username_entry.pack(fill=X, pady=(0, 20), ipady=8)
username_entry.insert(0, "admin")

# Password
Label(
    login_frame,
    text="Password",
    font=("Segoe UI", 11, "bold"),
    bg='white',
    fg='#2d3748',
    anchor=W
).pack(fill=X, pady=(0, 5))

password_entry = Entry(
    login_frame,
    font=("Segoe UI", 12),
    bg='#f7fafc',
    show="•",
    relief=FLAT,
    bd=2,
    highlightthickness=2,
    highlightcolor='#667eea',
    highlightbackground='#e2e8f0'
)
password_entry.pack(fill=X, pady=(0, 20), ipady=8)
password_entry.insert(0, "1234")

# Login button with gradient effect
login_btn = Button(
    login_frame,
    text="🔑 Login",
    font=("Segoe UI", 13, "bold"),
    bg='#667eea',
    fg='white',
    relief=FLAT,
    cursor='hand2',
    padx=20,
    pady=12,
    command=login
)
login_btn.pack(fill=X, pady=(0, 15))


# Hover effect
def on_enter(e):
    login_btn.config(bg='#5a67d8')


def on_leave(e):
    login_btn.config(bg='#667eea')


login_btn.bind('<Enter>', on_enter)
login_btn.bind('<Leave>', on_leave)

# Result label
result_label = Label(
    login_frame,
    text="",
    font=("Segoe UI", 10),
    bg='white'
)
result_label.pack()

# Footer
Label(
    login_frame,
    text="Default credentials: admin / 1234",
    font=("Segoe UI", 8),
    bg='white',
    fg='#a0aec0'
).pack(pady=(20, 0))

# ===== BIND KEYBOARD SHORTCUTS =====
root.bind('<Key>', on_key_press)

# ===== START APPLICATION =====
if __name__ == "__main__":
    root.mainloop()