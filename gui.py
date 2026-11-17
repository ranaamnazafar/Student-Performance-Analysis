import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==============================
# PROJECT PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "StudentsPerformance.csv"
CLEANED_DIR = BASE_DIR / "cleaned_data"
GRAPHS_DIR = BASE_DIR / "graphs"

CLEANED_DIR.mkdir(exist_ok=True)
GRAPHS_DIR.mkdir(exist_ok=True)

CLEANED_PATH = CLEANED_DIR / "StudentsPerformance_Cleaned.csv"

df = None
cleaned_df = None
current_canvas = None

# ==============================
# DARK THEME COLORS
# ==============================

BG = "#0B1120"
SIDEBAR = "#111B2E"
PANEL = "#172338"
WHITE = "#FFFFFF"
TEXT = "#F1F5F9"
MUTED = "#9AAAC0"
PURPLE = "#8B5CF6"
CYAN = "#22D3EE"
GREEN = "#34D399"
ORANGE = "#FBBF24"
RED = "#FB7185"

# ==============================
# MAIN WINDOW
# ==============================

root = tk.Tk()
root.title("Student Performance Analysis System")
root.geometry("1200x750")
root.minsize(950, 650)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=PANEL,
    foreground=TEXT,
    fieldbackground=PANEL,
    rowheight=30,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    background="#263650",
    foreground=WHITE,
    font=("Arial", 10, "bold")
)

style.map(
    "Treeview",
    background=[("selected", PURPLE)],
    foreground=[("selected", WHITE)]
)

# ==============================
# MAIN LAYOUT
# ==============================

sidebar = tk.Frame(root, bg=SIDEBAR, width=230)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

main = tk.Frame(root, bg=BG)
main.pack(side="right", fill="both", expand=True)

header = tk.Frame(main, bg=BG, height=75)
header.pack(fill="x", padx=25, pady=15)
header.pack_propagate(False)

tk.Label(
    header,
    text="Student Performance",
    bg=BG,
    fg=TEXT,
    font=("Arial", 20, "bold")
).pack(side="left")

content = tk.Frame(main, bg=BG)
content.pack(fill="both", expand=True, padx=25, pady=15)

status = tk.Label(
    main,
    text="Ready | Load your dataset to begin",
    bg=SIDEBAR,
    fg=MUTED,
    anchor="w",
    padx=15,
    pady=10
)
status.pack(side="bottom", fill="x")

# ==============================
# HELPER FUNCTIONS
# ==============================

def clear_content():
    global current_canvas

    if current_canvas:
        current_canvas.get_tk_widget().destroy()
        current_canvas = None

    for widget in content.winfo_children():
        widget.destroy()


def heading(title, subtitle):
    tk.Label(
        content,
        text=title,
        bg=BG,
        fg=TEXT,
        font=("Arial", 22, "bold")
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        content,
        text=subtitle,
        bg=BG,
        fg=MUTED,
        font=("Arial", 10)
    ).pack(anchor="w", pady=(0, 18))


def make_button(parent, text, command, color=PURPLE):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=WHITE,
        activebackground="#7C3AED",
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=12
    )


# ==============================
# LOAD DATASET
# ==============================

def load_dataset(path=None):
    global df, cleaned_df

    if path is None:
        path = filedialog.askopenfilename(
            title="Select Student Dataset",
            filetypes=[("CSV Files", "*.csv")]
        )

    if not path:
        return

    try:
        new_df = pd.read_csv(path)

        required = [
            "gender",
            "math score",
            "reading score",
            "writing score"
        ]

        for col in required:
            if col not in new_df.columns:
                messagebox.showerror(
                    "Invalid Dataset",
                    "Missing column: " + col
                )
                return

        df = new_df
        cleaned_df = None

        status.config(
            text=f"Dataset Loaded Successfully | {len(df)} Students"
        )

        show_dashboard()

    except Exception as error:
        messagebox.showerror("Loading Error", str(error))


# ==============================
# VIEW DATASET
# ==============================

