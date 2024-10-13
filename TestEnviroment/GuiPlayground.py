import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, simpledialog, scrolledtext


### build using "C:\Users\BJRte\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe" --onefile --windowed "C:\Users\BJRte\OneDrive\Desktop\Python Scripts\TestEnviroment\GuiPlayground.py"
### merged with git

# Function to update label text when button is clicked
def on_button_click():
    label.config(text="Welcome to our Application!")

# Function to display a message box
def show_message_box():
    messagebox.showinfo("Information", "This is a message box!")

# Function to open a file dialog and display the selected file path
def open_file_dialog():
    file_path = filedialog.askopenfilename()
    if file_path:
        label.config(text=f"Selected File: {file_path}")

# Function to open a color chooser and change the background color of the root window
def choose_color():
    color_code = colorchooser.askcolor(title="Choose a color")[1]
    if color_code:
        root.configure(bg=color_code)

# Function to toggle checkbox state and update label text
def toggle_check():
    if check_var.get():
        label.config(text="Checkbox is Checked")
    else:
        label.config(text="Checkbox is Unchecked")

# Function to update label text based on slider value
def slider_changed(event):
    label.config(text=f"Slider Value: {slider.get()}")

# Function to ask for user input and update label text with the input
def ask_user_input():
    user_input = simpledialog.askstring("Input", "Please enter your name:")
    if user_input:
        label.config(text=f"Hello, {user_input}!")

# Function to update label text with selected items from the listbox
def listbox_selection(event):
    selected_items = [listbox.get(i) for i in listbox.curselection()]
    label.config(text=f"You selected: {', '.join(selected_items)}")

# Function to update label text based on selected radio button
def radio_button_selected():
    label.config(text=f"Selected Option: {radio_var.get()}")

# Function to update label text based on spinbox value
def spinbox_value_changed():
    label.config(text=f"Spinbox Value: {spinbox.get()}")

# Function to toggle button text between ON and OFF
def toggle_button():
    if toggle_var.get():
        toggle_button.config(text="ON")
    else:
        toggle_button.config(text="OFF")

# Function to open a directory dialog and display the selected directory path
def open_directory_dialog():
    directory = filedialog.askdirectory()
    if directory:
        label.config(text=f"Selected Directory: {directory}")

# Function to show an error message box
def show_error_message():
    messagebox.showerror("Error", "This is an error message!")

# Function to show a warning message box
def show_warning_message():
    messagebox.showwarning("Warning", "This is a warning message!")

# Function to change the theme of the application based on combobox selection
def change_theme(event):
    selected_theme = theme_var.get()
    tt_style.theme_use(selected_theme)

# Create the main application window
root = tk.Tk()
root.title("Professional GUI Application")
root.geometry("600x500")
root.resizable(True, True)
root.configure(bg='#2e2e2e')

# Apply a modern style
tt_style = ttk.Style()
tt_style.theme_use('clam')

# Create a scrollable frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)
canvas = tk.Canvas(main_frame, bg='#2e2e2e')
vertical_scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview, width=25)
horizontal_scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview, width=25)
scrollable_frame = tk.Frame(canvas, bg='#2e2e2e')

# Bind scrollable frame to update the canvas scroll region
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

# Add scrollable frame to canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

# Pack canvas and scrollbars
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
vertical_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

# Enable scrolling with mouse wheel
def _on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _on_shift_mouse_wheel(event):
    canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

# Bind mouse wheel events to canvas for vertical and horizontal scrolling
canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
canvas.bind_all("<Shift-MouseWheel>", _on_shift_mouse_wheel)

# Create a header label
header_label = ttk.Label(scrollable_frame, text="Welcome", font=("Helvetica", 16, "bold"), background='#2e2e2e', foreground='#ffffff')
header_label.pack(pady=10)

# Create an instruction label
label = ttk.Label(scrollable_frame, text="Please click the button below:", font=("Helvetica", 12), background='#2e2e2e', foreground='#ffffff')
label.pack(pady=20)

# Create a button to change label text
button = ttk.Button(scrollable_frame, text="Click Here", command=on_button_click)
button.pack(pady=10)

# Create a button to show a message box
message_button = ttk.Button(scrollable_frame, text="Show Message Box", command=show_message_box)
message_button.pack(pady=10)

# Create a button to open a file dialog
file_button = ttk.Button(scrollable_frame, text="Open File", command=open_file_dialog)
file_button.pack(pady=10)

# Create a button to choose a color
color_button = ttk.Button(scrollable_frame, text="Choose Background Color", command=choose_color)
color_button.pack(pady=10)

# Create a checkbox
check_var = tk.BooleanVar()
check_button = ttk.Checkbutton(scrollable_frame, text="Check Me", variable=check_var, command=toggle_check)
check_button.pack(pady=10)

# Create a slider
slider = ttk.Scale(scrollable_frame, from_=0, to=100, orient='horizontal', command=slider_changed)
slider.pack(pady=10)

# Create a button to ask for user input
input_button = ttk.Button(scrollable_frame, text="Enter Your Name", command=ask_user_input)
input_button.pack(pady=10)

