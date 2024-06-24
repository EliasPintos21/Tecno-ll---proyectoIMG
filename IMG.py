import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import cv2
from PIL import Image, ImageTk
import numpy as np
import os

# Clase principal del programa
class ImageApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Editor de Imágenes")
        
        self.root.configure(bg="sea green")
        self.original_image = None
        self.modified_image = None
        self.image_path = None
        self.current_rotation = 0  # Variable para mantener el ángulo actual de rotación
        
        # Coordenadas de inicio y fin para el recorte
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        
        # Variable para mantener la proporción al cambiar el tamaño
        self.keep_aspect_ratio = tk.BooleanVar()
        self.keep_aspect_ratio.set(True)  # Por defecto, mantener la proporción
        
        # Configuración de la interfaz
        self.setup_ui()
    
    def setup_ui(self):
        # Botones para cargar imagen, deshacer cambios
        self.load_button = tk.Button(self.root, text="Cargar Imagen", command=self.load_image, bg="light blue")
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.undo_button = tk.Button(self.root, text="Deshacer Cambios", command=self.undo_changes, bg="light blue")
        self.undo_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Labels y entradas para los valores de traslación
        self.tx_label = tk.Label(self.root, text="Traslación en X:")
        self.tx_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.tx_entry = tk.Entry(self.root)
        self.tx_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.ty_label = tk.Label(self.root, text="Traslación en Y:")
        self.ty_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.ty_entry = tk.Entry(self.root)
        self.ty_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.translate_button = tk.Button(self.root, text="Aplicar Traslación", command=self.apply_translation, bg="light blue")
        self.translate_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Labels y entradas para los valores de redimensionamiento
        self.width_label = tk.Label(self.root, text="Nuevo Ancho:")
        self.width_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.width_entry = tk.Entry(self.root)
        self.width_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.height_label = tk.Label(self.root, text="Nueva Altura:")
        self.height_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.height_entry = tk.Entry(self.root)
        self.height_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Checkbutton para mantener la proporción
        self.keep_ratio_checkbutton = tk.Checkbutton(self.root, text="Mantener Proporción", variable=self.keep_aspect_ratio)
        self.keep_ratio_checkbutton.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        self.resize_button = tk.Button(self.root, text="Cambiar Tamaño", command=self.apply_resize, bg="light blue")
        self.resize_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Label y entrada para el ángulo de rotación
        self.rotate_label = tk.Label(self.root, text="Ángulo de Rotación:")
        self.rotate_label.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
        self.rotate_entry = tk.Entry(self.root)
        self.rotate_entry.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.rotate_button = tk.Button(self.root, text="Aplicar Rotación", command=self.apply_rotation, bg="light blue")
        self.rotate_button.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Botones para espejar horizontal y verticalmente
        self.mirror_horizontal_button = tk.Button(self.root, text="Espejar Horizontalmente", command=self.mirror_horizontal, bg="light blue")
        self.mirror_horizontal_button.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        self.mirror_vertical_button = tk.Button(self.root, text="Espejar Verticalmente", command=self.mirror_vertical, bg="light blue")
        self.mirror_vertical_button.grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Botón para recortar imagen
        self.crop_button = tk.Button(self.root, text="Recortar Imagen", command=self.start_crop, bg="light blue")
        self.crop_button.grid(row=12, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Botón para guardar imagen modificada
        self.save_button = tk.Button(self.root, text="Guardar Cambios", command=self.save_image, bg="light blue")
        self.save_button.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Canvas para mostrar las imágenes
        self.canvas_original = tk.Canvas(self.root, bg="gray")
        self.canvas_original.grid(row=0, column=2, rowspan=12, padx=10, pady=10, sticky=tk.E+tk.W+tk.N+tk.S)

        self.canvas_modified = tk.Canvas(self.root, bg="gray")
        self.canvas_modified.grid(row=0, column=3, rowspan=12, padx=10, pady=10, sticky=tk.E+tk.W+tk.N+tk.S)
        
        # Labels para mostrar los detalles de la imagen
        self.details_label = tk.Label(self.root, text="Detalles de la Imagen:")
        self.details_label.grid(row=14, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        self.details_text = tk.Text(self.root, height=5, width=50)
        self.details_text.grid(row=15, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        self.details_text.config(state=tk.DISABLED)
        
        # Eventos de ratón para el canvas original
        self.canvas_original.bind("<ButtonPress-1>", self.on_crop_start)
        self.canvas_original.bind("<B1-Motion>", self.on_crop_drag)
        self.canvas_original.bind("<ButtonRelease-1>", self.on_crop_end)

    def load_image(self):
        # Función para cargar la imagen
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            self.modified_image = self.original_image.copy()
            self.show_image(self.original_image, self.canvas_original)
            self.show_image(self.modified_image, self.canvas_modified)
            self.show_image_details(file_path, self.original_image)
    
    def show_image(self, img, canvas):
        # Ajustar el tamaño del canvas según la imagen
        h, w = img.shape[:2]
        canvas.config(width=w, height=h)
        
        # Función para mostrar la imagen en el canvas
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk
    
    def show_image_details(self, file_path, img):
        # Función para mostrar los detalles de la imagen
        height, width, channels = img.shape
        size = os.path.getsize(file_path)
        
        details = f"Alto: {height} px\n"
        details += f"Ancho: {width} px\n"
        details += f"Canales: {channels}\n"
        details += f"Tamaño en disco: {size / 1024:.2f} KB"
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, details)
        self.details_text.config(state=tk.DISABLED)
    
    def apply_translation(self):
        # Función para aplicar la traslación a la imagen
        try:
            tx = int(self.tx_entry.get())
            ty = -int(self.ty_entry.get())  # Invertir la dirección de traslación en Y
            rows, cols = self.original_image.shape[:2]
            M = np.float32([[1, 0, tx], [0, 1, ty]])
            self.modified_image = cv2.warpAffine(self.original_image, M, (cols, rows))
            self.show_image(self.modified_image, self.canvas_modified)
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos para la traslación.")

    
    def apply_resize(self):
        # Función para cambiar el tamaño de la imagen
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())
            if self.keep_aspect_ratio.get():
                # Redimensionar manteniendo la proporción
                width_ratio = new_width / self.original_image.shape[1]
                height_ratio = new_height / self.original_image.shape[0]
                scale_ratio = min(width_ratio, height_ratio)
                new_width = int(self.original_image.shape[1] * scale_ratio)
                new_height = int(self.original_image.shape[0] * scale_ratio)
                
            self.modified_image = cv2.resize(self.original_image, (new_width, new_height))
            self.show_image(self.modified_image, self.canvas_modified)
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos para el redimensionamiento.")
    
    def apply_rotation(self):
        # Función para aplicar la rotación a la imagen
        try:
            angle = float(self.rotate_entry.get())
            rows, cols = self.original_image.shape[:2]
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
            self.modified_image = cv2.warpAffine(self.original_image, M, (cols, rows))
            self.show_image(self.modified_image, self.canvas_modified)
            self.current_rotation = angle
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un ángulo válido para la rotación.")
    
    def mirror_horizontal(self):
        # Función para espejar horizontalmente la imagen
        if self.original_image is not None:
            self.modified_image = cv2.flip(self.modified_image, 1)
            self.show_image(self.modified_image, self.canvas_modified)
    
    def mirror_vertical(self):
        # Función para espejar verticalmente la imagen
        if self.original_image is not None:
            self.modified_image = cv2.flip(self.modified_image, 0)
            self.show_image(self.modified_image, self.canvas_modified)
    
    def start_crop(self):
        # Función para iniciar el recorte de la imagen
        if self.original_image is not None:
            self.canvas_original.bind("<ButtonPress-1>", self.on_crop_start)
            self.canvas_original.bind("<B1-Motion>", self.on_crop_drag)
            self.canvas_original.bind("<ButtonRelease-1>", self.on_crop_end)
            messagebox.showinfo("Recorte", "Seleccione la región a recortar con el mouse.")
    
    def on_crop_start(self, event):
        # Función para iniciar el recorte de la imagen
        self.crop_start_x = event.x
        self.crop_start_y = event.y
    
    def on_crop_drag(self, event):
        # Función para actualizar la vista previa del recorte mientras se arrastra el mouse
        if self.crop_start_x is not None and self.crop_start_y is not None:
            self.crop_end_x = event.x
            self.crop_end_y = event.y
            
            # Mostrar el área de recorte seleccionada en el canvas original
            self.show_image(self.original_image, self.canvas_original)
            self.canvas_original.create_rectangle(self.crop_start_x, self.crop_start_y, 
                                                  self.crop_end_x, self.crop_end_y, 
                                                  outline="red", width=2)
    
    def on_crop_end(self, event):
        # Función para aplicar el recorte cuando se suelta el botón del mouse
        if self.crop_start_x is not None and self.crop_start_y is not None and \
           self.crop_end_x is not None and self.crop_end_y is not None:
            
            # Asegurarse de que las coordenadas estén en el orden correcto
            x1 = min(self.crop_start_x, self.crop_end_x)
            y1 = min(self.crop_start_y, self.crop_end_y)
            x2 = max(self.crop_start_x, self.crop_end_x)
            y2 = max(self.crop_start_y, self.crop_end_y)
            
            # Recortar la imagen original
            self.modified_image = self.original_image[y1:y2, x1:x2]
            
            # Mostrar la imagen recortada en una nueva ventana
            self.show_cropped_image()
            
            # Reiniciar las coordenadas de recorte
            self.crop_start_x = None
            self.crop_start_y = None
            self.crop_end_x = None
            self.crop_end_y = None
            
            # Mostrar la imagen recortada en el canvas de vista previa
            self.show_image(self.modified_image, self.canvas_modified)
    
    def show_cropped_image(self):
        # Función para mostrar la imagen recortada en una nueva ventana
        if self.modified_image is not None:
            top = Toplevel()
            top.title("Imagen Recortada")
            cropped_canvas = tk.Canvas(top, bg="gray")
            cropped_canvas.pack()
            
            # Mostrar la imagen recortada en la nueva ventana
            self.show_image(self.modified_image, cropped_canvas)
    
    def undo_changes(self):
        # Función para deshacer los cambios
        if self.original_image is not None:
            self.modified_image = self.original_image.copy()
            self.show_image(self.modified_image, self.canvas_modified)
    
    def save_image(self):
        # Función para guardar la imagen modificada
        if self.modified_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                try:
                    cv2.imwrite(file_path, self.modified_image)
                    messagebox.showinfo("Guardar", "La imagen se ha guardado correctamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar la imagen: {str(e)}")

# Ejecución de la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()