def show_table(data, title="Student Dataset"):

    clear_content()
    heading(title, "Student records")

    if data is None or data.empty:
        messagebox.showinfo("Information", "No data available.")
        return

    frame = tk.Frame(content, bg=PANEL)
    frame.pack(fill="both", expand=True)

    columns = list(data.columns)

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    yscroll = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    xscroll = ttk.Scrollbar(
        frame,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=yscroll.set,
        xscrollcommand=xscroll.set
    )

    tree.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor="center")

    for _, row in data.iterrows():
        values = [
            "" if pd.isna(v) else str(v)
            for v in row
        ]
        tree.insert("", "end", values=values)

    tk.Label(
        content,
        text=f"Total Records: {len(data)}",
        bg=BG,
        fg=MUTED
    ).pack(anchor="w", pady=8)


# ==============================
# CLEAN DATASET
# ==============================

def clean_data():

    global cleaned_df

    if df is None:
        messagebox.showwarning(
            "Dataset Required",
            "Please load dataset first."
        )
        return

    try:
        work = df.copy()

        duplicates = int(work.duplicated().sum())
        work = work.drop_duplicates().copy()

        # Fill categorical missing values
        for col in work.select_dtypes(
            include=["object", "string"]
        ).columns:

            if work[col].isna().any():
                modes = work[col].mode()

                if not modes.empty:
                    work[col] = work[col].fillna(modes.iloc[0])

        # Clean score columns
        score_cols = [
            "math score",
            "reading score",
            "writing score"
        ]

        for col in score_cols:

            work[col] = pd.to_numeric(
                work[col],
                errors="coerce"
            )

            invalid = (
                (work[col] < 0) |
                (work[col] > 100)
            )

            work.loc[invalid, col] = pd.NA

            median_value = work[col].median()

            if pd.notna(median_value):
                work[col] = work[col].fillna(median_value)

        # Average score
        work["average score"] = (
            work[score_cols].mean(axis=1)
        ).round(2)

        # Pass / Fail
        work["result"] = work["average score"].apply(
            lambda x: "Pass" if x >= 40 else "Fail"
        )

        # Save cleaned CSV
        try:
            work.to_csv(CLEANED_PATH, index=False)
            saved_path = CLEANED_PATH

        except PermissionError:

            messagebox.showwarning(
                "Permission Denied",
                "Close the cleaned CSV if it is open in Excel. "
                "You can also save a new copy."
            )

            alternate = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile="StudentsPerformance_Cleaned_New.csv",
                filetypes=[("CSV Files", "*.csv")]
            )

            if not alternate:
                return

            work.to_csv(alternate, index=False)
            saved_path = Path(alternate)

        cleaned_df = work

        status.config(text="Data Cleaning Completed Successfully")

        messagebox.showinfo(
            "Cleaning Complete",
            f"Data cleaned successfully!\n\n"
            f"Original rows: {len(df)}\n"
            f"Duplicates removed: {duplicates}\n"
            f"Final rows: {len(work)}\n\n"
            f"Saved at:\n{saved_path}\n\n"
            "Pass rule: Average score >= 40"
        )

        show_table(cleaned_df, "Cleaned Student Dataset")

    except Exception as error:
        messagebox.showerror("Cleaning Error", str(error))


# ==============================
# DATA ANALYSIS
# ==============================

def analyze_data():

    if cleaned_df is None:
        messagebox.showwarning(
            "Cleaning Required",
            "Please clean dataset first."
        )
        return

    clear_content()
    heading(
        "Data Analysis",
        "Student performance summary"
    )

    male = (
        cleaned_df["gender"].str.lower() == "male"
    ).sum()

    female = (
        cleaned_df["gender"].str.lower() == "female"
    ).sum()

    passed = (cleaned_df["result"] == "Pass").sum()
    failed = (cleaned_df["result"] == "Fail").sum()

    report = f"""
    TOTAL STUDENTS: {len(cleaned_df)}

    MALE STUDENTS: {male}

    FEMALE STUDENTS: {female}

    PASSED STUDENTS: {passed}

    FAILED STUDENTS: {failed}

    OVERALL AVERAGE: {cleaned_df["average score"].mean():.2f}


    SUBJECT-WISE AVERAGES
    ----------------------------

    Math: {cleaned_df["math score"].mean():.2f}

    Reading: {cleaned_df["reading score"].mean():.2f}

    Writing: {cleaned_df["writing score"].mean():.2f}
    """

    tk.Label(
        content,
        text=report,
        bg=PANEL,
        fg=TEXT,
        font=("Consolas", 12),
        justify="left",
        padx=30,
        pady=25
    ).pack(fill="x", anchor="nw")


