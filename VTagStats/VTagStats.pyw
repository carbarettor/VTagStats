import os
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import ctypes
import json

def resource_path(relative_path):
    """
    Получает абсолютный путь к ресурсам.
    Работает как в режиме разработки, так и для скомпилированного PyInstaller (.exe).
    """
    try:
        # PyInstaller создает временную папку _MEIPASS при запуске .exe
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Скрываем консоль в Windows
if sys.platform == 'win32':
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def log_last_opened(file_path, log_file=None):
    if log_file is None:
        log_file = resource_path(os.path.join("Data", "open_file.txt"))
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "w", encoding="utf-8") as log:
            log.write(f"VTagStats version был открыт {current_time}\n")
    except Exception:
        pass

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VTagStats")
        self.geometry("1500x600")
        self.configure(bg="#F0F0F0")
        
        # Текущая тема (по умолчанию светлая)
        self.current_theme = "light"
        
        # Установка иконки из папки Data через resource_path
        icon_path = resource_path(os.path.join("Data", "icon.ico"))
        if sys.platform == 'win32' and os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        self.config = self.load_config()
        self.create_widgets()
        log_last_opened(sys.argv[0])
        
        # Загружаем картинки при инициализации
        self.images = {}

    def load_config(self):
        """Загружает конфигурацию из Data/config.json"""
        config_path = resource_path(os.path.join("Data", "config.json"))
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"ascii_art_path": resource_path(os.path.join("Data", "description.txt"))}

    def load_ascii_art(self):
        """Загружает ASCII-арт из Data/description.txt"""
        try:
            art_path = resource_path(os.path.join("Data", "description.txt"))
            with open(art_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            return f"Ошибка загрузки арта: {str(e)}"

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="white",
            fg="black",
            padx=10,
            pady=10
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Вставляем ASCII-арт
        ascii_art = self.load_ascii_art()
        self.text_area.insert(tk.END, ascii_art)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        buttons = [
            ("1. Кнопка", self.button_function),
            ("2. Очистка экрана", self.button_function_2),
            ("3. Модуль random", self.button_function_3),
            ("4. Модуль sys", self.button_function_4),
            ("5. Модуль min()", self.button_function_5),
            ("6. О программе", self.button_function_0),
            ("7. Показать лог", self.show_log_file),
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, width=35)
            btn.pack(pady=7)

        # Маленькие кнопки для ресурсов
        small_btn_frame = ttk.Frame(button_frame)
        small_btn_frame.pack(pady=10)
        
        # Вторая маленькая кнопка - Выход
        small_btn_2 = ttk.Button(
            small_btn_frame, 
            text="Выход", 
            command=self.destroy,
            width=12
        )
        small_btn_2.pack(side=tk.TOP, pady=2)

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

    def show_log_file(self):
        """Отображает содержимое файла лога в текстовом поле"""
        self.clear_text()
        log_file = resource_path(os.path.join("Data", "log.txt"))
        try:
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_area.insert(tk.END, f"Содержимое файла в папке 📁Data 📄log \n{content}")
            else:
                self.text_area.insert(tk.END, "Файл лога не найден.")
        except Exception as e:
            self.text_area.insert(tk.END, f"Ошибка при чтении файла: {e}")

    def button_function(self):
        self.clear_text()
        text = """Вот простой пример, как сделать кнопку на Python с помощью библиотеки tkinter:
              Пример: простое окно с кнопкой
                import tkinter as tk
                def on_click():
                print("Кнопка нажата!")

                    # Создаем окно
                window = tk.Tk()
                window.title("Пример кнопки")
                window.geometry("300x150")  # Ширина x Высота

                    #Создаем кнопку
                button = tk.Button(window, text="Нажми меня", command=on_click)
                button.pack(pady=20)  # Располагаем кнопку по центру

                    # Запускаем окно
                window.mainloop()
        🔧 Что делает этот код:
Создает окно.

В нем — кнопку с надписью "Нажми меня".

При нажатии на кнопку в консоли появляется текст "Кнопка нажата!"."""
        self.text_area.insert(tk.END, text)

    def button_function_2(self):
        self.clear_text()
        text = """Чтобы очистить экран в Python (в окне консоли/терминала), можно использовать один из следующих способов — в зависимости от операционной системы:
                                           Способ 1: Через os.system
        import os

    def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

    # Пример использования
    print("Текст до очистки")
    nput("Нажми Enter для очистки экрана...")
    clear_screen()
    print("Экран очищен!")

    cls — для Windows.

    clear — для Linux/macOS.


                                           Способ 2: Только для Windows (если ты точно знаешь, что у тебя Windows)
        import os
    os.system('cls')
                                            
                                           Способ 3: Очистка в Tkinter (если у тебя окно, а не консоль)
                Если ты работаешь с графическим окном tkinter, то "очистка экрана" означает удаление всех виджетов:
        import tkinter as tk

    def clear_window():
        for widget in window.winfo_children():
            widget.destroy()

    window = tk.Tk()
    window.geometry("300x200")

    tk.Label(window, text="Привет!").pack()
    tk.Button(window, text="Очистить экран", command=clear_window).pack()

    window.mainloop()


"""
        self.text_area.insert(tk.END, text)

    def button_function_3(self):
        self.clear_text()
        text = """Хочешь использовать random в Python? Вот основные примеры, как использовать модуль random:
                                           Импорт модуля
import random
                                           1. Случайное число
                                    Целое число от 1 до 10:
num = random.randint(1, 10)
print(num)
                                    Дробное число от 0 до 1:
num = random.random()
print(num)
                                    Дробное число от 5 до 10:
num = random.uniform(5, 10)
print(num)
                                           2. Случайный выбор из списка
fruits = ['яблоко', 'банан', 'груша']
choice = random.choice(fruits)
print(choice)
                                           3. Перемешать список
numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)
print(numbers)
                                           4. Выбрать несколько случайных элементов
nums = [10, 20, 30, 40, 50]
sample = random.sample(nums, 2)  # 2 случайных элемента
print(sample)

"""
        self.text_area.insert(tk.END, text)
    
    def button_function_4(self):
        self.clear_text()
        text="""Модуль sys в Python используется для работы с системными параметрами и функциями, связанными с интерпретатором Python.

                                        Вот основные примеры, как использовать sys:
                                           Импорт модуля
import sys
                                           Полезные функции и свойства
import sys

print("Программа работает")
sys.exit()  # завершение
print("Этот код не выполнится")
                                    2. sys.argv — аргументы командной строки
import sys

print("Имя файла:", sys.argv[0])
print("Аргументы:", sys.argv[1:])
                                    bash        Пример запуска из терминала:

python script.py hello world
                                    less        Вывод будет:
Имя файла: script.py
Аргументы: ['hello', 'world']
                                    3. sys.platform — узнать платформу
import sys

print(sys.platform)  # Пример: 'win32', 'linux', 'darwin'
                                    4. sys.version — версия Python
import sys

print(sys.version)
                                    5. sys.path — список путей для поиска модулей
import sys

for path in sys.path:
    print(path)
"""
        self.text_area.insert(tk.END, text)

    def button_function_5(self):
        self.clear_text()
        text = """1. min() — нахождение минимального значения (расширенный разбор)
        Функция min() — это один из самых мощных встроенных инструментов Python. На первый взгляд кажется, что она просто ищет самое маленькое число, но на самом деле её возможности гораздо шире. Она умеет работать со строками, сравнивать отдельные аргументы, искать элементы по заданным правилам и защищать код от ошибок.
        
        Вот подробные примеры того, как можно использовать min() в разных ситуациях:
        
        Пример 1: Поиск самого маленького числа в списке (Базовый уровень)
Самый частый сценарий — у вас есть список данных (например, цены товаров, температуры за неделю), и вам нужно найти минимум.


температуры = [22, 15, 18, -3, 5, 0]
самая_холодная = min(температуры)

print("Минимальная температура:", самая_холодная)
        
        Вывод будет:
        
Минимальная температура: -3
        
        Пример 2: Сравнение нескольких переменных напрямую
Не обязательно создавать список. Вы можете передать в функцию любые числа, переменные или математические выражения прямо через запятую.
        
игрок1_очки = 150
игрок2_очки = 95
игрок3_очки = 210

худший_результат = min(игрок1_очки, игрок2_очки, игрок3_очки, 50)
print("Самый низкий балл:", худший_результат)

        Вывод будет:
        
Самый низкий балл: 50
        
        Пример 3: Работа с текстом (Сортировка по алфавиту)
Если передать в функцию текст, min() не сломается. Она посмотрит на первые буквы каждого слова и вернет то, которое идет раньше в алфавите.
        
имена = ["Ян", "Борис", "Анна", "Виктор"]
первое_по_алфавиту = min(имена)

print("Первое имя по алфавиту:", первое_по_алфавиту)
        
        Вывод будет:
        
Первое имя по алфавиту: Анна
        
        Пример 4: Использование параметра key (Продвинутый уровень)
        У min() есть «секретная» настройка key, которая меняет логику поиска. Например, вам нужно найти не слово по алфавиту, а самое короткое слово. Для этого мы говорим функции: «ищи минимум по длине (len)».

слова = ["Программирование", "Кот", "Информатика", "Код"]

# Указываем, что сравнивать нужно по длине (len)
самое_короткое = min(слова, key=len)

print("Самое короткое слово:", самое_короткое)

        Вывод будет:

Самое короткое слово: Кот

        Пример 5: Защита от ошибок с параметром default (Безопасность кода)
Если вы попытаетесь скормить функции пустой список, программа "упадет" и выдаст ошибку ValueError. Чтобы этого избежать, можно задать запасной вариант ответа через настройку default.

пустая_корзина = []

# Если корзина пуста, функция не сломается, а вернет число 0
минимальная_цена = min(пустая_корзина, default=0)

print("Минимальная цена покупки:", минимальная_цена)

        Вывод будет:

Минимальная цена покупки: 0
"""

        self.text_area.insert(tk.END, text)

    def button_function_0(self):
        self.clear_text()
        text = """О программе:
[ 1.0.0  version ]

Веб-сайт: https://runa-apps.kz/school/students/anton/vtadstats/
Github: https://github.com/carbarettor/VTagStats/

Проверяется и запускается программа на системе Mint linux

OS: Linux Mint 22.3 x86_64
CPU: Intel i5-2310 (4) @ 3.200GHz 
GPU: NVIDIA GeForce GT 630 OEM
Memory: 8GB   

Характистики второго пк проверенные спомощью команды neofetch

И редактируется на основноп пк

OS: Windows 11 Pro
CPU: 12th Gen Intel(R) Core(TM) I5-12400F
GPU: NVIDIA GeForce RTX 3050 8GB
Memory:  16GB
 
"""
        self.text_area.insert(tk.END, text)

if __name__ == "__main__":
    app = App()
    app.mainloop()