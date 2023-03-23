import platform
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from PIL import ImageTk, Image

from Processor.Actions.remove_audio import RemoveAudio
from Processor.Actions.rotate import Rotate
from Processor.Actions.change_speed import ChangeSpeed
from Processor.Actions.concatenate import Concatenate
from Processor.Actions.crop import Crop
from Processor.Actions.add_image import AddImage
from Processor.action import Action
from Processor.ineedextraslider import INeedExtraSlider
from Processor.ineedimage import INeedImage
from Processor.videoboundsforslider import VideoBoundsForSlider
from Processor.params import Params
from file import File


# from moviepy.config import change_settings
# change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.0-Q16-HDRI\\magick.exe"})

_ACTIONS: dict[str, Action] = {
    "Обрезать": Crop(),
    "Соединить несколько видео": Concatenate(),
    "Изменить скорость": ChangeSpeed(),
    "Убрать звук": RemoveAudio(),
    "Повернуть": Rotate(),
    "Добавить изображение": AddImage()
}


class ImageCanvas:
    def __init__(self, root: tk.Tk):
        self.canvas = tk.Canvas(root)
        self.imgtk: ImageTk.PhotoImage
        self.image_container = None


class VideoEditorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Видеоредактор")
        self.root.attributes('-fullscreen', True)
        self.WIDTH = self.root.winfo_screenwidth()
        self.HEIGHT = self.root.winfo_screenheight()
        self.WIDGET_WIDTH = int(self.WIDTH * 0.45)

        self.start_processing_button: tk.Button = None
        self.start_slider: tk.Scale = None
        self.end_slider: tk.Scale = None
        self.start_image_canvas: ImageCanvas = None
        self.end_image_canvas: ImageCanvas = None
        self.option_menu: tk.OptionMenu = None
        self.extra_slider: tk.Scale = None
        self.loaded_files_label: tk.Label = None
        self.progress_bar: ttk.Progressbar = None
        self.menubar: tk.Menu = None
        self.choose_image_button: tk.Button = None

        self.disablable_widgets = []

        self.actions = _ACTIONS
        self.chosen_action = tk.StringVar(self.root, list(self.actions.keys())[0])

        self.imported_files: list[File] = []
        self.chosen_image_destination: str = None

        self.create_image_canvases()
        self.create_loaded_files_label()
        self.create_menubar()
        self.create_sliders()
        self.create_processing_button()
        self.create_progressbar()

        self.root.mainloop()

    def create_image_canvases(self):
        img = Image.open('usage.png')
        img.thumbnail((self.WIDGET_WIDTH, self.WIDGET_WIDTH))

        self.start_image_canvas = ImageCanvas(self.root)
        self.start_image_canvas.imgtk = ImageTk.PhotoImage(img)
        self.start_image_canvas.image_container = self.start_image_canvas.canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.start_image_canvas.imgtk
        )
        self.start_image_canvas.canvas.place(x=20, y=self.HEIGHT * 0.3, width=self.WIDTH * 0.45, height=self.HEIGHT)

        self.end_image_canvas = ImageCanvas(self.root)
        self.end_image_canvas.imgtk = ImageTk.PhotoImage(img)
        self.end_image_canvas.image_container = self.end_image_canvas.canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.end_image_canvas.imgtk
        )
        self.end_image_canvas.canvas.place(x=self.WIDTH * 0.5, y=self.HEIGHT * 0.3, width=self.WIDTH * 0.45,
                                           height=self.HEIGHT)

    def create_loaded_files_label(self):
        self.loaded_files_label = tk.Label(justify=tk.LEFT)
        self.loaded_files_label.place(x=10, y=0)
        self.update_loaded_files_label()

    def create_progressbar(self):
        self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, mode='indeterminate')

    def create_options(self):
        self.option_menu = tk.OptionMenu(self.root, self.chosen_action, *self.actions.keys(),
                                         command=self.option_changed)
        self.option_menu.place(x=self.WIDTH / 2, y=20)
        self.disablable_widgets.append(self.option_menu)

    def option_changed(self, value):
        action = self.actions[value]

        if isinstance(action, INeedExtraSlider):
            self.create_extra_slider(action.extra_slider_start(), action.extra_slider_end())
            return

        if isinstance(action, VideoBoundsForSlider) and isinstance(action, INeedImage):
            clip = self.imported_files[0].clip
            self.create_extra_slider(clip.start, clip.end)
            self.create_choose_image_button()

            return

        if self.extra_slider is not None:
            self.extra_slider.place_forget()

        if self.choose_image_button is not None:
            self.choose_image_button.place_forget()

    def create_choose_image_button(self):
        self.choose_image_button = tk.Button(self.root, text="Выбрать", command=self.choose_image)
        self.choose_image_button.place(x=self.WIDTH / 2, y=120)

    def choose_image(self):
        path = filedialog.askopenfilename(filetypes=[("JPEG Файл", '.jpeg')])
        self.chosen_image_destination = path

    def create_extra_slider(self, from_: float, to: float):
        self.extra_slider = tk.Scale(self.root, from_=from_, to=to, resolution=0.1, orient=tk.HORIZONTAL)
        self.extra_slider.place(x=self.WIDTH / 2, y=60)
        self.disablable_widgets.append(self.extra_slider)

    def create_processing_button(self):
        self.start_processing_button = tk.Button(self.root, text="Начать обработку", state=tk.DISABLED,
                                                 command=self.start_processing_pressed)
        self.start_processing_button.place(x=self.WIDTH - 150, y=20)
        self.disablable_widgets.append(self.start_processing_button)

    def create_menubar(self):
        self.menubar = tk.Menu(self.root)

        self.menubar.add_command(label="Загрузить файл", command=self.select_file)
        self.menubar.add_command(label="Выйти", command=self.root.quit)

        self.root.config(menu=self.menubar)

    def create_sliders(self):
        self.start_slider = tk.Scale(self.root, from_=0.1, to=1, resolution=0.05, state=tk.DISABLED, orient=tk.HORIZONTAL,
                                     command=self.start_slider_change)
        self.end_slider = tk.Scale(self.root, from_=0, to=1, resolution=0.05, state=tk.DISABLED, orient=tk.HORIZONTAL,
                                   command=self.end_slider_change)

        y = self.HEIGHT * 0.9

        self.start_slider.place(x=20, y=y, width=self.WIDGET_WIDTH)
        self.end_slider.place(x=self.WIDTH / 2, y=y, width=self.WIDGET_WIDTH)

        self.disablable_widgets += [self.start_slider, self.end_slider]

    def start_slider_change(self, value: str):
        self.end_slider.configure(from_=float(value))
        self.slider_changed(float(value), self.start_image_canvas)

    def end_slider_change(self, value: str):
        self.slider_changed(float(value), self.end_image_canvas)

    def slider_changed(self, value: float, image_canvas: ImageCanvas):
        img = self.get_image_from_seconds(value)
        img.thumbnail((self.WIDGET_WIDTH, self.WIDGET_WIDTH))
        image_canvas.imgtk = ImageTk.PhotoImage(img)
        image_canvas.canvas.itemconfig(image_canvas.image_container, image=image_canvas.imgtk)

    def start_processing_pressed(self):
        action = self.actions[self.chosen_action.get()]
        if isinstance(action, INeedImage) and self.chosen_image_destination is None:
            messagebox.showerror("Нет изображения", "Пожалуйста, выберите изображение")
            return

        save_dir = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not save_dir:
            return

        filename = self.imported_files[0].location.split('/')[-1].replace('.mp4', '')
        destination = f"{save_dir}/{filename}_{self.chosen_action.get()}_.mp4"

        self.before_processing()
        self.process_data(destination)

    def process_data(self, destination: str):
        extra_slider_value = self.extra_slider.get() if self.extra_slider is not None else 0
        params = Params(self.start_slider.get(), self.end_slider.get(), extra_slider_value,
                        self.chosen_image_destination)

        action = self.actions[self.chosen_action.get()]
        action.set_fields(self.imported_files.copy(), destination, params)
        action.start()

        self.imported_files.clear()

        self.monitor_processing_progress(action, destination)

    def before_processing(self):
        self.change_disablable_widgets_state(tk.DISABLED)

        btn = self.start_processing_button
        btn.configure(state=tk.DISABLED)
        self.progress_bar.place(x=btn.winfo_rootx(), y=btn.winfo_rooty() + 30,
                                width=self.start_processing_button.winfo_width())
        self.progress_bar.start(20)

    def on_processing_complete(self, destination: str):
        self.progress_bar.stop()
        self.progress_bar.place_forget()
        messagebox.showinfo("Завершено", "Обработка файла завершена!")

        action = self.actions[self.chosen_action.get()]
        action_type = type(action)
        self.actions[self.chosen_action.get()] = action_type()

        self.on_file_selected(destination)

        self.change_disablable_widgets_state(tk.ACTIVE)

    def monitor_processing_progress(self, thread, destination: str):
        if thread.is_alive():
            self.root.after(100, lambda: self.monitor_processing_progress(thread, destination))
        else:
            self.on_processing_complete(destination)

    def change_disablable_widgets_state(self, state=tk.constants):
        for widget in self.disablable_widgets:
            if widget is not None:
                widget.configure(state=state)

    def get_image_from_seconds(self, seconds: float) -> Image:
        frame = self.imported_files[0].clip.get_frame(seconds)
        return Image.fromarray(frame)

    def update_loaded_files_label(self):
        text = "Загруженные файлы:\n" + '\n'.join([file.location for file in self.imported_files])
        self.loaded_files_label.configure(text=text)

    def select_file(self):
        file_location = filedialog.askopenfilename(initialdir="/", title="Выберите mp4 файл",
                                                   filetypes=[("mp4", '*.mp4')])
        if not file_location:
            return

        self.on_file_selected(file_location)

    def on_file_selected(self, file_location: str):
        self.imported_files.append(File(file_location))
        self.update_loaded_files_label()
        self.create_options()

        self.start_processing_button.configure(state=tk.ACTIVE)

        clip = self.imported_files[0].clip
        self.start_slider.configure(from_=0, to=clip.end, state=tk.ACTIVE)
        self.end_slider.configure(to=clip.end, state=tk.ACTIVE)

        self.start_slider.set(clip.start)
        self.end_slider.set(clip.end)


if __name__ == '__main__':
    if platform.system() == "Windows":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    VideoEditorGUI()