# ==============================
# VIEW GRAPHS
# ==============================

def show_graph(graph_type):

    global current_canvas

    if cleaned_df is None:
        messagebox.showwarning(
            "Cleaning Required",
            "Please clean dataset first."
        )
        return

    clear_content()
    heading("Data Visualization", "Student performance charts")

    fig = Figure(
        figsize=(8, 4.5),
        dpi=100,
        facecolor=PANEL
    )

    ax = fig.add_subplot(111)
    ax.set_facecolor(PANEL)

    ax.tick_params(colors=TEXT)

    for spine in ax.spines.values():
        spine.set_color("#334155")

    if graph_type == "gender":

        counts = cleaned_df["gender"].value_counts()

        ax.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"color": TEXT}
        )

        ax.set_title(
            "Gender Distribution",
            color=TEXT
        )

        filename = "gender_distribution.png"

    elif graph_type == "average":

        averages = cleaned_df[
            ["math score", "reading score", "writing score"]
        ].mean()

        ax.bar(
            ["Math", "Reading", "Writing"],
            averages.values,
            color=[PURPLE, CYAN, GREEN]
        )

        ax.set_ylim(0, 110)
        ax.set_title(
            "Average Subject Scores",
            color=TEXT
        )

        filename = "average_subject_scores.png"

    else:

        for col in [
            "math score",
            "reading score",
            "writing score"
        ]:

            ax.hist(
                cleaned_df[col],
                bins=15,
                alpha=0.4,
                label=col
            )

        ax.set_title(
            "Subject Score Distribution",
            color=TEXT
        )

        ax.legend()

        filename = "subject_score_distribution.png"

    fig.tight_layout()

    fig.savefig(
        GRAPHS_DIR / filename,
        facecolor=PANEL
    )

    current_canvas = FigureCanvasTkAgg(
        fig,
        master=content
    )

    current_canvas.draw()

    current_canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )


def show_graph_menu():

    clear_content()
    heading("View Graphs", "Choose a graph")

    options = [
        ("Gender Distribution", lambda: show_graph("gender")),
        ("Average Subject Scores", lambda: show_graph("average")),
        ("Subject Score Distribution", lambda: show_graph("distribution"))
    ]

    for label, command in options:
        make_button(
            content,
            label,
            command
        ).pack(anchor="w", pady=8)


# ==============================
# EXPORT DATA
# ==============================

def export_data():

    if cleaned_df is None:
        messagebox.showwarning(
            "No Cleaned Data",
            "Please clean dataset first."
        )
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile="StudentsPerformance_Cleaned.csv",
        filetypes=[("CSV Files", "*.csv")]
    )

    if path:
        try:
            cleaned_df.to_csv(path, index=False)

            messagebox.showinfo(
                "Export Successful",
                "Cleaned dataset exported successfully!"
            )

        except Exception as error:
            messagebox.showerror("Export Error", str(error))


# ==============================
# DASHBOARD
# ==============================

