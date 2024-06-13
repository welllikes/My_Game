import tkinter as tk
from tkinter import filedialog, colorchooser
from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab
import random

# Класс для создания главного меню
class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Главное меню")
        self.root.geometry("600x400")  # Размеры большого окна
        self.root.configure(bg="#f0f0f0")  # Установка цвета фона

        self.label = tk.Label(root, text="Добро пожаловать в раскраску", font=("Arial", 24, "bold"), bg="#f0f0f0")
        self.label.pack(pady=20)

        self.start_button = tk.Button(root, text="Начать рисовать", command=self.start_application,
                                    bg="#84C084", fg="white", padx=20, pady=10, font=("Arial", 16, "bold"), borderwidth=0)
        self.start_button.pack(pady=20, fill=tk.X)

        self.load_button = tk.Button(root, text="Загрузить изображение", command=self.load_image,
                                    bg="#84AD8C", fg="white", padx=20, pady=10, font=("Arial", 16, "bold"), borderwidth=0)
        self.load_button.pack(pady=20, fill=tk.X)

        self.exit_button = tk.Button(root, text="Выйти", command=root.quit,
                                    bg="#DE8971", fg="white", padx=20, pady=10, font=("Arial", 16, "bold"), borderwidth=0)
        self.exit_button.pack(pady=20, fill=tk.X)

    def start_application(self):
        self.open_coloring_app()

    def load_image(self):
        self.open_coloring_app(load_image=True)

    def open_coloring_app(self, load_image=False):
        self.root.destroy()
        app = ColoringApp(load_image)