# Create a listbox with multiple selection enabled
listbox = tk.Listbox(scrollable_frame, selectmode=tk.EXTENDED)
listbox_items = ["Option 1", "Option 2", "Option 3", "Option 4"]
for item in listbox_items:
    listbox.insert(tk.END, item)
listbox.bind('<<ListboxSelect>>', listbox_selection)
listbox.pack(pady=10)

# Create radio buttons
radio_var = tk.StringVar(value="Option 1")
radio_button1 = ttk.Radiobutton(scrollable_frame, text="Option 1", variable=radio_var, value="Option 1", command=radio_button_selected)
radio_button2 = ttk.Radiobutton(scrollable_frame, text="Option 2", variable=radio_var, value="Option 2", command=radio_button_selected)
radio_button1.pack(pady=5)
radio_button2.pack(pady=5)

# Create a spinbox
spinbox = ttk.Spinbox(scrollable_frame, from_=0, to=10, command=spinbox_value_changed)
spinbox.pack(pady=10)

# Create a toggle button
toggle_var = tk.BooleanVar()
toggle_button = ttk.Checkbutton(scrollable_frame, text="OFF", variable=toggle_var, command=toggle_button, style='Toggle.TButton')
toggle_button.pack(pady=10)

# Create a button to open a directory dialog
directory_button = ttk.Button(scrollable_frame, text="Open Directory", command=open_directory_dialog)
directory_button.pack(pady=10)

# Create buttons for different types of message boxes
error_button = ttk.Button(scrollable_frame, text="Show Error Message", command=show_error_message)
error_button.pack(pady=10)
warning_button = ttk.Button(scrollable_frame, text="Show Warning Message", command=show_warning_message)
warning_button.pack(pady=10)

# Create a canvas for drawing
drawing_canvas = tk.Canvas(scrollable_frame, width=200, height=150, bg='white')
drawing_canvas.pack(pady=10)
drawing_canvas.create_rectangle(50, 50, 150, 100, fill='blue')

# Create a progress bar
progress = ttk.Progressbar(scrollable_frame, length=200, mode='determinate')
progress.pack(pady=10)
progress['value'] = 50

# Create a text widget
text_widget = tk.Text(scrollable_frame, height=5, width=40)
text_widget.pack(pady=10)
text_widget.insert(tk.INSERT, "This is a Text widget.")

# Create a scrolled text widget
scrolled_text = scrolledtext.ScrolledText(scrollable_frame, width=40, height=5, wrap=tk.WORD)
scrolled_text.pack(pady=10)
scrolled_text.insert(tk.INSERT, "This is a ScrolledText widget.")

# Create a menu
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_file_dialog)
file_menu.add_command(label="Save")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Undo")
edit_menu.add_command(label="Redo")
menu_bar.add_cascade(label="Edit", menu=edit_menu)

# Create a paned window for two resizable panes
paned_window = ttk.Panedwindow(scrollable_frame, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
left_pane = ttk.Label(paned_window, text="Left Pane")
right_pane = ttk.Label(paned_window, text="Right Pane")
paned_window.add(left_pane, weight=1)
paned_window.add(right_pane, weight=4)

# Create a treeview to display hierarchical data
tree = ttk.Treeview(scrollable_frame)
tree.pack(pady=10)
tree['columns'] = ('size', 'modified')
tree.heading('#0', text='Name', anchor='w')
tree.heading('size', text='Size', anchor='w')
tree.heading('modified', text='Modified', anchor='w')
tree.insert('', 'end', text='Item 1', values=('20 KB', 'Today'))
tree.insert('', 'end', text='Item 2', values=('15 KB', 'Yesterday'))

# Create a notebook (tabs)
notebook = ttk.Notebook(scrollable_frame)
notebook.pack(pady=10, fill='both', expand=True)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
notebook.add(tab1, text="Tab 1")
notebook.add(tab2, text="Tab 2")
tab1_label = ttk.Label(tab1, text="This is Tab 1")
tab1_label.pack(pady=10)
tab2_label = ttk.Label(tab2, text="This is Tab 2")
tab2_label.pack(pady=10)

# Create a combobox for theme selection
theme_var = tk.StringVar()
theme_combobox = ttk.Combobox(scrollable_frame, textvariable=theme_var)
theme_combobox['values'] = tt_style.theme_names()
theme_combobox.current(tt_style.theme_names().index('clam'))
theme_combobox.bind('<<ComboboxSelected>>', change_theme)
theme_combobox.pack(pady=10)

# Create a message widget for displaying longer text
message = tk.Message(scrollable_frame, text="This is a Message widget, similar to a label but for longer text.", width=300)
message.pack(pady=10)

# Create a separator to divide sections visually
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.pack(fill='x', pady=10)

# Create a labelframe to group related widgets
labelframe = ttk.Labelframe(scrollable_frame, text="Labelframe Example")
labelframe.pack(pady=10, padx=10, fill='both')
label_inside = ttk.Label(labelframe, text="Content inside Labelframe")
label_inside.pack(pady=10)

# Start the main event loop to run the application
root.mainloop()