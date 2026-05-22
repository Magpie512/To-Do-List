#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from tkcalendar import DateEntry
import json
import os

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced TODO List")
        self.root.geometry("850x600")
        self.root.minsize(700, 450)
        
        # Store todos as list of dicts
        self.todos = []
        self.editing_index = None
        self.sort_reverse = False
        self.sort_col = None
        
        self.apply_theme()
        self.setup_ui()
        self.load_from_backup()  # Automatically load tasks from AppData on startup
    
    def apply_theme(self):
        style = ttk.Style()
        # Use clam theme as base for better cross-platform appearance
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        # Comfy colors and fonts
        bg_color = "#f4f6f9"
        text_color = "#2c3e50"
        font_main = ("Segoe UI", 10)
        font_heading = ("Segoe UI", 10, "bold")
        
        self.root.configure(bg=bg_color)
        
        style.configure("TFrame", background=bg_color)
        style.configure("TLabelframe", background=bg_color)
        style.configure("TLabelframe.Label", background=bg_color, font=font_heading, foreground=text_color)
        style.configure("TLabel", background=bg_color, font=font_main, foreground=text_color)
        style.configure("TButton", font=font_main, padding=4)
        style.configure("TEntry", font=font_main)
        style.configure("TCombobox", font=font_main)
        
        style.configure("Treeview", 
                        font=font_main, 
                        rowheight=28, 
                        background="#ffffff",
                        fieldbackground="#ffffff",
                        foreground=text_color)
        style.configure("Treeview.Heading", font=font_heading, padding=4)
        
        # Selected row colors
        style.map('Treeview', background=[('selected', '#3498db')])

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # --- INPUT & EDITING SECTION ---
        self.input_frame = ttk.LabelFrame(main_frame, text=" Task Details ", padding="10")
        self.input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.input_frame.columnconfigure(1, weight=1)
        
        # Task Title
        ttk.Label(self.input_frame, text="Task Title:").grid(row=0, column=0, sticky=tk.W, pady=3, padx=5)
        self.task_entry = ttk.Entry(self.input_frame, font=("Arial", 10))
        self.task_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=3, padx=5)
        
        # Priority / Importance
        ttk.Label(self.input_frame, text="Importance:").grid(row=0, column=2, sticky=tk.W, pady=3, padx=5)
        self.priority_combobox = ttk.Combobox(self.input_frame, values=["Low", "Medium", "High"], state="readonly", width=10)
        self.priority_combobox.set("Medium")
        self.priority_combobox.grid(row=0, column=3, sticky=tk.W, pady=3, padx=5)
        
        # Intuitive Calendar Deadline Picker
        ttk.Label(self.input_frame, text="Deadline:").grid(row=1, column=0, sticky=tk.W, pady=3, padx=5)
        self.deadline_picker = DateEntry(
            self.input_frame, 
            width=12, 
            background='#3498db',
            foreground='white', 
            borderwidth=1, 
            date_pattern='yyyy-mm-dd',
            font=("Segoe UI", 10),
            showweeknumbers=False
        )
        self.deadline_picker.grid(row=1, column=1, sticky=tk.W, pady=3, padx=5)
        
        # Action Buttons
        self.submit_btn = ttk.Button(self.input_frame, text="Add Task", command=self.save_task)
        self.submit_btn.grid(row=1, column=2, columnspan=2, sticky=(tk.W, tk.E), pady=3, padx=5)
        
        # Description
        ttk.Label(self.input_frame, text="Description:").grid(row=2, column=0, sticky=tk.NW, pady=3, padx=5)
        self.desc_entry = ttk.Entry(self.input_frame, font=("Arial", 10))
        self.desc_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=3, padx=5)
        
        # --- TREEVIEW SECTION ---
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ('status', 'title', 'importance', 'deadline', 'description')
        self.task_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
        
        # Define Headings
        self.task_tree.heading('status', text='Status ↕', command=lambda: self.sort_by('status'))
        self.task_tree.heading('title', text='Task Title ↕', command=lambda: self.sort_by('title'))
        self.task_tree.heading('importance', text='Importance ↕', command=lambda: self.sort_by('importance'))
        self.task_tree.heading('deadline', text='Deadline ↕', command=lambda: self.sort_by('deadline'))
        self.task_tree.heading('description', text='Description')
        
        # Define Column Widths
        self.task_tree.column('status', width=80, anchor=tk.CENTER, stretch=False)
        self.task_tree.column('title', width=150, anchor=tk.W)
        self.task_tree.column('importance', width=90, anchor=tk.CENTER, stretch=False)
        self.task_tree.column('deadline', width=100, anchor=tk.CENTER, stretch=False)
        self.task_tree.column('description', width=250, anchor=tk.W)
        
        # Scrollbars
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Event Bindings
        self.task_tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Configure row colors for tags
        self.task_tree.tag_configure('evenrow', background='#f8f9fa')
        self.task_tree.tag_configure('oddrow', background='#ffffff')
        self.task_tree.tag_configure('completed', foreground='#a0a0a0', background='#e9ecef')
        
        # --- BUTTON CONTROL PANEL ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        ttk.Button(btn_frame, text="Toggle Complete", command=self.toggle_complete).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Edit Selected", command=self.start_edit).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Clear Completed", command=self.clear_completed).pack(side=tk.LEFT, padx=3)
        self.cancel_edit_btn = ttk.Button(btn_frame, text="Cancel Edit", command=self.clear_inputs, state=tk.DISABLED)
        self.cancel_edit_btn.pack(side=tk.RIGHT, padx=3)
        
        ttk.Button(btn_frame, text="Import", command=self.import_tasks).pack(side=tk.RIGHT, padx=3)
        ttk.Button(btn_frame, text="Export", command=self.export_tasks).pack(side=tk.RIGHT, padx=3)
        
        # --- STATUS BAR ---
        self.status_label = ttk.Label(main_frame, text="0 tasks", relief=tk.SUNKEN, anchor=tk.W, padding="3")
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def save_task(self):
        title = self.task_entry.get().strip()
        priority = self.priority_combobox.get()
        
        # Extracting date object out as a formatted string correctly
        deadline = self.deadline_picker.get_date().strftime('%Y-%m-%d')
        desc = self.desc_entry.get().strip()
        
        if not title:
            messagebox.showwarning("Validation Error", "Please enter a task title.")
            return

        if self.editing_index is not None:
            self.todos[self.editing_index].update({
                'text': title,
                'importance': priority,
                'deadline': deadline,
                'description': desc
            })
            self.editing_index = None
            self.input_frame.config(text=" Task Details ")
            self.submit_btn.config(text="Add Task")
            self.cancel_edit_btn.config(state=tk.DISABLED)
        else:
            todo = {
                'text': title,
                'importance': priority,
                'deadline': deadline,
                'description': desc,
                'completed': False,
                'created': datetime.now()
            }
            self.todos.append(todo)
        
        self.refresh_treeview()
        self.clear_inputs()
        self.save_to_backup()

    def start_edit(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task from the list to edit.")
            return
        
        item_id = selection[0]
        self.editing_index = self.task_tree.index(item_id)
        
        self.input_frame.config(text=" Editing Task... ")
        self.submit_btn.config(text="Save Changes")
        self.cancel_edit_btn.config(state=tk.NORMAL)
        
        task = self.todos[self.editing_index]
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, task['text'])
        self.priority_combobox.set(task['importance'])
        
        # Update calendar widget to reflect targeted task's date 
        date_obj = datetime.strptime(task['deadline'], "%Y-%m-%d").date()
        self.deadline_picker.set_date(date_obj)
        
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, task['description'])

    def clear_inputs(self):
        self.editing_index = None
        self.task_entry.delete(0, tk.END)
        self.priority_combobox.set("Medium")
        self.deadline_picker.set_date(datetime.now().date())
        self.desc_entry.delete(0, tk.END)
        
        self.input_frame.config(text=" Task Details ")
        self.submit_btn.config(text="Add Task")
        self.cancel_edit_btn.config(state=tk.DISABLED)
        self.task_entry.focus()

    def toggle_complete(self):
        selection = self.task_tree.selection()
        if not selection:
            return
        
        index = self.task_tree.index(selection[0])
        self.todos[index]['completed'] = not self.todos[index]['completed']
        self.refresh_treeview()
        
        children = self.task_tree.get_children()
        if children:
            self.task_tree.selection_set(children[index])
        self.save_to_backup()
    
    def delete_task(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
        
        index = self.task_tree.index(selection[0])
        if messagebox.askyesno("Confirm Delete", f"Delete task: '{self.todos[index]['text']}'?"):
            self.todos.pop(index)
            self.clear_inputs()
            self.refresh_treeview()
            self.save_to_backup()
    
    def clear_completed(self):
        completed_count = sum(1 for todo in self.todos if todo['completed'])
        if completed_count == 0:
            messagebox.showinfo("No Completed Tasks", "There are no completed tasks to clear.")
            return
        
        if messagebox.askyesno("Confirm Clear", f"Remove {completed_count} completed task(s)?"):
            self.todos = [todo for todo in self.todos if not todo['completed']]
            self.clear_inputs()
            self.refresh_treeview()
            self.save_to_backup()
    
    def on_double_click(self, event):
        row_id = self.task_tree.identify_row(event.y)
        if not row_id:
            return
        self.toggle_complete()

    def sort_by(self, col):
        self.clear_inputs() # Clear any active edits before sorting
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_col = col

        if col == "importance":
            priority_map = {"Low": 1, "Medium": 2, "High": 3}
            self.todos.sort(key=lambda x: priority_map.get(x['importance'], 0), reverse=self.sort_reverse)
        elif col == "deadline":
            self.todos.sort(key=lambda x: x['deadline'], reverse=self.sort_reverse)
        elif col == "title":
            self.todos.sort(key=lambda x: x['text'].lower(), reverse=self.sort_reverse)
        elif col == "status":
            self.todos.sort(key=lambda x: x['completed'], reverse=self.sort_reverse)
            
        self.refresh_treeview()
        self.save_to_backup()

    def refresh_treeview(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        for i, todo in enumerate(self.todos):
            status_symbol = "✓ Done" if todo['completed'] else "⟳ Pending"
            row_values = (
                status_symbol,
                todo['text'],
                todo['importance'],
                todo['deadline'],
                todo['description']
            )
            
            tags = ('completed',) if todo['completed'] else ('evenrow' if i % 2 == 0 else 'oddrow',)
            self.task_tree.insert('', tk.END, values=row_values, tags=tags)
        
        total = len(self.todos)
        completed = sum(1 for todo in self.todos if todo['completed'])
        remaining = total - completed
        
        status_text = f" {total} task(s) total — {remaining} remaining, {completed} completed"
        self.status_label.config(text=status_text)

    def export_tasks(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Tasks"
        )
        if not file_path:
            return
            
        try:
            def datetime_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError("Type not serializable")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.todos, f, default=datetime_serializer, indent=4)
            messagebox.showinfo("Export Successful", f"Successfully exported tasks to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting:\n{e}")

    def import_tasks(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Tasks"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                imported_todos = json.load(f)
                
                # Verify structure and convert dates
                for todo in imported_todos:
                    if 'created' in todo and todo['created']:
                        todo['created'] = datetime.fromisoformat(todo['created'])
                
                if self.todos:
                    response = messagebox.askyesnocancel(
                        "Import Tasks",
                        "Do you want to overwrite your existing tasks?\n\n"
                        "Yes: Overwrite all current tasks\n"
                        "No: Append imported tasks to current list\n"
                        "Cancel: Abort import"
                    )
                    if response is None: # Cancel
                        return
                    elif response: # Yes (Overwrite)
                        self.todos = imported_todos
                    else: # No (Append)
                        self.todos.extend(imported_todos)
                else:
                    self.todos = imported_todos
                
                self.refresh_treeview()
                self.save_to_backup()
                messagebox.showinfo("Import Successful", f"Successfully imported tasks from {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred while importing:\n{e}")

    # --- SYSTEM APPDATA BACKUP & LOADING FUNCTIONALITIES ---
    
    def save_to_backup(self):
        """Saves the current todo list into the Windows AppData local directory."""
        # This points safely to C:\Users\<Username>\AppData\Roaming\AdvancedTodoList
        appdata_dir = os.path.join(os.environ['APPDATA'], "AdvancedTodoList")
        
        # Build directory silently if it doesn't exist
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir)
            
        file_path = os.path.join(appdata_dir, "todo_backup.json")
        
        try:
            def datetime_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError("Type not serializable")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.todos, f, default=datetime_serializer, indent=4)
                
        except Exception as e:
            print(f"Error saving backup file: {e}")

    def load_from_backup(self):
        """Loads tasks from the Windows AppData directory if it exists."""
        appdata_dir = os.path.join(os.environ['APPDATA'], "AdvancedTodoList")
        file_path = os.path.join(appdata_dir, "todo_backup.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    loaded_todos = json.load(f)
                    
                    # Convert string representations back into Python datetime items
                    for todo in loaded_todos:
                        if 'created' in todo and todo['created']:
                            todo['created'] = datetime.fromisoformat(todo['created'])
                            
                    self.todos = loaded_todos
                    self.refresh_treeview()
            except Exception as e:
                print(f"Error loading backup file: {e}")

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()