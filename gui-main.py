#!/usr/bin/env python3

"""
Comments Boilerplate v1.0 Tkinter GUI: a portable source file comments generator.
Add header comments to the source code files of a project.
Can be made recursive or not. Supports various languages (C++, Python).
"""

import tkinter as tk
import treewalker
from tkinter import messagebox, scrolledtext
from tkinter.filedialog import askdirectory, askopenfilename

# Get program directory path, input language (can be set to auto so application figures it out
# using file extensions) and recursive flag.

class Application:

    def __init__(self, root: tk.Tk):
        self.dir_name = ''
        self.file_path = ''

        # Project Directory
        self.project_dir_label = tk.Label(root, text="Project directory:")
        self.project_dir_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=15)
        self.project_dir_entry = tk.Entry(root, width=30)
        self.project_dir_entry.grid(row=0, column=1, sticky=tk.W)
        self.choose_dir_btn = tk.Button(root, text="...", command=self.set_directory_name)
        self.choose_dir_btn.grid(row=0, column=2, sticky=tk.W)
        self.comment_dir_btn = tk.Button(root, text='Generate Project Comments', command=self.generate_dir_comments)
        self.comment_dir_btn.grid(row=0, column=3, sticky=tk.W)
        self.recurse = tk.IntVar()
        self.recurse_chkbox = tk.Checkbutton(root, text="Recurse", variable=self.recurse)
        self.recurse_chkbox.grid(row=0, column=4)

        # File
        self.select_file_label = tk.Label(root, text='File:')
        self.select_file_label.grid(row=1, column=0,sticky=tk.W, padx=10, pady=15)
        self.select_file_entry = tk.Entry(root, width=30)
        self.select_file_entry.grid(row=1, column=1, sticky=tk.W)
        self.select_file_btn = tk.Button(root, text="...", command=self.set_file_name)
        self.select_file_btn.grid(row=1, column=2, sticky=tk.W)
        self.comment_file_btn = tk.Button(root, text='Generate File Comments', command=self.generate_file_comments)
        self.comment_file_btn.grid(row=1, column=3, sticky=tk.W)

        # Language Selection
        self.language_select_label = tk.Label(root, text="Language:")
        self.language_select_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=15)
        self.selected_language = tk.StringVar(root)
        self.language_options = [treewalker.CPP_NAME, treewalker.PYTHON_NAME, treewalker.CSHARP_NAME,
                                 treewalker.JAVA_NAME, treewalker.LISP_NAME, treewalker.LUA_NAME,
                                 treewalker.JAVASCRIPT_NAME, treewalker.VBNET_NAME, treewalker.BASH_NAME, treewalker.PERL_NAME]
        self.selected_language.set(self.language_options[0])
        self.languages_optionmenu = tk.OptionMenu(root, self.selected_language, *self.language_options)
        self.languages_optionmenu.grid(row=2, column=1, sticky=tk.W)

        # Header Contents
        self.selected_licence = tk.StringVar(root)
        self.licences = ['MIT', 'BSD', 'GPLv3', 'LGPLv3', 'Apache']
        self.selected_licence.set(self.licences[0])
        self.licence_selector_label = tk.Label(root, text='Licence:')
        self.licence_selector_label.grid(row=2, column=2, sticky=tk.W, pady=15)
        self.licence_selector = tk.OptionMenu(root, self.selected_licence, *self.licences)
        self.licence_selector.grid(row=2, column=3, sticky=tk.W)

        self.author_label = tk.Label(root, text='Author:')
        self.author_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=15)
        self.author_entry = tk.Entry(root, width=30)
        self.author_entry.grid(row=3, column=1, sticky=tk.W)

        self.file_description_label = tk.Label(root, text='File description:')
        self.file_description_label.grid(row=4, column=0, sticky=tk.W, padx=10, pady=15)
        self.file_description_textbox = scrolledtext.ScrolledText(root, height=10, width=20)
        self.file_description_textbox.grid(row=4, column=1, sticky=tk.W, pady=10)

        self.file_remarks_label = tk.Label(root, text='Remarks:')
        self.file_remarks_label.grid(row=5, column=0, sticky=tk.W, padx=10, pady=15)
        self.file_remarks_textbox = scrolledtext.ScrolledText(root, height=10, width=20)
        self.file_remarks_textbox.grid(row=5, column=1, sticky=tk.W, pady=10)

    def validate_heading_form(self) -> bool:
        # At the moment this just performs one check, but in the future we might want to add more elements that need validation.
        return self.author_entry.get() != None

    def get_heading(self):
        if self.validate_heading_form():
            return treewalker.Heading(self.author_entry.get(), self.selected_licence.get(), self.file_description_textbox.get(1.0, tk.END).strip(), self.file_remarks_textbox.get(1.0, tk.END).strip())
        else:
            return None

    def generate_file_comments(self):
        if self.select_file_entry.get():
            self.file_path = self.select_file_entry.get()
        else:
            messagebox.showerror('Unspecified path', 'The path of the project was not entered.')
            return
        heading = self.get_heading()
        if not heading:
            messagebox.showerror('Incorrect heading parameters', 'The heading parameters you entered are invalid.')
            return
        generator = treewalker.HeadingGenerator(self.file_path, self.selected_language.get())
        try:
            if not generator.comment_file(heading):
                messagebox.showerror('Incorrect path', 'You provided an invalid file path. You need to enter the full path to the file. Make sure the path points to a source file of the language you selected')
                return
            messagebox.showinfo('Signing complete', 'The project or file was successfully signed.')
        except Exception as e:
            messagebox.showerror('Signing unsuccessful', 'The project or file could not be successfully signed. Error details: ' + str(e))

    def generate_dir_comments(self):
        if self.project_dir_entry.get():
            self.dir_name = self.project_dir_entry.get()
        else:
            messagebox.showerror('Unspecified path', 'The path of the project was not entered.')
            return
        heading = self.get_heading()
        if not heading:
            messagebox.showerror('Incorrect heading parameters', 'The heading parameters you entered are invalid.')
            return
        generator = treewalker.HeadingGenerator(self.dir_name, self.selected_language.get())
        try:
            if not generator.comment_directory(heading, self.recurse.get()):
                messagebox.showerror('Incorrect path', 'You provided an invalid path to the project directory. You need to enter the full path to the directory.')
                return
            messagebox.showinfo('Signing complete', 'The project or file was successfully signed.')
        except:
            messagebox.showerror('Signing unsuccessful', 'The project or file could not be successfully signed.')

    def set_file_name(self):
        self.select_file_entry.delete(0, tk.END)
        self.select_file_entry.insert(0, askopenfilename())

    def set_directory_name(self):
        self.project_dir_entry.delete(0, tk.END)
        self.project_dir_entry.insert(0, askdirectory(mustexist=True))

if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("Comments Boilerplate v1.0 beta")
    app = Application(root)
    root.mainloop()
