#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced TODO List")
        self.root.geometry("850x600")
        self.root.minsize(700, 450)
        
        # Store todos as list of dicts
        self.todos = []
        self.editing_index = None
        
        self.setup_ui()
    
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
            background='darkblue',
            foreground='white', 
            borderwidth=2, 
            date_pattern='yyyy-mm-dd'
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
        self.task_tree.heading('status', text='Status')
        self.task_tree.heading('title', text='Task Title')
        self.task_tree.heading('importance', text='Importance')
        self.task_tree.heading('deadline', text='Deadline')
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
        self.task_tree.bind('<Double-Button-1>', lambda e: self.toggle_complete())
        
        # Configure row colors for tags
        self.task_tree.tag_configure('completed', foreground='gray')
        
        # --- BUTTON CONTROL PANEL ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        ttk.Button(btn_frame, text="Toggle Complete", command=self.toggle_complete).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Edit Selected", command=self.start_edit).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Clear Completed", command=self.clear_completed).pack(side=tk.LEFT, padx=3)
        self.cancel_edit_btn = ttk.Button(btn_frame, text="Cancel Edit", command=self.clear_inputs, state=tk.DISABLED)
        self.cancel_edit_btn.pack(side=tk.RIGHT, padx=3)
        
        # --- STATUS BAR ---
        self.status_label = ttk.Label(main_frame, text="0 tasks", relief=tk.SUNKEN, anchor=tk.W, padding="3")
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def save_task(self):
        title = self.task_entry.get().strip()
        priority = self.priority_combobox.get()
        
        # FIXED: Extracting date object out as a formatted string correctly
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
    
    def clear_completed(self):
        completed_count = sum(1 for todo in self.todos if todo['completed'])
        if completed_count == 0:
            messagebox.showinfo("No Completed Tasks", "There are no completed tasks to clear.")
            return
        
        if messagebox.askyesno("Confirm Clear", f"Remove {completed_count} completed task(s)?"):
            self.todos = [todo for todo in self.todos if not todo['completed']]
            self.clear_inputs()
            self.refresh_treeview()
    
    def refresh_treeview(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        for todo in self.todos:
            status_symbol = "✓ Done" if todo['completed'] else "⟳ Pending"
            row_values = (
                status_symbol,
                todo['text'],
                todo['importance'],
                todo['deadline'],
                todo['description']
            )
            
            if todo['completed']:
                self.task_tree.insert('', tk.END, values=row_values, tags=('completed',))
            else:
                self.task_tree.insert('', tk.END, values=row_values)
        
        total = len(self.todos)
        completed = sum(1 for todo in self.todos if todo['completed'])
        remaining = total - completed
        
        status_text = f" {total} task(s) total — {remaining} remaining, {completed} completed"
        self.status_label.config(text=status_text)

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()