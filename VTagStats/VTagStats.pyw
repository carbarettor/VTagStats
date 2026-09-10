import os
import datetime
import tkinter as tk
from tkinter import ttk
import sys
import ctypes
import json

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if sys.platform == 'win32':
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def log_last_opened(file_path, log_file=None):
    if log_file is None:
        log_file = resource_path(os.path.join("Data", "log.txt"))
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "w", encoding="utf-8") as log:
            log.write(f"VTagStats version был открыт {current_time}\n")
    except Exception:
        pass


class RoundedFrame(tk.Canvas):
    """Кастомный закругленный контейнер для текстового поля."""
    def __init__(self, parent, radius=33, bg_color="#FFFFFF", border_bg="#F0F0F0", **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, bg=border_bg, **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_bg = border_bg
        self.rect_id = None
        self.bind("<Configure>", self._draw)

    def _round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w > 1 and h > 1:
            self.rect_id = self._round_rect(1, 1, w - 1, h - 1, self.radius, fill=self.bg_color, outline=self.bg_color)

    def set_theme(self, bg_color, border_bg):
        self.bg_color = bg_color
        self.border_bg = border_bg
        self.configure(bg=border_bg)
        self._draw()


class CustomScrollbar(tk.Canvas):
    """Сверхтонкий кастомный скроллбар."""
    def __init__(self, parent, target_widget, width=6, bg_color="#1E1E1E", thumb_color="#444444", **kwargs):
        super().__init__(parent, width=width, highlightthickness=0, bd=0, bg=bg_color, **kwargs)
        self.target = target_widget
        self.thumb_color = thumb_color
        self.bg_color = bg_color
        self.width = width
        
        self.target.configure(yscrollcommand=self.set_scroll)
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        
        self.target.bind("<MouseWheel>", self._on_mousewheel, add="+")
        self.target.bind("<Button-4>", self._on_mousewheel, add="+")
        self.target.bind("<Button-5>", self._on_mousewheel, add="+")

    def draw_thumb(self, y1, y2):
        self.delete("all")
        r = self.width // 2
        x1, x2 = 1, self.width - 1
        if y2 - y1 < self.width:
            y2 = y1 + self.width

        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        self.create_polygon(points, smooth=True, fill=self.thumb_color, outline=self.thumb_color)

    def set_scroll(self, first, last):
        first = float(first)
        last = float(last)
        height = self.winfo_height()
        if height <= 1:
            return
        y1 = first * height
        y2 = last * height
        self.draw_thumb(y1, y2)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.target.yview_scroll(-2, "units")
        elif event.num == 5:
            self.target.yview_scroll(2, "units")
        elif event.delta:
            self.target.yview_scroll(int(-1 * (event.delta / 60)), "units")
        return "break"

    def on_click(self, event):
        height = self.winfo_height()
        if height > 0:
            fraction = event.y / height
            self.target.yview_moveto(fraction)

    def on_drag(self, event):
        height = self.winfo_height()
        if height > 0:
            fraction = event.y / height
            self.target.yview_moveto(fraction)

    def set_theme(self, bg_color, thumb_color):
        self.bg_color = bg_color
        self.thumb_color = thumb_color
        self.configure(bg=bg_color)
        first, last = self.target.yview()
        self.set_scroll(first, last)


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=220, height=32,
                 radius=10, bg_color="#E1E1E1", fg_color="#000000",
                 hover_color="#D0D0D0", canvas_bg="#F0F0F0",
                 font=("TkDefaultFont", 9)):
        super().__init__(parent, width=width, height=height,
                          highlightthickness=0, bd=0, bg=canvas_bg)
        self.command = command
        self.radius = radius
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self._btn_width = width
        self._btn_height = height

        self.shape_id = self._round_rect(1, 1, width - 1, height - 1, radius,
                                          fill=bg_color, outline=bg_color)
        self.label_id = self.create_text(width // 2, height // 2, text=text,
                                          fill=fg_color, font=font)

        for tag in (self.shape_id, self.label_id):
            self.tag_bind(tag, "<Button-1>", self._on_click)
            self.tag_bind(tag, "<Enter>", self._on_enter)
            self.tag_bind(tag, "<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.configure(cursor="hand2")

    def _round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, event=None):
        self.itemconfig(self.shape_id, fill=self.hover_color, outline=self.hover_color)

    def _on_leave(self, event=None):
        self.itemconfig(self.shape_id, fill=self.bg_color, outline=self.bg_color)

    def _on_click(self, event=None):
        if self.command:
            self.command()

    def set_theme(self, bg_color, fg_color, hover_color, canvas_bg):
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.configure(bg=canvas_bg)
        self.itemconfig(self.shape_id, fill=bg_color, outline=bg_color)
        self.itemconfig(self.label_id, fill=fg_color)


