import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime
from tkinter import scrolledtext

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # API Key (замените на свой)
        self.api_key = "YOUR_API_KEY"
        self.base_url = "https://v6.exchangerate-api.com/v6/"
        
        # Файл для хранения истории
        self.history_file = "conversion_history.json"
        self.history = []
        
        # Загрузка истории
        self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка курсов валют
        self.load_currencies()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Currency Converter", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Выбор валюты "Из"
        ttk.Label(main_frame, text="Из валюты:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.from_currency = ttk.Combobox(main_frame, width=15, state="readonly")
        self.from_currency.grid(row=1, column=1, padx=5, pady=5)
        
        # Выбор валюты "В"
        ttk.Label(main_frame, text="В валюту:", font=("Arial", 10)).grid(row=1, column=2, sticky=tk.W, padx=5)
        self.to_currency = ttk.Combobox(main_frame, width=15, state="readonly")
        self.to_currency.grid(row=1, column=3, padx=5, pady=5)
        
        # Поле ввода суммы
        ttk.Label(main_frame, text="Сумма:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_entry = ttk.Entry(main_frame, width=20)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Кнопка конвертации
        self.convert_btn = ttk.Button(main_frame, text="Конвертировать", command=self.convert_currency)
        self.convert_btn.grid(row=2, column=2, columnspan=2, pady=10)
        
        # Результат
        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=3, column=0, columnspan=4, pady=10)
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        # Таблица истории
        ttk.Label(main_frame, text="История конвертаций:", font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))
        
        # Создание таблицы
        columns = ("Дата", "Из", "В", "Сумма", "Результат")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
        
        # Настройка колонок
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=6, column=4, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки управления историей
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Загрузить историю", command=self.load_history_gui).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт истории", command=self.export_history).pack(side=tk.LEFT, padx=5)
        
        # Настройка веса колонок для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Привязка клавиши Enter к конвертации
        self.amount_entry.bind('<Return>', lambda event: self.convert_currency())
        
    def load_currencies(self):
        """Загрузка списка доступных валют"""
        try:
            url = f"{self.base_url}{self.api_key}/codes"
            response = requests.get(url)
            data = response.json()
            
            if data.get('result') == 'success':
                currency_codes = [code for code, name in data.get('supported_codes', [])]
                self.from_currency['values'] = currency_codes
                self.to_currency['values'] = currency_codes
                
                # Установка стандартных валют
                if currency_codes:
                    self.from_currency.set('USD')
                    self.to_currency.set('EUR' if 'EUR' in currency_codes else currency_codes[0])
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить список валют")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке валют: {str(e)}")
            
    def convert_currency(self):
        """Конвертация валюты"""
        # Проверка ввода
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число")
            return
            
        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()
        
        if not from_cur or not to_cur:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите валюты")
            return
            
        try:
            # Запрос к API
            url = f"{self.base_url}{self.api_key}/pair/{from_cur}/{to_cur}/{amount}"
            response = requests.get(url)
            data = response.json()
            
            if data.get('result') == 'success':
                converted_amount = data.get('conversion_result')
                rate = data.get('conversion_rate')
                
                result_text = f"{amount:.2f} {from_cur} = {converted_amount:.2f} {to_cur} (Курс: {rate:.4f})"
                self.result_label.config(text=result_text)
                
                # Сохранение в историю
                self.add_to_history(from_cur, to_cur, amount, converted_amount, rate)
                
                # Обновление таблицы
                self.update_history_table()
                
            else:
                error_message = data.get('error-type', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка", f"Ошибка конвертации: {error_message}")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            
    def add_to_history(self, from_cur, to_cur, amount, result, rate):
        """Добавление записи в историю"""
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from_currency": from_cur,
            "to_currency": to_cur,
            "amount": amount,
            "result": result,
            "rate": rate
        }
        self.history.append(entry)
        self.save_history()
        
    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")
            
    def load_history(self):
        """Загрузка истории из JSON файла"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            self.history = []
            
    def update_history_table(self):
        """Обновление таблицы истории"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Добавление данных
        for entry in reversed(self.history[-50:]):  # Показываем последние 50 записей
            self.tree.insert("", tk.END, values=(
                entry.get('date', ''),
                entry.get('from_currency', ''),
                entry.get('to_currency', ''),
                f"{entry.get('amount', 0):.2f}",
                f"{entry.get('result', 0):.2f}"
            ))
            
    def load_history_gui(self):
        """Загрузка истории через GUI"""
        self.load_history()
        self.update_history_table()
        messagebox.showinfo("Успех", "История загружена")
        
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()
            messagebox.showinfo("Успех", "История очищена")
            
    def export_history(self):
        """Экспорт истории в текстовый файл"""
        if not self.history:
            messagebox.showwarning("Предупреждение", "История пуста")
            return
            
        try:
            filename = f"history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("История конвертаций валют\n")
                f.write("=" * 50 + "\n\n")
                for entry in self.history:
                    f.write(f"Дата: {entry.get('date', '')}\n")
                    f.write(f"Из: {entry.get('from_currency', '')} -> В: {entry.get('to_currency', '')}\n")
                    f.write(f"Сумма: {entry.get('amount', 0):.2f} -> Результат: {entry.get('result', 0):.2f}\n")
                    f.write(f"Курс: {entry.get('rate', 0):.4f}\n")
                    f.write("-" * 30 + "\n")
            messagebox.showinfo("Успех", f"История экспортирована в файл {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
