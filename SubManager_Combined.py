import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors

# Database connection (using original SubManager.py database path)
connection = sqlite3.connect("Desktop/NEA Test/DB_Login_Test.db")
cursor = connection.cursor()

# Only create user table for login system (don't touch existing tables)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        userid INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        firstname TEXT,
        surname TEXT
    )""")
connection.commit()

class HoverInfo:
    def __init__(self, widget, text, background="#FFF9C4", borderwidth=1, relief="solid", font=("Arial", 10)):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.background = background
        self.borderwidth = borderwidth
        self.relief = relief
        self.font = font
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root+20}+{event.y_root+10}")
        label = tk.Label(self.tooltip, text=self.text, background=self.background,
                        relief=self.relief, borderwidth=self.borderwidth, font=self.font)
        label.pack()

    def on_leave(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Subscription Manager")
        self.geometry("600x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {
            "Login": LoginFrame(self),
            "SignUp": SignUpFrame(self),
            "Welcome": WelcomeFrame(self),
            "ExpenseInsights": ExpenseInsightsFrame(self),
            "ViewSubscriptions": ViewSubscriptionsFrame(self),
            "Alerts_Reminders": Alerts_RemindersFrame(self)
        }

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame("Login")

    def showFrame(self, pageName):
        self.frames[pageName].tkraise()

class LoginFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self.label = tk.Label(self, text="Subscription Manager Login", font=("Arial", 16))
        self.label.grid(column=1, row=1, pady=10, columnspan=2)

        tk.Label(self, text="Username:").grid(row=2, column=1, sticky="e", padx=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=2, column=2, padx=5, pady=5)

        tk.Label(self, text="Password:").grid(row=3, column=1, sticky="e", padx=5)
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.grid(row=3, column=2, padx=5, pady=5)

        tk.Button(self, text="Login", command=self.attempt_login).grid(row=4, column=2, pady=10)
        tk.Button(self, text="Create Account", command=lambda: container.showFrame("SignUp")).grid(row=5, column=2)

    def attempt_login(self):
        if self.validate_fields() and self.check_credentials():
            self.master.showFrame("Welcome")

    def validate_fields(self):
        if not self.username_entry.get() or not self.password_entry.get():
            messagebox.showerror("Error", "All fields required")
            return False
        return True

    def check_credentials(self):
        cursor.execute("SELECT password FROM User WHERE username=?", (self.username_entry.get(),))
        result = cursor.fetchone()
        if not result or result[0] != self.password_entry.get():
            messagebox.showerror("Error", "Invalid credentials")
            return False
        return True

class SignUpFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self.label = tk.Label(self, text="Create New Account", font=("Arial", 16))
        self.label.grid(column=1, row=1, pady=10, columnspan=2)

        fields = [
            ("First Name:", 2), ("Last Name:", 3),
            ("Username:", 4), ("Password:", 5), ("Confirm Password:", 6)
        ]
        
        self.entries = {}
        for text, row in fields:
            tk.Label(self, text=text).grid(row=row, column=1, sticky="e", padx=5)
            entry = tk.Entry(self, show='*' if "password" in text.lower() else None)
            entry.grid(row=row, column=2, padx=5, pady=5)
            self.entries[text.split(":")[0].strip().lower().replace(" ", "_")] = entry

        tk.Button(self, text="Register", command=self.register_user).grid(row=7, column=2, pady=10)
        tk.Button(self, text="Back to Login", command=lambda: container.showFrame("Login")).grid(row=8, column=2)

    def register_user(self):
        if self.validate_form():
            cursor.execute("""
                INSERT INTO User (username, password, firstname, surname)
                VALUES (?, ?, ?, ?)
            """, (
                self.entries['username'].get(),
                self.entries['password'].get(),
                self.entries['first_name'].get(),
                self.entries['last_name'].get()
            ))
            connection.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            self.master.showFrame("Login")

    def validate_form(self):
        if any(len(entry.get()) == 0 for entry in self.entries.values()):
            messagebox.showerror("Error", "All fields required")
            return False
            
        if self.entries['password'].get() != self.entries['confirm_password'].get():
            messagebox.showerror("Error", "Passwords do not match")
            return False
            
        cursor.execute("SELECT username FROM User WHERE username=?", (self.entries['username'].get(),))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return False
            
        return True
    
class WelcomeFrame(tk.Frame):
  def __init__(self, container):
    super().__init__(container)

    # Configure grid weights for responsive layout
    self.columnconfigure(0, weight=1)
    self.columnconfigure(1, weight=1)
    self.columnconfigure(2, weight=1)

    # Add padding around the frame
    self.configure(padx=20, pady=20)

    # Welcome Header
    header_frame = tk.Frame(self)
    header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 30), sticky="ew")
    header_frame.columnconfigure(0, weight=1)

    welcome_label = tk.Label(
        header_frame,
        text="Welcome to Subscription Manager",
        font=("Arial", 24, "bold"),
        foreground="#2C3E50"
    )
    welcome_label.grid(row=0, column=0, pady=(0, 10))

    subtitle_label = tk.Label(
        header_frame,
        text="Manage your subscriptions efficiently and track your expenses",
        font=("Arial", 12),
        foreground="#7F8C8D"
    )
    subtitle_label.grid(row=1, column=0)

    # Create card frames for each section
    self.create_card(
        0,
        "View Subscriptions",
        "Manage and track all your active subscriptions",
        "📋",
        lambda: container.showFrame("ViewSubscriptions")
    )

    self.create_card(
        1,
        "Expense Insights",
        "Analyse your subscription spending patterns",
        "📊",
        lambda: container.showFrame("ExpenseInsights")
    )

    self.create_card(
        2,
        "Alerts & Reminders",
        "Stay updated with billing cycles and renewals",
        "🔔",
        lambda: container.showFrame("Alerts_Reminders")
    )

    # Add quick summary stats
    summary_frame = tk.Frame(self, relief="solid", borderwidth=1)
    summary_frame.grid(row=2, column=0, columnspan=3, pady=(30, 0), sticky="ew", padx=20)
    summary_frame.configure(bg="#F8F9FA")

    # Get summary data from database
    cursor.execute("""
        SELECT
            COUNT(*) as total_subs,
            SUM(CASE
                WHEN cost LIKE '£%' THEN CAST(REPLACE(REPLACE(cost, '£', ''), ',', '') AS DECIMAL(10,2))
                ELSE CAST(cost AS DECIMAL(10,2))
            END) as total_cost
        FROM Subscription
    """)
    total_subs, total_cost = cursor.fetchone()

    # Display summary stats
    stats_label = tk.Label(
        summary_frame,
        text=f"Quick Summary: {total_subs} Active Subscriptions | Total Monthly Cost: £{total_cost:.2f}",
        font=("Arial", 15),
        bg="#F8F9FA",
        fg="#2C3E50",
        pady=15
    )
    stats_label.pack(expand=True)

  def create_card(self, col, title, description, emoji, command):
    """Creates a styled card widget with hover effect"""
    card = tk.Frame(self, relief="solid", borderwidth=1)
    card.grid(row=1, column=col, padx=10, sticky="nsew")
    card.configure(bg="white")

    # Store references as instance attributes
    card.child_widgets = []

    # Emoji icon
    emoji_label = tk.Label(
        card,
        text=emoji,
        font=("Arial", 32),
        bg="white"
    )
    emoji_label.pack(pady=(20, 10))
    card.child_widgets.append(emoji_label)

    # Title
    title_label = tk.Label(
        card,
        text=title,
        font=("Arial", 14, "bold"),
        bg="white",
        fg="#2C3E50"
    )
    title_label.pack(pady=(0, 10))
    card.child_widgets.append(title_label)

    # Description
    desc_label = tk.Label(
        card,
        text=description,
        font=("Arial", 10),
        bg="white",
        fg="#7F8C8D",
        wraplength=200
    )
    desc_label.pack(pady=(0, 20))
    card.child_widgets.append(desc_label)

    # Button
    button = tk.Button(
        card,
        text="Open",
        command=command,
        relief="solid",
        bg="#3498DB",
        fg="white",
        width=15,
        cursor="hand2"
    )
    button.pack(pady=(0, 20))
    card.child_widgets.append(button)

    # Bind hover events directly to the card
    card.bind("<Enter>", self.on_card_enter)
    card.bind("<Leave>", self.on_card_leave)

  def on_card_enter(self, event):
    card = event.widget
    card.configure(bg="#E6E6E6")
    for widget in card.child_widgets:
        widget.configure(bg="#E6E6E6")

  def on_card_leave(self, event):
    card = event.widget
    card.configure(bg="white")
    for widget in card.child_widgets:
        widget.configure(bg="white")




class ExpenseInsightsFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.configure(bg="#FFFFFF")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Control Panel
        control_panel = tk.Frame(self, bg="#FFFFFF")
        control_panel.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        control_panel.columnconfigure(1, weight=1)

        # Title
        title_label = tk.Label(
            control_panel,
            text="Expense Insights & Analytics",
            font=("Arial", 18, "bold"),
            fg="#2C3E50",
            bg="#FFFFFF"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=(0, 20))

        # Year Filter
        self.year_var = tk.StringVar(value="All Years")
        self.year_dropdown = ttk.Combobox(
            control_panel,
            textvariable=self.year_var,
            state="readonly",
            width=12,
            font=("Arial", 12)
        )
        self.year_dropdown.grid(row=0, column=1, sticky="e")
        self.year_dropdown.bind("<<ComboboxSelected>>", self.update_visualization)

        # Visualization Area
        self.viz_frame = tk.Frame(self, bg="#FFFFFF")
        self.viz_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.viz_frame.columnconfigure(0, weight=1)
        self.viz_frame.rowconfigure(0, weight=1)

        # Back Button
        back_button = tk.Button(
            self,
            text="← Back to Welcome",
            command=lambda: container.showFrame("Welcome"),
            bg="#3498DB",
            fg="black",
            relief="solid",
            borderwidth = 1
        )
        back_button.grid(row=2, column=0, pady=10)

        # Initialize Plot
        plt.switch_backend('TkAgg')
        self.fig, self.ax = plt.subplots(figsize=(12, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=20, pady=20)

        # Initial Load
        self.available_years = self.get_available_years()
        self.year_dropdown['values'] = ["All Years"] + sorted(self.available_years, reverse=True)
        self.update_visualization()

    def get_available_years(self):
        """Get distinct years from database"""
        try:
            cursor.execute("""
                SELECT DISTINCT strftime('%Y', 
                    substr(nextBillingDate, 7, 4) || '-' || 
                    substr(nextBillingDate, 4, 2) || '-' || 
                    substr(nextBillingDate, 1, 2)
                ) as year
                FROM Subscription
                WHERE nextBillingDate IS NOT NULL
                ORDER BY year DESC
            """)
            return [str(row[0]) for row in cursor.fetchall()]
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load years: {str(e)}")
            return []

    def update_visualization(self, event=None):
        """Update the bar chart with stable tooltips"""
        local_conn = None
        try:
            # Clear previous elements
            for widget in self.viz_frame.winfo_children():
                widget.destroy()

            # Create new figure with expanded width
            fig = plt.Figure(figsize=(20, 9), dpi=100)
            ax = fig.add_subplot(111)

            # Database connection and query
            local_conn = sqlite3.connect("Desktop/NEA Test/DB_Login_Test.db")
            local_cursor = local_conn.cursor()

            sql = """
                SELECT 
                    strftime('%Y-%m', 
                        substr(nextBillingDate, 7, 4) || '-' || 
                        substr(nextBillingDate, 4, 2) || '-' || 
                        substr(nextBillingDate, 1, 2)
                    ) as month,
                    SUM(CAST(REPLACE(REPLACE(cost, '£', ''), ',', '') AS REAL)) as total
                FROM Subscription
                WHERE nextBillingDate IS NOT NULL 
                AND cost IS NOT NULL 
            """
            params = []
            if self.year_var.get() != "All Years":
                sql += " AND strftime('%Y', substr(nextBillingDate, 7, 4) || '-' || substr(nextBillingDate, 4, 2) || '-' || substr(nextBillingDate, 1, 2)) = ?"
                params.append(self.year_var.get())
            
            sql += " GROUP BY month ORDER BY month"
            local_cursor.execute(sql, params)
            results = local_cursor.fetchall()

            # Process data
            dates = []
            amounts = []
            for row in results:
                if row[0]:
                    dates.append(datetime.strptime(row[0], "%Y-%m"))
                    amounts.append(float(row[1]))

            if dates and amounts:
                bars = ax.bar(dates, amounts, width=20, color='#3498DB', edgecolor='black')

                cursor = mplcursors.cursor(bars, hover=True)
                
                @cursor.connect("add")
                def _(sel):
                    # Get bar dimensions
                    bar = sel.artist.patches[sel.index]
                    x = bar.get_x()
                    width = bar.get_width()
                    height = bar.get_height()
                    
                    # Calculate fixed position (center top of bar)
                    mid_x = x + width/2
                    mid_y = height * 1.02  # Just above the bar
                    
                    # Format display text
                    bar_date = mdates.num2date(mid_x).strftime('%b %Y')
                    formatted_value = f"£{height:,.2f}"
                    
                    # Set annotation properties
                    sel.annotation.xy = (mid_x, mid_y)
                    sel.annotation.set(text=f"{formatted_value}\n{bar_date}")
                    sel.annotation.get_bbox_patch().set(
                        fc="white", 
                        alpha=0.9,
                        boxstyle="round,pad=0.3"
                    )
                    sel.annotation.arrow_patch.set_visible(False)  # Remove arrow

            if self.year_var.get() == "All Years":
                # Major ticks: Months
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Short month
                plt.setp(ax.xaxis.get_majorticklabels(), 
                        rotation=0,
                        ha='center',
                        fontsize=10,
                        va='bottom')
                
                # Minor ticks: Years
                ax.xaxis.set_minor_locator(mdates.YearLocator())
                ax.xaxis.set_minor_formatter(mdates.DateFormatter('%Y'))
                plt.setp(ax.xaxis.get_minorticklabels(),
                        rotation=0,
                        ha='center',
                        fontsize=8,
                        color='#666666',  # Gray color for years
                        va='top')
                
                # Adjust spacing and padding
                fig.subplots_adjust(bottom=0.25)
                ax.tick_params(axis='x', which='major', pad=25)  # More space below months
                ax.tick_params(axis='x', which='minor', pad=5)   # Less space below years

            else:
                # Single year formatting
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                plt.setp(ax.xaxis.get_majorticklabels(), 
                        rotation=0,
                        ha='center',
                        fontsize=12)

            # Universal styling
            ax.set_ylabel("Monthly Cost (£)", fontsize=12, labelpad=10)
            ax.set_xlabel("Billing Period", fontsize=12, labelpad=15)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"£{x:,.2f}"))
            ax.set_ylim(0, max(amounts) * 1.1)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.set_title(f"Subscription Expenses Analysis ({self.year_var.get()})", fontsize=16)
            fig.tight_layout()

            # Embed plot
            canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill='both')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate visualization: {str(e)}")
        finally:
            if local_conn:
                local_conn.close()






class ViewSubscriptionsFrame(tk.Frame):
  def __init__(self, container):
    super().__init__(container)
    self.columnconfigure(1, weight=1)
    self.rowconfigure(4, weight=1)  # Changed from row 3 to 4

    # Header
    self.label = tk.Label(self, text="View Subscriptions", font=("Arial", 16, "bold"))
    self.label.grid(column=0, row=0, columnspan=5, pady=(10, 20), sticky="ew")

    # Button frame (top controls)
    button_frame = tk.Frame(self)
    button_frame.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(0, 10))
    
    # Navigation button
    self.Welcome_button = tk.Button(button_frame, text="← Back", 
                                    command=lambda: container.showFrame("Welcome"))
    self.Welcome_button.pack(side=tk.LEFT, padx=5)

    # Spacer
    tk.Frame(button_frame, width=20).pack(side=tk.LEFT)

    # Primary action buttons
    self.Add_button = tk.Button(button_frame, text="+ Add Subscription", 
                                command=self.create_subscription_modal)
    self.Add_button.pack(side=tk.LEFT, padx=5)

    self.Edit_button = tk.Button(button_frame, text="🖋 Edit", 
                                command=self.create_edit_modal, state=tk.DISABLED)
    self.Edit_button.pack(side=tk.LEFT, padx=5)

    self.Delete_button = tk.Button(button_frame, text="🗑 Delete", 
                                    command=self.delete_subscription, state=tk.DISABLED)
    self.Delete_button.pack(side=tk.LEFT, padx=5)

    # Filter/Search controls frame
    controls_frame = tk.Frame(self)
    controls_frame.grid(row=2, column=0, columnspan=5, sticky="ew", pady=5)

    # Filter Button (left side)
    self.Filter_button = tk.Button(controls_frame, text="🔍 Filter", 
                                    command=self.create_filter_modal)
    self.Filter_button.pack(side=tk.LEFT, padx=5)

    # Refresh Button
    self.Refresh_button = tk.Button(controls_frame, text="↻ Refresh", 
                                    command=self.refresh_treeview)
    self.Refresh_button.pack(side=tk.LEFT, padx=5)

    # Search (right side)
    search_frame = tk.Frame(controls_frame)
    search_frame.pack(side=tk.RIGHT, padx=5)
    
    tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
    self.search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=25)
    search_entry.pack(side=tk.LEFT)
    search_entry.bind("<KeyRelease>", self.handle_search)

    # Treeview (moved to row 3)
    tree_frame = tk.Frame(self)
    tree_frame.grid(row=3, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)
    tree_frame.columnconfigure(0, weight=1)
    tree_frame.rowconfigure(0, weight=1)

    self.tree = ttk.Treeview(tree_frame)
    self.tree.grid(row=0, column=0, sticky="nsew")

    # Vertical Scrollbar
    vscrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
    vscrollbar.grid(row=0, column=1, sticky="ns")
    self.tree.configure(yscrollcommand=vscrollbar.set)

    # Horizontal Scrollbar
    hscrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
    hscrollbar.grid(row=1, column=0, sticky="ew")
    self.tree.configure(xscrollcommand=hscrollbar.set)

    self.tree["columns"] = ('subscriptionName', 'cost', 'brandName', 'folderName', 'billingCycle', 'nextBillingDate')
    self.tree.column('#0', width=100)
    self.tree.column('subscriptionName', width=100)
    self.tree.column('cost', width=100)
    self.tree.column('brandName', width=100)
    self.tree.column('folderName', width=115)
    self.tree.column('billingCycle', width=100)
    self.tree.column('nextBillingDate', width=100)

    # Set the column headings
    self.tree.heading('#0', text='Subscription ID')
    self.tree.heading('subscriptionName', text='Name')
    self.tree.heading('cost', text='Cost')
    self.tree.heading('brandName', text='Brand')
    self.tree.heading('folderName', text='Folder Type')
    self.tree.heading('billingCycle', text='Billing Cycle')
    self.tree.heading('nextBillingDate', text='Billing Date')

    self.populate_tree()

    self.filter_modal = None

    self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)



  def binary_search_prefix(self, prefix):
    """Find first occurrence of prefix using binary search"""
    low = 0
    high = len(self.sorted_subs) - 1
    prefix = prefix.lower()
    first_match = -1
    
    while low <= high:
        mid = (low + high) // 2
        current_name = self.sorted_subs[mid][1].lower()
        
        if current_name.startswith(prefix):
            first_match = mid
            high = mid - 1  # Look for earlier matches
        elif current_name < prefix:
            low = mid + 1
        else:
            high = mid - 1
            
    return first_match


  def merge_sort(self, arr):
    """Merge sort implementation for subscription names"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = self.merge_sort(arr[:mid])
    right = self.merge_sort(arr[mid:])
    
    return self.merge(left, right)

  def merge(self, left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i][1].lower() < right[j][1].lower():  # Compare names
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result  
  
  
  
  def populate_tree(self):
    self.refresh_treeview()



  def refresh_treeview(self):
    # Clear existing items
    for item in self.tree.get_children():
        self.tree.delete(item)

    # Fetch raw data
    cursor.execute("""
        SELECT s.subscriptionid, s.subscriptionName, s.cost, 
               b.brandName, f.folderName, s.billingCycle, s.nextBillingDate
        FROM Subscription s
        INNER JOIN Brand b ON s.brandid = b.brandid
        INNER JOIN Folder f ON s.folderid = f.folderid
    """)
    raw_data = cursor.fetchall()
    
    # Sort using merge sort
    self.sorted_subs = self.merge_sort(raw_data)
    
    # Store for binary search
    self.all_subscriptions = self.sorted_subs
    
    # Insert into treeview
    for row in self.sorted_subs:
        self.tree.insert('', 'end', text=row[0], values=row[1:])

  def handle_search(self, event):
    search_term = self.search_var.get().strip().lower()
    
    # Clear current items
    for item in self.tree.get_children():
        self.tree.delete(item)
    
    if not search_term:
        self.refresh_treeview()
        return
    
    # Binary search for prefix
    first_index = self.binary_search_prefix(search_term)
    
    if first_index == -1:
        return  # No matches
    
    # Collect all matches
    matches = []
    current_index = first_index
    while current_index < len(self.sorted_subs):
        sub_name = self.sorted_subs[current_index][1].lower()
        if sub_name.startswith(search_term):
            matches.append(self.sorted_subs[current_index])
            current_index += 1
        else:
            break
    
    # Display matches
    for sub in matches:
        self.tree.insert('', 'end', text=sub[0], values=sub[1:])


  def on_tree_select(self, event):
    selected_items = self.tree.selection()
    if selected_items:
        self.Edit_button['state'] = tk.NORMAL
        self.Delete_button['state'] = tk.NORMAL
    else:
        self.Edit_button['state'] = tk.DISABLED
        self.Delete_button['state'] = tk.DISABLED

  def delete_subscription(self):
    selected_items = self.tree.selection()
    if not selected_items:
        messagebox.showerror("Error", "Please select a subscription to delete.")
        return

    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected subscription(s)?"):
        for item in selected_items:
            subscription_id = self.tree.item(item)['text']
            sql = "DELETE FROM Subscription WHERE subscriptionid = ?"
            cursor.execute(sql, (subscription_id,))

        connection.commit()
        self.refresh_treeview()
        messagebox.showinfo("Success", "Subscription(s) deleted successfully.")
    
    connection.commit()
    self.refresh_treeview()  # Triggers merge sort


  def create_edit_modal(self):
    selected_items = self.tree.selection()

    # Defensive programming: Check if any item is selected
    if not selected_items:
        messagebox.showerror("Error", "Please select a subscription to edit.")
        return

    # Handle multiple selections: Only edit the first selected item
    if len(selected_items) > 1:
        messagebox.showwarning("Warning", "Multiple items selected. Editing only the first selected subscription.")

    item = selected_items[0]
    values = self.tree.item(item, 'values')
    subscription_id = self.tree.item(item, 'text')

    edit_modal = tk.Toplevel(self)
    edit_modal.title("Edit Subscription")
    edit_modal.geometry("500x500+400+200")
    edit_modal.resizable(False, False)

    # Edit Subscription Name
    label = tk.Label(edit_modal, text="Edit Subscription Name:")
    label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    self.edit_subscription_name_box = tk.Entry(edit_modal)
    self.edit_subscription_name_box.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    self.edit_subscription_name_box.insert(0, values[0])  # Subscription Name

    # Edit Subscription Cost
    label = tk.Label(edit_modal, text="Edit Subscription Cost:")
    label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    self.edit_subscription_cost_box = tk.Entry(edit_modal)
    self.edit_subscription_cost_box.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
    self.edit_subscription_cost_box.insert(0, values[1])  # Cost

    # Edit Brand
    label = tk.Label(edit_modal, text="Edit Subscription Brand:")
    label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
    self.edit_brand_box = tk.Entry(edit_modal)
    self.edit_brand_box.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
    self.edit_brand_box.insert(0, values[2])  # Brand

    # Edit Folder Type
    label = tk.Label(edit_modal, text="Edit Folder Type:")
    label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
    self.edit_folder_type_box = tk.Entry(edit_modal)
    self.edit_folder_type_box.grid(row=7, column=0, padx=10, pady=5, sticky="ew")
    self.edit_folder_type_box.insert(0, values[3])  # Folder Type

    # Edit Billing Cycle
    label = tk.Label(edit_modal, text="Edit Billing Cycle:")
    label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
    self.edit_billing_cycle_combobox = ttk.Combobox(edit_modal, width=27, state="readonly")
    self.edit_billing_cycle_combobox.grid(row=9, column=0, padx=10, pady=5, sticky="ew")
    self.edit_billing_cycle_combobox['values'] = ('Daily', 'Weekly', 'Monthly', 'Yearly', 'Custom')
    self.edit_billing_cycle_combobox.set(values[4])  # Billing Cycle
    self.edit_billing_cycle_combobox.bind("<<ComboboxSelected>>", self.on_edit_billing_cycle_select)

    # Edit Billing Date
    label = tk.Label(edit_modal, text="Edit Billing Date:")
    label.grid(row=10, column=0, padx=10, pady=5, sticky="w")
    self.edit_billing_date_box = tk.Entry(edit_modal)
    self.edit_billing_date_box.grid(row=11, column=0, padx=10, pady=5, sticky="ew")
    self.edit_billing_date_box.insert(0, values[5])  # Billing Date

    # Update Button
    update_button = tk.Button(edit_modal, text="Update",
                            command=lambda: self.edit_data(subscription_id, edit_modal))
    update_button.grid(row=12, column=0, padx=10, pady=20)

    edit_modal.transient(self.master)
    edit_modal.grab_set()
    self.wait_window(edit_modal)



  def edit_data(self, subscription_id, edit_modal):
    try:
        subscription = self.edit_subscription_name_box.get().strip()
        subscription_cost = self.edit_subscription_cost_box.get().strip()
        brand = self.edit_brand_box.get().strip()
        folder_type = self.edit_folder_type_box.get().strip()
        billing_cycle = self.edit_billing_cycle_combobox.get().strip()
        billing_date = self.edit_billing_date_box.get().strip()

        # Basic validation
        if not all([subscription, subscription_cost, brand, folder_type, billing_cycle, billing_date]):
            messagebox.showerror("Error", "All fields must be filled")
            return

        # Validate cost format
        if subscription_cost.startswith('£'):
            subscription_cost = subscription_cost[1:]
        try:
            cost_float = float(subscription_cost)
            if cost_float <= 0:
                raise ValueError
            subscription_cost = f"£{cost_float:.2f}"
        except ValueError:
            messagebox.showerror("Error", "Invalid cost format")
            return

        # Validate date format
        try:
            billing_date_obj = datetime.strptime(billing_date, "%d/%m/%Y").date()
            if billing_date_obj <= date.today():
                messagebox.showerror("Error", "Billing date must be in the future")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use DD/MM/YYYY")
            return

        # Get or create folder and brand IDs
        folderid = self.insert_or_get_folder(folder_type)
        brandid = self.insert_or_get_brand(brand)

        # Update the subscription
        sql = """
        UPDATE Subscription
        SET subscriptionName = ?, cost = ?, brandid = ?, folderid = ?, billingCycle = ?, nextBillingDate = ?
        WHERE subscriptionid = ?
        """
        cursor.execute(sql, (subscription, subscription_cost, brandid, folderid,
                           billing_cycle, billing_date, subscription_id))
        connection.commit()

        self.refresh_treeview()
        messagebox.showinfo("Success", "Subscription updated successfully!")
        edit_modal.destroy()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while updating the subscription: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    connection.commit()
    self.refresh_treeview()  # Triggers merge sort

  def create_subscription_modal(self):
    modal = tk.Toplevel(self)

    modal.title("Add Subscription")

    modal.geometry("500x500+400+200")

    modal.resizable(False, False)


    # Make modal a child of main window and grab focus

    modal.transient(self.master)  # Set main window as parent
    modal.grab_set()  # Make modal take all focus

    # Subscription Name
    label = tk.Label(modal, text="Add a Subscription Name:")

    label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    self.subscription_name_box = tk.Entry(modal)

    self.subscription_name_box.grid(row=1, column=0, padx=10, pady=5, sticky="ew")



    # Subscription Cost

    label = tk.Label(modal, text="Add a Subscription Cost:")

    label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    self.subscription_cost_box = tk.Entry(modal)

    self.subscription_cost_box.grid(row=3, column=0, padx=10, pady=5, sticky="ew")



    # Brand

    label = tk.Label(modal, text="Add a Subscription Brand:")

    label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

    self.brand_box = tk.Entry(modal)

    self.brand_box.grid(row=5, column=0, padx=10, pady=5, sticky="ew")



    # Folder Type with Info Icon
    folder_frame = tk.Frame(modal)  # Create a frame to hold the label and the info icon
    folder_frame.grid(row=6, column=0, padx=10, pady=5, sticky="w")  # Position the frame

    # Label for Folder Type
    label = tk.Label(folder_frame, text="Add a Folder Type:")
    label.grid(row=0, column=0, sticky="w")  # Align the label to the left

    # Info icon next to the label, smaller size
    info_icon = tk.Label(folder_frame, text="?", font='Helvetica 12 bold', background="#0078D7", foreground="white", width=2, height=1)
    info_icon.grid(row=0, column=1, padx=(5, 0), sticky="w")  # Place the icon next to the label with a small padding

    # Attach the hover tooltip to the info icon
    HoverInfo(info_icon, "Folder Type is used to categorise subscriptions into different folders. (e.g. Entertainment, Utilities, Health and Wellbeing) ")

    # Folder Type Entry Box
    self.folder_type_box = tk.Entry(modal)
    self.folder_type_box.grid(row=7, column=0, padx=10, pady=5, sticky="ew")


    # Billing Cycle

    label = tk.Label(modal, text="Add a Billing Cycle:")

    label.grid(row=8, column=0, padx=10, pady=5, sticky="w")

    self.billing_cycle_combobox = ttk.Combobox(modal, width=27, state = "readonly")

    self.billing_cycle_combobox.grid(row=9, column=0, padx=10, pady=5, sticky="ew")

    self.billing_cycle_combobox['values'] = ('Daily', 'Weekly', 'Monthly', 'Yearly', 'Custom')

    # Billing Date

    label = tk.Label(modal, text="Add a Billing Date:")

    label.grid(row=10, column=0, padx=10, pady=5, sticky="w")

    self.billing_date_box = tk.Entry(modal)

    self.billing_date_box.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

    # Save Button

    save_button = tk.Button(modal, text="Save", command=self.save_data)

    save_button.grid(row=12, column=0, padx=10, pady=20)

    modal.grab_set()

    self.wait_window(modal)



   # self.label = tk.Label(self, text = "Subscription 1   £xxxx.xx   Today", borderwidth =2, relief = "solid")

    #self.label.grid(column = 0, row = 3, sticky = 'nsew', columnspan = 2)


  def handle_custom_billing_cycle_modal(self, is_edit_mode=False):
    """
    Create a modal for setting a custom billing cycle

    Args:
        is_edit_mode (bool): Determines which modal's combobox to update
    """
    # Determine the parent modal and combobox based on mode
    if is_edit_mode:
        parent_modal = self.edit_billing_cycle_combobox.master.master
        combobox = self.edit_billing_cycle_combobox
    else:
        parent_modal = self.billing_cycle_combobox.master.master
        combobox = self.billing_cycle_combobox

    # Create custom cycle window
    custom_cycle_window = tk.Toplevel(parent_modal)
    custom_cycle_window.title("Custom Billing Cycle")
    custom_cycle_window.geometry("400x200")
    custom_cycle_window.grid_columnconfigure(0, weight=1)
    custom_cycle_window.grid_columnconfigure(1, weight=1)

    # Set up proper window hierarchy
    custom_cycle_window.transient(parent_modal)
    custom_cycle_window.grab_set()

    # Label
    label = tk.Label(custom_cycle_window, text="Set custom billing cycle:")
    label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    # Frame for spinbox and combobox
    input_frame = tk.Frame(custom_cycle_window)
    input_frame.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

    # Label for "Every"
    every_label = tk.Label(input_frame, text="Every")
    every_label.pack(side=tk.LEFT, padx=(0, 5))

    # Spinbox for number input
    spinbox = ttk.Spinbox(
        input_frame,
        from_=1,
        to=999,
        width=5,
        wrap=True,
        validate="key",
        validatecommand=(custom_cycle_window.register(lambda P: P.isdigit() or P == ""), '%P')
    )
    spinbox.set(1)
    spinbox.pack(side=tk.LEFT, padx=5)

    # Combobox for time unit
    time_unit = ttk.Combobox(
        input_frame,
        values=["day", "week", "month", "year"],
        state="readonly",
        width=10
    )
    time_unit.set("day")
    time_unit.pack(side=tk.LEFT, padx=5)

    def validate_and_set():
        try:
            value = int(spinbox.get())
            if value <= 0:
                raise ValueError("Value must be positive")

            unit = time_unit.get()
            unit_plural = unit + 's' if value > 1 else unit

            cycle_text = f"Every {value} {unit_plural}"
            combobox.set(cycle_text)
            custom_cycle_window.destroy()
            parent_modal.grab_set()
        except ValueError:
            messagebox.showerror("Invalid Input", "Value must be positive")

    # Submit button
    submit_button = tk.Button(
        custom_cycle_window,
        text="Submit",
        command=validate_and_set
    )
    submit_button.grid(row=2, column=0, columnspan=2, pady=20, padx=10, sticky="ew")

    # Cancel button
    cancel_button = tk.Button(
        custom_cycle_window,
        text="Cancel",
        command=lambda: [custom_cycle_window.destroy(), parent_modal.grab_set()]
    )
    cancel_button.grid(row=3, column=0, columnspan=2, pady=(0, 20), padx=10, sticky="ew")



  def on_billing_cycle_select(self, event=None):
    """
    Handle billing cycle selection for new subscription modal
    """
    if self.billing_cycle_combobox.get() == "Custom":
        self.handle_custom_billing_cycle_modal(is_edit_mode=False)



  def on_edit_billing_cycle_select(self, event=None):
    """
    Handle billing cycle selection for edit subscription modal
    """
    if self.edit_billing_cycle_combobox.get() == "Custom":
        self.handle_custom_billing_cycle_modal(is_edit_mode=True)




  def save_data(self):

    subscription = self.subscription_name_box.get()

    subscription_cost = self.subscription_cost_box.get()

    brand = self.brand_box.get()

    folder_type = self.folder_type_box.get()

    billing_cycle = self.billing_cycle_combobox.get()

    billing_date = self.billing_date_box.get()



    if not self.validate_input():
        return

    # Print values (for testing)

    print("Subscription Name:", subscription)

    print("Subscription Cost:", subscription_cost)

    print("Brand:", brand)

    print("Folder Type:", folder_type)

    print("Billing Cycle:", billing_cycle)

    print("Billing Date:", billing_date)



    folderid = self.insert_or_get_folder(folder_type)

    brandid = self.insert_or_get_brand(brand)

    self.insert_subscription(subscription, subscription_cost, brandid, folderid, billing_cycle, billing_date)

    self.refresh_treeview()

    messagebox.showinfo("Success", "Subscription saved successfully!")

    connection.commit()
    self.refresh_treeview()  # Triggers merge sort

  def validate_input(self):
    if self.Empty():
        return False
    if not self.validate_subscription_cost():
        return False
    valid_date, message = self.billing_date_validated()
    if not valid_date:
        messagebox.showerror("Invalid Date", message)
        return False
    return True


  def insert_or_get_folder(self, folder_name):
    cursor.execute("SELECT folderid FROM Folder WHERE folderName = ?", (folder_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute("INSERT INTO Folder (folderName) VALUES (?)", (folder_name,))
        connection.commit()
        return cursor.lastrowid


  def insert_or_get_brand(self, brand_name):
    cursor.execute("SELECT brandid FROM Brand WHERE brandName = ?", (brand_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute("INSERT INTO Brand (brandName) VALUES (?)", (brand_name,))
        connection.commit()
        return cursor.lastrowid

  def insert_subscription(self, name, cost, brand_id, folder_id, billing_cycle, billing_date):

    sql = """
    INSERT INTO Subscription (subscriptionName,cost,brandid,folderid,billingCycle,nextBillingDate) VALUES (?,?,?,?,?,?)
    """
    cursor.execute(sql, (name, cost, brand_id, folder_id, billing_cycle, billing_date))
    connection.commit()




  def validate_subscription_cost(self):
    cost = self.subscription_cost_box.get().strip()

    if cost.startswith('£'):
        cost = cost[1:]


    try:
        cost_float = float(cost)

        if cost_float <= 0:
            raise ValueError("Cost must be positive.")

        cost_float = round(cost_float,2)

        formatted_cost = f"£{cost_float:.2f}"
        self.subscription_cost_box.delete(0,tk.END)
        self.subscription_cost_box.insert(0,formatted_cost)

        return True
    except ValueError:
        tk.messagebox.showerror("Invalid Input", "Please enter a valid number for the subscription cost")
        return False


  def billing_date_validated(self):
    billing_date = self.billing_date_box.get().strip()

    try:
        billing_date = datetime.strptime(billing_date, "%d/%m/%Y").date()

        # Check if billing date is in the past
        if billing_date <= date.today():
            return False, "Billing date must be in the future."

        return True, "Valid billing date"

    except ValueError:
        return False, "Invalid date format, please use DD/MM/YYYY"




  def Empty(self):

    if len(self.billing_cycle_combobox.get()) == 0 or len(self.subscription_name_box.get()) == 0 or len(self.brand_box.get()) == 0 or len(self.folder_type_box.get()) == 0 or len(self.billing_date_box.get()) == 0 or len(self.subscription_cost_box.get()) == 0:

        messagebox.showerror("Error", "Must fill in all fields")

        return True

    else:

        return False



  def create_filter_modal(self):
    self.filter_modal = tk.Toplevel(self)
    self.filter_modal.title("Filter Subscriptions")
    self.filter_modal.geometry("1100x300")
    self.filter_modal.resizable(False, False)
    
    # Configure grid layout
    self.filter_modal.columnconfigure(0, weight=1)
    self.filter_modal.rowconfigure(0, weight=1)
    
    # Filter Criteria Frame
    criteria_frame = tk.Frame(self.filter_modal, padx=20, pady=20)
    criteria_frame.grid(row=0, column=0, sticky="nsew")
    
    # Brand Filter
    tk.Label(criteria_frame, text="Brand:").grid(row=0, column=0, sticky="w")
    self.filter_brand_combobox = ttk.Combobox(criteria_frame, width=25)
    self.filter_brand_combobox.grid(row=1, column=0, sticky="w", padx=5)
    
    # Folder Type Filter
    tk.Label(criteria_frame, text="Folder Type:").grid(row=0, column=1, sticky="w")
    self.filter_folder_type_combobox = ttk.Combobox(criteria_frame, width=25)
    self.filter_folder_type_combobox.grid(row=1, column=1, sticky="w", padx=5)
    
    # Billing Cycle Filter
    tk.Label(criteria_frame, text="Billing Cycle:").grid(row=0, column=2, sticky="w")
    self.filter_billing_cycle_combobox = ttk.Combobox(criteria_frame, width=25)
    self.filter_billing_cycle_combobox.grid(row=1, column=2, sticky="w", padx=5)
    
    # Cost Sorting Filter
    tk.Label(criteria_frame, text="Sort by Cost:").grid(row=0, column=3, sticky="w")
    self.filter_cost_sort_combobox = ttk.Combobox(criteria_frame, 
                                                values=["None", "Highest to Lowest", "Lowest to Highest"],
                                                width=25)
    self.filter_cost_sort_combobox.grid(row=1, column=3, sticky="w", padx=5)
    
    # Populate combobox values
    cursor.execute("SELECT DISTINCT brandName FROM Brand")
    self.filter_brand_combobox['values'] = ["All Brands"] + [b[0] for b in cursor.fetchall()]
    self.filter_brand_combobox.set("All Brands")
    
    cursor.execute("SELECT DISTINCT folderName FROM Folder")
    self.filter_folder_type_combobox['values'] = ["All Folders"] + [f[0] for f in cursor.fetchall()]
    self.filter_folder_type_combobox.set("All Folders")
    
    self.filter_billing_cycle_combobox['values'] = ["All Cycles", "Daily", "Weekly", "Monthly", "Yearly"]
    self.filter_billing_cycle_combobox.set("All Cycles")
    
    self.filter_cost_sort_combobox.set("None")

    # Single Apply Button positioned at bottom-center
    apply_button = tk.Button(self.filter_modal, 
                           text="Apply Filters", 
                           command=self.filter_data,
                           bg="#4CAF50", 
                           fg="black", 
                           width=20,
                           height=2)
    apply_button.place(relx=0.5, rely=0.9, anchor="center")  # Centered at bottom

    # Configure modal behavior
    self.filter_modal.transient(self.master)
    self.filter_modal.grab_set()
    self.filter_modal.protocol("WM_DELETE_WINDOW", self.filter_modal.destroy)

  def filter_data(self):
    # Get filter values
    brand = self.filter_brand_combobox.get()
    folder = self.filter_folder_type_combobox.get()
    billing_cycle = self.filter_billing_cycle_combobox.get()
    cost_sort = self.filter_cost_sort_combobox.get()

    # Build query
    query = """SELECT s.subscriptionid, s.subscriptionName, s.cost, 
                b.brandName, f.folderName, s.billingCycle, s.nextBillingDate
                FROM Subscription s
                INNER JOIN Brand b ON s.brandid = b.brandid
                INNER JOIN Folder f ON s.folderid = f.folderid
                WHERE 1=1"""
    params = []

    # Apply filters
    if brand != "All Brands":
        query += " AND b.brandName = ?"
        params.append(brand)
    
    if folder != "All Folders":
        query += " AND f.folderName = ?"
        params.append(folder)
    
    if billing_cycle != "All Cycles":
        query += " AND s.billingCycle = ?"
        params.append(billing_cycle)

    # Apply cost sorting
    if cost_sort != "None":
        cost_order = "DESC" if "Highest" in cost_sort else "ASC"
        query += f" ORDER BY CAST(REPLACE(REPLACE(s.cost, '£', ''), ',', '') AS DECIMAL) {cost_order}"

    # Execute query
    cursor.execute(query, params)
    filtered_data = cursor.fetchall()

    # Update Treeview
    self.tree.delete(*self.tree.get_children())
    for row in filtered_data:
        self.tree.insert('', 'end', text=row[0], values=row[1:])

    # Close modal
    self.filter_modal.destroy()





class Alerts_RemindersFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        
        # Configure grid weights for responsive layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        # Header
        header_frame = tk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        
        # Title and Navigation
        title_label = tk.Label(
            header_frame,
            text="Alerts & Reminders",
            font=("Arial", 18, "bold"),
            fg="#2C3E50"
        )
        title_label.pack(side=tk.LEFT)
        
        back_button = tk.Button(
            header_frame,
            text="← Back to Welcome",
            command=lambda: container.showFrame("Welcome"),
            bg="#3498DB",
            fg="black",
            relief="solid",
            borderwidth=1
        )
        back_button.pack(side=tk.RIGHT)
        
        # Button Frame
        button_frame = tk.Frame(self)
        button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        # Add Alert Button
        self.add_alert_button = tk.Button(
            button_frame,
            text="+ Create New Alert",
            command=self.create_alert_modal,
            bg="#2ECC71",
            fg="black",
            relief="solid",
            borderwidth=1
        )
        self.add_alert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete Alert Button (initially disabled)
        self.delete_alert_button = tk.Button(
            button_frame,
            text="🗑 Delete Alert",
            command=self.delete_alert,
            state=tk.DISABLED,
            bg="#E74C3C",
            fg="black",
            relief="solid",
            borderwidth=1
        )
        self.delete_alert_button.pack(side=tk.LEFT)
        
        # Create a frame to hold TreeView and Scrollbars
        tree_frame = tk.Frame(self)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for alerts
        self.alerts_tree = ttk.Treeview(tree_frame)
        self.alerts_tree.grid(row=0, column=0, sticky="nsew")
        
        # Vertical Scrollbar
        vscrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.alerts_tree.yview)
        vscrollbar.grid(row=0, column=1, sticky="ns")
        self.alerts_tree.configure(yscrollcommand=vscrollbar.set)
        
        # Horizontal Scrollbar
        hscrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.alerts_tree.xview)
        hscrollbar.grid(row=1, column=0, sticky="ew")
        self.alerts_tree.configure(xscrollcommand=hscrollbar.set)
        
        # Configure Treeview columns
        self.alerts_tree["columns"] = ('subscription', 'alert_date', 'alert_type', 'alert_message')
        self.alerts_tree.column('#0', width=70, minwidth=70)
        self.alerts_tree.column('subscription', width=150, minwidth=100)
        self.alerts_tree.column('alert_date', width=100, minwidth=100)
        self.alerts_tree.column('alert_type', width=100, minwidth=80)
        self.alerts_tree.column('alert_message', width=250, minwidth=150)
        
        # Set column headings
        self.alerts_tree.heading('#0', text='Alert ID')
        self.alerts_tree.heading('subscription', text='Subscription')
        self.alerts_tree.heading('alert_date', text='Alert Date')
        self.alerts_tree.heading('alert_type', text='Alert Type')
        self.alerts_tree.heading('alert_message', text='Message')
        
        # Empty state message
        self.empty_label = tk.Label(
            tree_frame,
            text="No alerts created yet. Click '+ Create New Alert' to add one.",
            font=("Arial", 12),
            fg="#7F8C8D"
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bind selection event
        self.alerts_tree.bind("<<TreeviewSelect>>", self.on_alert_select)
        
        # Store user email for reminders
        self.user_email = ""
        
        # Initialize by loading alerts
        self.create_alert_table_if_not_exists()
        self.load_alerts()

        # Configure Treeview colors
        self.alerts_tree.tag_configure('urgent', background='#ffcccc')  # Red
        self.alerts_tree.tag_configure('warning', background='#ffe6cc')  # Amber
        self.alerts_tree.tag_configure('safe', background='#ccffcc')    # Green

        # Add urgency legend
        legend_frame = tk.Frame(self)
        legend_frame.grid(row=3, column=0, pady=10, sticky="ew")
        
        tk.Label(legend_frame, text="Urgency:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Label(legend_frame, text="<3 days", bg='#ffcccc', width=8).pack(side=tk.LEFT, padx=2)
        tk.Label(legend_frame, text="4-7 days", bg='#ffe6cc', width=8).pack(side=tk.LEFT, padx=2)
        tk.Label(legend_frame, text=">7 days", bg='#ccffcc', width=8).pack(side=tk.LEFT, padx=2)
    
    def create_alert_table_if_not_exists(self):
        """Create the Alert table if it doesn't exist yet"""
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Alert (
                    alertid INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscriptionid INTEGER,
                    alert_date TEXT,
                    alert_type TEXT,
                    alert_message TEXT,
                    FOREIGN KEY (subscriptionid) REFERENCES Subscription(subscriptionid)
                )
            """)
            
            connection.commit()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error creating tables: {str(e)}")
    
    def load_alerts(self):
        """Load alerts from database into treeview"""
        try:
            # Clear existing items FIRST
            self.alerts_tree.delete(*self.alerts_tree.get_children())  # Clear all items
            
            # Execute query to get alerts with subscription names
            cursor.execute("""
                SELECT a.alertid, s.subscriptionName, a.alert_date, a.alert_type, a.alert_message
                FROM Alert a
                JOIN Subscription s ON a.subscriptionid = s.subscriptionid
                ORDER BY a.alert_date ASC
            """)
            
            alerts = cursor.fetchall()
            
            # Show/hide empty state message
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center") if not alerts else self.empty_label.place_forget()
            
            # Insert alerts with color coding
            today = date.today()
            for alert in alerts:
                alert_date = datetime.strptime(alert[2], "%d/%m/%Y").date()
                days_remaining = (alert_date - today).days
            
                # Determine urgency tag
                if days_remaining <= 3:
                    tag = 'urgent'
                elif 4 <= days_remaining <= 7:
                    tag = 'warning'
                else:
                    tag = 'safe'
                
                # Insert with tag
                self.alerts_tree.insert('', 'end', text=alert[0], values=alert[1:], tags=(tag,))
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading alerts: {str(e)}")
    
    def on_alert_select(self, event):
        """Handle tree selection event"""
        selected_items = self.alerts_tree.selection()
        if selected_items:
            self.delete_alert_button['state'] = tk.NORMAL
        else:
            self.delete_alert_button['state'] = tk.DISABLED
    
    def delete_alert(self):
        """Delete selected alert(s) from database"""
        selected_items = self.alerts_tree.selection()
        if not selected_items:
            return
            
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected alert(s)?"):
            try:
                for item in selected_items:
                    alert_id = self.alerts_tree.item(item)['text']
                    cursor.execute("DELETE FROM Alert WHERE alertid = ?", (alert_id,))
                
                connection.commit()
                self.load_alerts()  # Refresh display
                messagebox.showinfo("Success", "Alert(s) deleted successfully")
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete alert: {str(e)}")
    
    def create_alert_modal(self):
        """Create modal dialog for adding a new alert"""
        # Create the top level window
        modal = tk.Toplevel(self)
        modal.title("Create New Alert")
        modal.geometry("500x400+400+200")
        modal.resizable(False, False)
        modal.transient(self.master)  # Set main window as parent
        modal.grab_set()  # Make modal take all focus
        
        # Configure column weights
        modal.columnconfigure(0, weight=1)
        
        # Add a heading
        heading = tk.Label(
            modal,
            text="Create New Alert",
            font=("Arial", 16, "bold"),
            fg="#2C3E50"
        )
        heading.grid(row=0, column=0, pady=(15, 20), sticky="ew")
        
        # Create form frame
        form_frame = tk.Frame(modal)
        form_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        form_frame.columnconfigure(1, weight=1)
        
        # Subscription selection
        label = tk.Label(form_frame, text="Subscription:", anchor="w")
        label.grid(row=0, column=0, pady=5, sticky="w")
        
        self.subscription_combobox = ttk.Combobox(form_frame, state="readonly", width=30)
        self.subscription_combobox.grid(row=0, column=1, pady=5, sticky="ew")
        
        # Populate subscription options
        cursor.execute("SELECT subscriptionid, subscriptionName FROM Subscription ORDER BY subscriptionName")
        subscriptions = cursor.fetchall()
        self.subscription_combobox['values'] = [sub[1] for sub in subscriptions]
        self.subscription_ids = [sub[0] for sub in subscriptions]
        
        if subscriptions:
            self.subscription_combobox.current(0)
        
        # Bind subscription change event
        self.subscription_combobox.bind("<<ComboboxSelected>>", self.on_subscription_change)
        
        # Alert Type
        label = tk.Label(form_frame, text="Alert Type:", anchor="w")
        label.grid(row=1, column=0, pady=5, sticky="w")
        
        self.alert_type_combobox = ttk.Combobox(form_frame, state="readonly", width=30)
        self.alert_type_combobox.grid(row=1, column=1, pady=5, sticky="ew")
        self.alert_type_combobox['values'] = ["Subscription Renewal", "Price Increase", "Custom"]
        self.alert_type_combobox.current(0)
        self.alert_type_combobox.bind("<<ComboboxSelected>>", self.on_alert_type_change)
        
        # Alert Date
        label = tk.Label(form_frame, text="Alert Date:", anchor="w")
        label.grid(row=2, column=0, pady=5, sticky="w")
        
        self.alert_date_entry = tk.Entry(form_frame)
        self.alert_date_entry.grid(row=2, column=1, pady=5, sticky="ew")
        self.alert_date_entry.insert(0, (date.today() + timedelta(days=1)).strftime("%d/%m/%Y"))  # Default to tomorrow
        
        # Date format note
        date_note = tk.Label(
            form_frame, 
            text="Format: DD/MM/YYYY", 
            fg="#7F8C8D", 
            font=("Arial", 8)
        )
        date_note.grid(row=3, column=1, sticky="w")
        
        # Alert Message
        label = tk.Label(form_frame, text="Alert Message:", anchor="w")
        label.grid(row=4, column=0, pady=5, sticky="w")
        
        self.alert_message_text = tk.Text(form_frame, height=4, width=30)
        self.alert_message_text.grid(row=4, column=1, pady=5, sticky="ew")
        
        # Add prebuilt message based on alert type
        self.update_default_message()
        
        # Button frame
        button_frame = tk.Frame(modal)
        button_frame.grid(row=2, column=0, pady=20, sticky="ew")
        
        # Save button
        save_button = tk.Button(
            button_frame,
            text="Save Alert",
            command=lambda: self.save_alert(modal),
            bg="#2ECC71",
            fg="black",
            width=15,
            height=2
        )
        save_button.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=modal.destroy,
            width=15,
            height=2
        )
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        modal.wait_window()
    
    def on_subscription_change(self, event=None):
        """Update default message when subscription changes"""
        self.update_default_message()
    
    def on_alert_type_change(self, event=None):
        """Update default message when alert type changes"""
        self.update_default_message()
    
    def update_default_message(self):
        """Set the default message based on the selected alert type and subscription"""
        alert_type = self.alert_type_combobox.get()
        subscription = self.subscription_combobox.get()
        
        default_messages = {
            "Subscription Renewal": f"Your {subscription} subscription will renew soon.",
            "Price Increase": f"The price for your {subscription} subscription will increase soon.",
            "Custom": ""
        }
        
        # Clear existing text and insert new default message
        self.alert_message_text.delete('1.0', tk.END)
        self.alert_message_text.insert('1.0', default_messages.get(alert_type, ""))
    
    def save_alert(self, modal):
        """Save the alert to database"""
        try:
            # Get values from form
            if not self.subscription_combobox.get():
                messagebox.showerror("Error", "Please select a subscription")
                return
                
            subscription_index = self.subscription_combobox.current()
            subscription_id = self.subscription_ids[subscription_index]
            alert_type = self.alert_type_combobox.get()
            alert_date = self.alert_date_entry.get().strip()
            alert_message = self.alert_message_text.get('1.0', tk.END).strip()
            
            # Validate date
            try:
                alert_date_obj = datetime.strptime(alert_date, "%d/%m/%Y").date()
                today = date.today()
                
                # New validation: Prevent past/today dates
                if alert_date_obj <= today:
                    messagebox.showerror("Error", "Alert date must be in the future")
                    return
                
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY")
                return
                
            # Validate other fields
            if not alert_type or not alert_message:
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            # Insert alert into database
            cursor.execute(
                "INSERT INTO Alert (subscriptionid, alert_date, alert_type, alert_message) VALUES (?, ?, ?, ?)",
                (subscription_id, alert_date, alert_type, alert_message)
            )
            connection.commit()
            
            # Refresh display and close modal
            self.load_alerts()
            modal.destroy()
            messagebox.showinfo("Success", "Alert created successfully!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save alert: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")




if __name__ == "__main__":
    app = Window()
    app.mainloop()