class App(tk.Tk):

    THEMES = {
        "light": {
            "bg": "#F0F0F0",
            "frame_bg": "#F0F0F0",
            "text_bg": "#FFFFFF",
            "text_fg": "#000000",
            "btn_bg": "#E1E1E1",
            "btn_fg": "#000000",
            "btn_active": "#D0D0D0",
            "scrollbar_bg": "#FFFFFF",
            "scrollbar_thumb": "#A0A0A0",
        },
        "dark": {
            "bg": "#2B2B2B",
            "frame_bg": "#2B2B2B",
            "text_bg": "#1E1E1E",
            "text_fg": "#E0E0E0",
            "btn_bg": "#3C3F41",
            "btn_fg": "#E0E0E0",
            "btn_active": "#4E5254",
            "scrollbar_bg": "#1E1E1E",
            "scrollbar_thumb": "#555555",
        },
    }

    def __init__(self):
        super().__init__()
        self.title("VTagStats")
        self.geometry("1500x600")

        self.config_data = self.load_config()

        self.current_theme = self.config_data.get("theme", "light")
        if self.current_theme not in self.THEMES:
            self.current_theme = "light"

        icon_path = resource_path(os.path.join("Data", "icon.ico"))
        if sys.platform == 'win32' and os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.theme_choice = tk.StringVar(value=self.current_theme)

        self.menu_open = False

        self.create_menu()
        self.create_widgets()
        self.apply_theme()
        self.bind("<Map>", lambda e: self._apply_title_bar_theme(), add="+")

        log_last_opened(sys.argv[0])

        self.images = {}

    def load_config(self):
        config_path = resource_path(os.path.join("Data", "config.json"))
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"ascii_art_path": resource_path(os.path.join("Data", "description.txt"))}

    def save_config(self):
        config_path = resource_path(os.path.join("Data", "config.json"))
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def load_ascii_art(self):
        try:
            art_path = resource_path(os.path.join("Data", "description.txt"))
            with open(art_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            return f"Ошибка загрузки арта: {str(e)}"

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.theme_choice.set(self.current_theme)
        self.config_data["theme"] = self.current_theme
        self.save_config()
        self.apply_theme()

    def on_theme_choice(self):
        self.current_theme = self.theme_choice.get()
        self.config_data["theme"] = self.current_theme
        self.save_config()
        self.apply_theme()
        self.close_dropdown()

    def apply_theme(self):
        theme = self.THEMES[self.current_theme]

        self.configure(bg=theme["bg"])

        style = ttk.Style(self)
        style.configure("TFrame", background=theme["bg"])

        if hasattr(self, "main_frame"):
            self.main_frame.configure(style="TFrame")
        if hasattr(self, "button_frame"):
            self.button_frame.configure(style="TFrame")
        if hasattr(self, "small_btn_frame"):
            self.small_btn_frame.configure(style="TFrame")

        if hasattr(self, "text_container"):
            self.text_container.set_theme(bg_color=theme["text_bg"], border_bg=theme["bg"])

        if hasattr(self, "scrollbar"):
            self.scrollbar.set_theme(theme["scrollbar_bg"], theme["scrollbar_thumb"])

        if hasattr(self, "action_buttons"):
            for btn in self.action_buttons:
                btn.set_theme(
                    bg_color=theme["btn_bg"], fg_color=theme["btn_fg"],
                    hover_color=theme["btn_active"], canvas_bg=theme["bg"],
                )

        if hasattr(self, "text_area"):
            self.text_area.configure(
                bg=theme["text_bg"],
                fg=theme["text_fg"],
                insertbackground=theme["text_fg"],
            )

        if hasattr(self, "menubar_frame"):
            self.menubar_frame.configure(bg=theme["btn_bg"])
            self.settings_menu_btn.configure(
                bg=theme["btn_bg"], fg=theme["btn_fg"],
                activebackground=theme["btn_active"], activeforeground=theme["btn_fg"],
            )
            self.dropdown_frame.configure(bg=theme["frame_bg"], highlightbackground=theme["btn_active"])
            for child in self.dropdown_frame.winfo_children():
                if isinstance(child, tk.Radiobutton):
                    child.configure(
                        bg=theme["frame_bg"], fg=theme["btn_fg"],
                        activebackground=theme["btn_active"], activeforeground=theme["btn_fg"],
                        selectcolor=theme["btn_bg"],
                    )
                elif isinstance(child, tk.Label):
                    child.configure(
                        bg=theme["frame_bg"], fg=theme["btn_fg"],
                    )

        self._apply_title_bar_theme()

    def _apply_title_bar_theme(self):
        if sys.platform != 'win32':
            return
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            value = ctypes.c_int(1 if self.current_theme == "dark" else 0)
            for attribute in (20, 19):
                result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value)
                )
                if result == 0:
                    break
            w, h = self.winfo_width(), self.winfo_height()
            if w > 1 and h > 1:
                self.geometry(f"{w+1}x{h}")
                self.after(10, lambda: self.geometry(f"{w}x{h}"))
        except Exception:
            pass

    def create_menu(self):
        self.menubar_frame = tk.Frame(self, bd=0, highlightthickness=0)
        self.menubar_frame.pack(side=tk.TOP, fill=tk.X)

        self.settings_menu_btn = tk.Label(
            self.menubar_frame, text="  Настройки  ", padx=6, pady=4, cursor="hand2"
        )
        self.settings_menu_btn.pack(side=tk.LEFT)
        self.settings_menu_btn.bind("<Button-1>", lambda e: self.toggle_dropdown())

        self.dropdown_frame = tk.Frame(self, bd=1, relief=tk.SOLID)

        tk.Radiobutton(
            self.dropdown_frame, text="☀ Светлая тема", variable=self.theme_choice,
            value="light", command=self.on_theme_choice, indicatoron=True,
            anchor="w", padx=10, pady=5, borderwidth=0, highlightthickness=0,
        ).pack(fill=tk.X)
        tk.Radiobutton(
            self.dropdown_frame, text="🌙 Тёмная тема", variable=self.theme_choice,
            value="dark", command=self.on_theme_choice, indicatoron=True,
            anchor="w", padx=10, pady=5, borderwidth=0, highlightthickness=0,
        ).pack(fill=tk.X)

        about_lbl = tk.Label(
            self.dropdown_frame, text="О программе", anchor="w",
            padx=10, pady=5, cursor="hand2"
        )
        about_lbl.pack(fill=tk.X)
        about_lbl.bind("<Button-1>", lambda e: (self.button_function_0(), self.close_dropdown()))

        self.bind_all("<Button-1>", self._maybe_close_dropdown, add="+")

    def toggle_dropdown(self):
        self.close_dropdown() if self.menu_open else self.open_dropdown()

    def open_dropdown(self):
        self.dropdown_frame.place(in_=self.menubar_frame, x=0, rely=1, anchor="nw")
        self.dropdown_frame.lift()
        self.menu_open = True

    def close_dropdown(self):
        self.dropdown_frame.place_forget()
        self.menu_open = False

    def _maybe_close_dropdown(self, event):
        if not self.menu_open:
            return
        widget = event.widget
        for owner in (self.dropdown_frame, self.settings_menu_btn):
            w = widget
            while w is not None:
                if w == owner:
                    return
                w = w.master
        self.close_dropdown()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Закругленный контейнер для текста (радиус 33)
        self.text_container = RoundedFrame(self.main_frame, radius=33)
        self.text_container.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.text_area = tk.Text(
            self.text_container,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="white",
            fg="black",
            padx=15,
            pady=15,
            bd=0,
            highlightthickness=0
        )
        
        self.scrollbar = CustomScrollbar(
            self.text_container, 
            target_widget=self.text_area,
            width=6,
            bg_color="#1E1E1E",
            thumb_color="#555555"
        )

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

        ascii_art = self.load_ascii_art()
        self.text_area.insert(tk.END, ascii_art)

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        buttons = [
            ("1. Кнопка", self.button_function),
            ("2. Очистка экрана", self.button_function_2),
            ("3. Модуль random", self.button_function_3),
            ("4. Модуль sys", self.button_function_4),
            ("5. Модуль min()", self.button_function_5),
            ("6. О программе", self.button_function_0),
            ("7. Показать лог", self.show_log_file),
        ]

        self.action_buttons = []
        theme = self.THEMES[self.current_theme]
        for text, command in buttons:
            btn = RoundedButton(
                self.button_frame, text=text, command=command,
                width=220, height=32, radius=10,
                bg_color=theme["btn_bg"], fg_color=theme["btn_fg"],
                hover_color=theme["btn_active"], canvas_bg=theme["bg"],
            )
            btn.pack(pady=4)
            self.action_buttons.append(btn)

        self.small_btn_frame = ttk.Frame(self.button_frame)
        self.small_btn_frame.pack(pady=6)

        small_btn_2 = RoundedButton(
            self.small_btn_frame, text="Выход", command=self.destroy,
            width=100, height=30, radius=10,
            bg_color=theme["btn_bg"], fg_color=theme["btn_fg"],
            hover_color=theme["btn_active"], canvas_bg=theme["bg"],
        )
        small_btn_2.pack(side=tk.TOP, pady=2)
        self.action_buttons.append(small_btn_2)

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

    def show_log_file(self):
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
[ 1.0.1  version ]

Веб-сайт: https://carbarettor.github.io/VTagStats/
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