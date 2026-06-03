import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import threading
import json
from llm.llm import llm
from par.build_empty_xml import empty_builder
from par.gpd import gpd
from par.process_definition import process_definition_builder
from par.variables import variables
from par.forms import forms
from par.generate_par import create_zip_with_par_extension


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор бизнес-процесса")
        self.root.geometry("700x600")
        
        ttk.Label(root, text="Введите текстовое описание бизнес-процесса", font=('Arial', 14, 'bold')).pack(pady=5)
        
        text_frame = ttk.Frame(root)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=('Arial', 13),
            height=15
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Сгенерировать PAR", command=self.generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear).pack(side=tk.LEFT, padx=5)
        
        settings_frame = ttk.LabelFrame(root, text="Настройки API", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(settings_frame, text="OpenAI API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_entry = ttk.Entry(settings_frame, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Температура (0.0-1.0):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.temp_entry = ttk.Entry(settings_frame, width=10)
        self.temp_entry.insert(0, "0.0")
        self.temp_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.status = tk.StringVar()
        self.status.set("Готов к работе. Введите описание бизнес-процесса.")
        status_label = ttk.Label(root, textvariable=self.status, relief=tk.SUNKEN)
        status_label.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
    

    def clear(self):
        self.text_area.delete("1.0", tk.END)
        self.status.set("Поле очищено. Введите новое описание.")
    

    def generate(self):
        text = self.text_area.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("Внимание", "Введите описание бизнес-процесса")
            return
        
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("Внимание", "Введите OpenAI API ключ")
            return
        
        try:
            temp = float(self.temp_entry.get().strip())
        except ValueError:
            messagebox.showwarning("Внимание", "Температура должна быть числом")
            return
        
        os.environ['OPENAI_API_KEY'] = api_key

        self.status.set("Генерация бизнес-процесса через LLM...")
        self.progress.start()
        
        thread = threading.Thread(target=self._generate_thread, args=(text, temp))
        thread.daemon = True
        thread.start()
    

    def _generate_thread(self, text, temp):
        try:
            data = llm(text, temp)
            
            self.root.after(0, lambda: self.status.set("Создание XML-файлов..."))
            
            empty_builder("comments", "versions")
            empty_builder("forms", "forms")
            empty_builder("variables", "variables")
            empty_builder("gpd", "process-diagram")
            
            process_definition_builder(data)
            gpd("gpd.xml", data)
            variables('variables.xml', data)
            ftl_files = forms("forms.xml", data)
            
            files_to_archive = [
                "gpd.xml",
                "processdefinition.xml",
                "comments.xml",
                "forms.xml",
                "variables.xml"
            ]
            files_to_archive += ftl_files
            
            result = create_zip_with_par_extension(
                file_list=files_to_archive,
                output_name="result"
            )
            
            if result:
                for f in files_to_archive:
                    if os.path.exists(f):
                        os.remove(f)
            
            self.root.after(0, lambda r=result: self._on_success(r))
            
        except Exception as err:
            import traceback
            traceback_str = traceback.format_exc()
            print("=== ПОЛНАЯ ОШИБКА ===")
            print(traceback_str)
            self.root.after(0, lambda e=err: self._on_error(str(e)))
    

    def _on_success(self, result_path):
        self.progress.stop()
        self.status.set(f"Готово! PAR-архив создан: {result_path}")
        messagebox.showinfo("Успех", f"Файл создан: {os.path.abspath(result_path)}")
    

    def _on_error(self, error_msg):
        self.progress.stop()
        self.status.set(f"Ошибка: {error_msg} \nПожалуйста, попробуйте еще раз")
        messagebox.showerror("Ошибка - пожалуйста, попробуйте еще раз", error_msg)