# Класс для создания приложения раскраски
class ColoringApp:
    def __init__(self, load_image=False):
        self.root = tk.Tk()
        self.root.title("Раскраска")

        self.canvas_width = 600
        self.canvas_height = 400

        self.background_image = None
        self.image_id = None

        self.undo_stack = []
        self.redo_stack = []

        # Создание главной рамки для размещения всех виджетов
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        # Создание рамки для кнопок управления слева
        self.controls_frame = ttk.Frame(self.main_frame, width=150)
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Кнопки для отмены действий
        self.undo_button = tk.Button(self.controls_frame, text="Отмена", command=self.undo,
                                    bg="#85C1E9", fg="white", font=("Arial", 12, "bold"), borderwidth=0)
        self.undo_button.pack(padx=10, pady=5, fill=tk.X)

        # Создание рамки для холста
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Создание холста для рисования
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.mouse_pressed = False

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Ползунки для прокрутки холста
        self.scroll_x = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Настройка холста для использования ползунков
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        # Создание кнопок для различных функций с разными цветами
        self.load_button = tk.Button(self.controls_frame, text="Загрузить изображение", command=self.load_image,
                                    bg="#48C9B0", fg="white", font=("Arial", 12, "bold"), borderwidth=0)
        self.load_button.pack(padx=10, pady=5, fill=tk.X)

        self.save_button = tk.Button(self.controls_frame, text="Сохранить изображение", command=self.save_image,
                                    bg="#60A872", fg="white", font=("Arial", 12, "bold"), borderwidth=0)
        self.save_button.pack(padx=10, pady=5, fill=tk.X)

        self.clear_button = tk.Button(self.controls_frame, text="Очистка холста", command=self.clear_canvas,
                                      bg="#DE8971", fg="white", font=("Arial", 12, "bold"), borderwidth=0)
        self.clear_button.pack(padx=10, pady=5, fill=tk.X)

        self.color_button = tk.Button(self.controls_frame, text="Палитра", command=self.choose_color,
                                     bg="#FFC300", fg="white", font=("Arial", 12, "bold"), borderwidth=0)
        self.color_button.pack(padx=10, pady=5, fill=tk.X)

        # Выпадающее меню для выбора типа кисти
        self.brush_type = tk.StringVar()
        self.brush_type.set("Кисти")  # Тип кисти по умолчанию
        self.brush_menu = tk.OptionMenu(self.controls_frame, self.brush_type, "Кисть", "Карандаш", "Спрей")
        self.brush_menu.configure(bg="#D2B4DE", fg="white", font=("Arial", 12, "bold"), borderwidth=0)
        self.brush_menu.pack(padx=10, pady=5, fill=tk.X)

        # Кнопка для переключения режима ластика
        self.eraser_button = tk.Button(self.controls_frame, text="Ластик", command=self.toggle_eraser,
                                   bg="#FC7464", fg="white", font=("Arial", 12, "bold"), borderwidth=0)
        self.eraser_button.pack(padx=10, pady=5, fill=tk.X)

        # Ползунок для регулировки размера кисти
        self.brush_size_slider = tk.Scale(self.controls_frame, from_=1, to=50, orient=tk.HORIZONTAL, label="Размер кисти",
                                          command=self.set_brush_size, bg="#D4E6F1", font=("Arial", 12, "italic"))
        self.brush_size_slider.pack(padx=10, pady=5, fill=tk.X)
        self.brush_size_slider.set(5)  # Размер кисти по умолчанию

        # Кнопка выхода из приложения
        self.exit_button = tk.Button(self.controls_frame, text="Выход", command=self.root.quit,
                                 bg="#E74C3C", fg="white", font=("Arial", 12, "bold"), borderwidth=0)
        self.exit_button.pack(padx=10, pady=5, fill=tk.X)

        self.root.update()  # Обновление окна, чтобы получить правильные размеры
        min_width = self.controls_frame.winfo_width() + self.canvas_width
        min_height = self.canvas_height
        self.root.minsize(min_width, min_height)

        self.color = "#000000"
        self.brush_size = 5
        self.eraser_mode = False
        if load_image:
            self.load_image()
        # Привязка функции рисования к движению мыши
        self.canvas.bind("<B1-Motion>", self.draw)

        # Открытие окна на весь экран
        self.root.state('zoomed')

    def run(self):
        # Запуск цикла обработки событий Tkinter
        self.root.mainloop()

    def on_button_press(self, event):
        self.mouse_pressed = True
        self.current_line = []
        self.save_canvas_state()

    def on_button_release(self, event):
        self.mouse_pressed = False
        self.save_canvas_state()

    def load_image(self):
        # Открытие диалога для выбора изображения
        file = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file:
            self.clear_canvas()  # Очистка холста перед загрузкой нового изображения
            self.background_image = Image.open(file)

            # Получение размеров экрана
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight() - 100  # Учитываем панель задач и заголовок окна

            # Изменение размера изображения, если оно больше экрана
            if self.background_image.width > screen_width or self.background_image.height > screen_height:
                ratio = min(screen_width / self.background_image.width, screen_height / self.background_image.height)
                new_width = int(self.background_image.width * ratio)
                new_height = int(self.background_image.height * ratio)
                self.background_image = self.background_image.resize((new_width, new_height), Image.LANCZOS)

            self.image_tk = ImageTk.PhotoImage(self.background_image)
            self.canvas_width, self.canvas_height = self.background_image.size
            self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height), width=self.canvas_width, height=self.canvas_height)

            # Отображение изображения на холсте
            if self.image_id:
                self.canvas.delete(self.image_id)
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
            self.undo_stack = []
            self.redo_stack = []
            # Настройка размера окна для соответствия холсту и кнопкам управления
            self.root.geometry(f"{self.canvas_width + 150}x{self.canvas_height}")
            self.root.resizable(False, False)
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk, tag='background')

            # Отображение изображения на холсте
            if self.image_id:
                self.canvas.delete(self.image_id)
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
            self.undo_stack = []
            self.redo_stack = []
            # Настройка размера окна для соответствия холсту и кнопкам управления
            self.root.geometry(f"{self.canvas_width + 150}x{self.canvas_height}")
            self.root.resizable(False, False)
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk, tag='background')

    def draw(self, event):
        if self.mouse_pressed:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            if self.eraser_mode:
                self.draw_eraser(x, y)
            else:
                brush_type = self.brush_type.get()
                if brush_type == "Кисти":
                    item = self.draw_round_brush(x, y)
                elif brush_type == "Карандаш":
                    self.draw_square_brush(x, y)
                elif brush_type == "Спрей":
                    self.draw_spray_brush(x, y)

    def save_canvas_state(self):
        if not self.mouse_pressed:
            self.undo_stack.append(self.get_canvas_image())

    def get_canvas_image(self):
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        image = ImageGrab.grab(bbox=(x, y, x1, y1))
        return image

    def undo(self):
        if self.undo_stack:
            # Элемент, предшествующий текущему состоянию будет самым новым в redo_stack
            if len(self.redo_stack) >= 6:
                self.redo_stack.pop(0)  # Если в redo_stack уже есть три состояния, удаляем самое старое
            # Текущее состояние перемещаем в redo_stack перед восстановлением из undo_stack
            self.redo_stack.append(self.undo_stack.pop())

            # Проверяем, не является ли следующий элемент в undo_stack последним состоянием
            if self.undo_stack:
                self.load_canvas_state(self.undo_stack[-1])
            else:
                self.canvas.delete("all")
                # Восстанавливаем фоновое изображение, если оно существует
                if self.background_image:
                    self.image_tk = ImageTk.PhotoImage(self.background_image)
                    self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

    def redo(self):
        if self.redo_stack:
            ps_data = self.redo_stack.pop()
            self.undo_stack.append(ps_data)
            self.load_canvas_state(ps_data)

    def save_canvas_state_to_redo(self):
        if len(self.redo_stack) >= 3:
            self.redo_stack.pop(0)
        self.redo_stack.append(self.get_canvas_image())

    def save_canvas_state_to_undo(self):
        self.undo_stack.append(self.get_canvas_image())

    def load_canvas_state(self, image):
        self.image_tk = ImageTk.PhotoImage(image)
        # Очищаем холст и вставляем изображение
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)
        self.canvas.image = self.image_tk

    def draw_round_brush(self, x, y):
        # Рисование круглой кистью
        x1, y1 = (x - self.brush_size), (y - self.brush_size)
        x2, y2 = (x + self.brush_size), (y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill=self.color, outline="", tags=("drawing",))

    def draw_square_brush(self, x, y):
        # Рисование квадратной кистью
        x1, y1 = (x - self.brush_size), (y - self.brush_size)
        x2, y2 = (x + self.brush_size), (y + self.brush_size)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.color, outline="", tags=("drawing",))

    def draw_spray_brush(self, x, y):
        # Рисование распылителем
        for _ in range(30):
            dx = random.randint(-self.brush_size, self.brush_size)
            dy = random.randint(-self.brush_size, self.brush_size)
            self.canvas.create_oval(x + dx, y + dy, x + dx + 1, y + dy + 1, fill=self.color, outline="",
                                    tags=("drawing",))

    def draw_eraser(self, x, y):
        # Рисование ластиком
        eraser_size = self.brush_size / 2
        overlapping_items = self.canvas.find_overlapping(x - eraser_size, y - eraser_size, x + eraser_size,
                                                         y + eraser_size)
        for item in overlapping_items:
            if "drawing" in self.canvas.gettags(item):
                self.canvas.delete(item)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG images", "*.png")])
        if not file_path:
            return
        gif_path = file_path.replace('.png', '.gif')
        self.canvas.postscript(file=gif_path, colormode='color')
        with Image.open(gif_path) as img:
            img.save(file_path, 'PNG')
        import os
        os.remove(gif_path)
        print(f"Изображение успешно сохранено как: {file_path}")

    def clear_canvas(self):
        # Очистка холста
        self.canvas.delete("all")
        for item in self.canvas.find_withtag("drawing"):
            self.canvas.delete(item)

    def choose_color(self):
        # Открытие диалога выбора цвета
        color = colorchooser.askcolor()
        if color:
            self.color = color[1]

    def toggle_eraser(self):
        # Переключение режима ластика
        self.eraser_mode = not self.eraser_mode

    def set_brush_size(self, size):
        # Установка размера кисти
        self.brush_size = int(size)

if __name__ == "__main__":
    root = tk.Tk()
    main_menu = MainMenu(root)
    root.mainloop()