def show_dashboard():

    clear_content()

    heading(
        "Welcome, Amna!",
        "Your Student Performance Dashboard"
    )

    if df is None:

        make_button(
            content,
            "Load Dataset",
            load_dataset
        ).pack(anchor="w")

        return

    male = (
        df["gender"].str.lower() == "male"
    ).sum()

    female = (
        df["gender"].str.lower() == "female"
    ).sum()

    average = (
        f'{cleaned_df["average score"].mean():.2f}'
        if cleaned_df is not None else "--"
    )

    # Dashboard cards
    cards_frame = tk.Frame(content, bg=BG)
    cards_frame.pack(fill="x", pady=10)

    cards = [
        ("Total Students", len(df),
         lambda: show_table(df, "All Students")),

        ("Female Students", female,
         lambda: show_table(
             df[df["gender"].str.lower() == "female"],
             "Female Students"
         )),

        ("Male Students", male,
         lambda: show_table(
             df[df["gender"].str.lower() == "male"],
             "Male Students"
         )),

        ("Average Score", average,
         analyze_data if cleaned_df is not None else clean_data)
    ]

    for i, (title, value, action) in enumerate(cards):

        card = tk.Button(
            cards_frame,
            text=f"{title}\n\n{value}",
            command=action,
            bg=PANEL,
            fg=CYAN,
            activebackground="#263650",
            activeforeground=WHITE,
            font=("Arial", 13, "bold"),
            relief="flat",
            height=5,
            cursor="hand2"
        )

        card.grid(
            row=0,
            column=i,
            padx=6,
            sticky="nsew"
        )

        cards_frame.columnconfigure(i, weight=1)

    # Quick Actions
    tk.Label(
        content,
        text="Quick Actions",
        bg=BG,
        fg=TEXT,
        font=("Arial", 16, "bold")
    ).pack(anchor="w", pady=(30, 12))

    actions_frame = tk.Frame(content, bg=BG)
    actions_frame.pack(fill="x")

    actions = [
        ("Load Dataset", load_dataset, PURPLE),
        ("View Dataset",
         lambda: show_table(df) if df is not None else None,
         "#0891B2"),
        ("Clean Dataset", clean_data, "#059669"),
        ("Analyze Dataset", analyze_data, "#D97706")
    ]

    for index, (label, command, color) in enumerate(actions):

        button = make_button(
            actions_frame,
            label,
            command,
            color
        )

        button.grid(
            row=index // 2,
            column=index % 2,
            padx=8,
            pady=8,
            sticky="ew"
        )

    actions_frame.columnconfigure(0, weight=1)
    actions_frame.columnconfigure(1, weight=1)

    # Bottom buttons
    bottom = tk.Frame(content, bg=BG)
    bottom.pack(anchor="w", pady=15)

    make_button(
        bottom,
        "View Graphs",
        show_graph_menu,
        "#334155"
    ).pack(side="left", padx=5)

    make_button(
        bottom,
        "Export Cleaned CSV",
        export_data,
        "#334155"
    ).pack(side="left", padx=5)


# ==============================
# SIDEBAR
# ==============================

tk.Label(
    sidebar,
    text="✦ STUDENT\n   ANALYTICS",
    bg=SIDEBAR,
    fg=WHITE,
    font=("Arial", 19, "bold"),
    justify="left"
).pack(anchor="w", padx=22, pady=35)


def sidebar_button(text, command):

    tk.Button(
        sidebar,
        text=text,
        command=command,
        bg=SIDEBAR,
        fg=WHITE,
        activebackground=PANEL,
        activeforeground=CYAN,
        font=("Arial", 10),
        relief="flat",
        anchor="w",
        padx=20,
        pady=13,
        cursor="hand2"
    ).pack(fill="x", padx=10, pady=2)


sidebar_button("⌂   Dashboard", show_dashboard)
sidebar_button("＋   Load Dataset", load_dataset)

sidebar_button(
    "▤   View Dataset",
    lambda: show_table(df) if df is not None else None
)

sidebar_button("✦   Clean Data", clean_data)
sidebar_button("▥   Data Analysis", analyze_data)
sidebar_button("▧   View Graphs", show_graph_menu)
sidebar_button("⇩   Export Data", export_data)

tk.Frame(
    sidebar,
    bg=SIDEBAR
).pack(fill="both", expand=True)

tk.Label(
    sidebar,
    text="PROJECT BY\nAmna Zafar | BS IT",
    bg=SIDEBAR,
    fg=MUTED,
    font=("Arial", 9),
    justify="left"
).pack(anchor="w", padx=22, pady=20)


# ==============================
# START APPLICATION
# ==============================

show_dashboard()

if DATASET_PATH.exists():
    load_dataset(str(DATASET_PATH))

root.mainloop()