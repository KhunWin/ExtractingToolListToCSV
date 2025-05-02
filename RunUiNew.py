import tkinter as tk
from tkinter import filedialog, messagebox
import os
from GetExcelNew import *

class UI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.all_file = True
        self.title("Capability Automation Tool")
        self.geometry("700x900")
        self.configure(bg="white")

        self.file_paths = {}
        self.file_labels = {}
        self.buttons = {}

        self.button_label = tk.Label(self, text="Choose AMM File for A320, A330, A380", fg="black",bg="white")
        self.button_label.pack(pady=5)
        self.create_buttons()

        self.user_input_label = tk.Label(self, text="Type output file name", fg="black", bg="white")
        self.user_input_label.pack(pady=5)

        self.user_input = tk.Entry(self, bg="white", fg="black")
        self.user_input.pack(pady=5)
        
        self.result_text = tk.Text(self, height=10, bg="black", fg="white")
        self.result_text.pack(pady=10)
        self.result_text.insert(tk.END, "The program is running.....\n","black")

        self.create_execute_button()
        self.create_reset_button()

    def create_button_with_label(self, button_text, command, index):
        canvas = tk.Canvas(self, width=200, height=40, bg="white", highlightthickness=0)
        canvas.pack(pady=5)

        button = canvas.create_rectangle(0, 0, 200, 40, fill="blue", outline="")
        text = canvas.create_text(100, 20, text=button_text, fill="white")

        canvas.tag_bind(button, "<Button-1>", lambda event, cmd=command: self.on_button_click(event, cmd))
        canvas.tag_bind(text, "<Button-1>", lambda event, cmd=command: self.on_button_click(event, cmd))
        canvas.tag_bind(button, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(button, "<Leave>", lambda event: self.on_button_hover(event, "leave"))
        canvas.tag_bind(text, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(text, "<Leave>", lambda event: self.on_button_hover(event, "leave"))

        self.buttons[index] = (canvas, button, text)

        label = tk.Label(self, text="", bg="white")
        label.pack(pady=5)
        self.file_labels[index] = label
    

    def on_button_click(self, event, command):
        command()

    def on_button_hover(self, event, state):
        canvas = event.widget
        button_index = next(index for index, (c, _, _) in self.buttons.items() if c == canvas)
        _, button, _ = self.buttons[button_index]
        if state == "enter":
            canvas.itemconfig(button, fill="dark blue")
        else:
            canvas.itemconfig(button, fill="blue")

    def create_buttons(self):
        
        self.create_button_with_label("Choose AMM File(.sgm)", self.choose_file1, 1)
        label = tk.Label(self, text="Choose AMM Folder for A350", fg="black",bg="white")
        label.pack(pady=5)
        self.create_button_with_label("Choose AMM Folder", self.choose_folder1, 2)
        self.create_button_with_label("Choose MPD(.csv)", self.choose_file2, 3)
        self.create_button_with_label("Choose TEM(.csv)", self.choose_file3, 4)
        self.create_button_with_label("Choose HXStock(.csv)", self.choose_file4, 5)

    def create_execute_button(self):
        
        label = tk.Label(self, text="Click Execute to create an excel document", fg="black", bg="white")
        label.pack(pady=5)


        canvas = tk.Canvas(self, width=200, height=40, bg="white", highlightthickness=0)
        canvas.pack(pady=4)

        button = canvas.create_rectangle(0, 0, 200, 40, fill="blue", outline="")
        text = canvas.create_text(100, 20, text="Execute", fill="white")

        canvas.tag_bind(button, "<Button-1>", self.on_execute_click)
        canvas.tag_bind(text, "<Button-1>", self.on_execute_click)
        canvas.tag_bind(button, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(button, "<Leave>", lambda event: self.on_button_hover(event, "leave"))
        canvas.tag_bind(text, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(text, "<Leave>", lambda event: self.on_button_hover(event, "leave"))

    def on_execute_click(self, event):
        self.create_excel_file() 

    def create_reset_button(self):
        canvas = tk.Canvas(self, width=200, height=40, bg="white", highlightthickness=0)
        canvas.pack(pady=5)

        button = canvas.create_rectangle(0, 0, 200, 40, fill="blue", outline="")
        text = canvas.create_text(100, 20, text="Reset", fill="white")

        canvas.tag_bind(button, "<Button-1>", self.on_reset_click)
        canvas.tag_bind(text, "<Button-1>", self.on_reset_click)
        canvas.tag_bind(button, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(button, "<Leave>", lambda event: self.on_button_hover(event, "leave"))
        canvas.tag_bind(text, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(text, "<Leave>", lambda event: self.on_button_hover(event, "leave"))

    def on_reset_click(self, event):
        self.reset()

    def choose_file1(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_paths[1] = file_path
            self.file_labels[1].config(text=os.path.basename(file_path))

    def choose_folder1(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.file_paths[1] = folder_path
            self.file_labels[2].config(text=os.path.basename(folder_path))

    def choose_file2(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if not file_path.lower().endswith('.csv'):
                messagebox.showerror("Invalid File", "Please choose a .csv file for MPD.")
            else:
                self.file_paths[2] = file_path
                self.file_labels[3].config(text=os.path.basename(file_path))

    def choose_file3(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if not file_path.lower().endswith('.csv'):
                messagebox.showerror("Invalid File", "Please choose a .csv file for TEM.")
            else:
                self.file_paths[3] = file_path
                self.file_labels[4].config(text=os.path.basename(file_path))

    def choose_file4(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if not file_path.lower().endswith('.csv'):
                messagebox.showerror("Invalid File", "Please choose a .csv file for HXStock.")
            else:
                self.file_paths[4] = file_path
                self.file_labels[5].config(text=os.path.basename(file_path))

    def create_execute_button(self):
        label = tk.Label(self, text="Click Execute to create an excel document", fg="black", bg="white")
        label.pack(pady=5)

        canvas = tk.Canvas(self, width=200, height=40, bg="white", highlightthickness=0)
        canvas.pack(pady=5)

        button = canvas.create_rectangle(0, 0, 200, 40, fill="blue", outline="")
        text = canvas.create_text(100, 20, text="Execute", fill="white")

        canvas.tag_bind(button, "<Button-1>", self.on_execute_click)
        canvas.tag_bind(text, "<Button-1>", self.on_execute_click)
        canvas.tag_bind(button, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(button, "<Leave>", lambda event: self.on_button_hover(event, "leave"))
        canvas.tag_bind(text, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(text, "<Leave>", lambda event: self.on_button_hover(event, "leave"))

        self.buttons['execute'] = (canvas, button, text)

    def create_reset_button(self):
        canvas = tk.Canvas(self, width=200, height=40, bg="white", highlightthickness=0)
        canvas.pack(pady=5)

        button = canvas.create_rectangle(0, 0, 200, 40, fill="blue", outline="")
        text = canvas.create_text(100, 20, text="Reset", fill="white")

        canvas.tag_bind(button, "<Button-1>", self.on_reset_click)
        canvas.tag_bind(text, "<Button-1>", self.on_reset_click)
        canvas.tag_bind(button, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(button, "<Leave>", lambda event: self.on_button_hover(event, "leave"))
        canvas.tag_bind(text, "<Enter>", lambda event: self.on_button_hover(event, "enter"))
        canvas.tag_bind(text, "<Leave>", lambda event: self.on_button_hover(event, "leave"))

        self.buttons['reset'] = (canvas, button, text)

    def on_execute_click(self, event):
        canvas = event.widget
        _, button, _ = self.buttons['execute']
        canvas.itemconfig(button, fill="dark blue")
        self.after(100, lambda: canvas.itemconfig(button, fill="blue"))
        self.create_excel_file()

    def on_reset_click(self, event):
        canvas = event.widget
        _, button, _ = self.buttons['reset']
        canvas.itemconfig(button, fill="dark blue")
        self.after(100, lambda: canvas.itemconfig(button, fill="blue"))
        self.reset()

    #this function is called in the on_execute_click function to create the excel file
    def create_excel_file(self):
        if not self.user_input.get().strip():
            messagebox.showwarning("No Input", "Please input the output filename.")
            return
        
        amm_file = self.file_paths.get(1)
        mpd_file = self.file_paths.get(2)
        tem_file = self.file_paths.get(3)
        hxstock_file = self.file_paths.get(4)

        if not all([amm_file, mpd_file, tem_file, hxstock_file]):
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Cannot proceed to create an excel document. Make sure to select all files.\n", "red")
            self.result_text.insert(tk.END, "Please select all files before executing.\n","black")
            return 
        
        self.result_text.delete(1.0, tk.END)
        
        self.result_text.insert(tk.END, f"AMM file: {amm_file}\n", "black")
        self.result_text.insert(tk.END, f"MPD file: {mpd_file}\n","black")
        self.result_text.insert(tk.END, f"TEM file: {tem_file}\n","black")
        self.result_text.insert(tk.END, f"HXStock file: {hxstock_file}\n","black")

        try:
            self.result_text.insert(tk.END, "Creating Excel file...\n", "black")
            ##this is the main function that is called to create the excel file from GetExcelNew.py
            all_excel = CapabilityAutomationToolNew(amm_file, mpd_file, tem_file, hxstock_file)
            all_excel.run(f"{self.user_input.get()}.xlsx")

        except Exception as e:
            self.result_text.insert(tk.END, f"Error: {e}\n", "red")
            print(f"Error in running CapabilityAutomationTool: {e}")
        finally:
            try:
                self.result_text.insert(tk.END, "Creating Excel file compeleted!.\n", "black")
                print("Create Excel file finished running.")
            except Exception as e:
                self.result_text.insert(tk.END, "Unsuccessful execution.\n", "black")
                print("Unsuccessful execution. Error: ", e)

    #this function is to reset the UI so that the user can input new files without closing the UI
    def reset(self):
        self.file_paths.clear()
        for label in self.file_labels.values():
            label.config(text="")
        self.user_input.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Reset complete. Please reselect files and execute.\n", "black")
        self.result_text.insert(tk.END, "The program is running.....\n","black")
        print("Reset complete. Please reselect files and execute.")


# do not delet his main function. This is the main function that runs the UI
if __name__ == "__main__":
    app = UI()
    app.mainloop()

# End of RunUiNew.py