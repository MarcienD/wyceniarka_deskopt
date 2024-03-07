import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import ezdxf
from math import sqrt, pi

def analyze_dxf(file_path, material, thickness, require_material):
    # Otwieranie pliku DXF i przetwarzanie geometrii
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    liczba_geometrii = 0
    obwod_geometrii = 0.0
    max_area = 0

    # Analiza każdej geometrii w pliku DXF
    for entity in msp.query('*'):
        if entity.dxftype() in ['LINE', 'CIRCLE', 'ARC']:
            # Obliczanie obwodu dla lini, okręgów i łuków
            liczba_geometrii += 1
            if entity.dxftype() == 'CIRCLE':
                area = calculate_area(entity)
                max_area = max(max_area, area)
                obwod_geometrii += 2 * pi * entity.dxf.radius
            else:
                obwod_geometrii += entity.length
        elif entity.dxftype() in ['LWPOLYLINE', 'SPLINE']:
            # Obliczanie długości dla wieloboków i krzywych
            liczba_geometrii += 1
            obwod_geometrii += calculate_lwpolyline_length(entity)
            if require_material:
                area = calculate_area(entity)
                max_area = max(max_area, area)

    # Tworzenie okna wynikowego z analizą
    result_window = tk.Toplevel()
    result_window.title("Wyniki analizy pliku DXF")

    # Wyświetlanie wyników analizy w oknie
    tk.Label(result_window, text=f"Rodzaj materiału: {material}").pack(pady=5)
    tk.Label(result_window, text=f"Grubość materiału: {thickness}").pack(pady=5)
    tk.Label(result_window, text=f"Liczba geometrii: {liczba_geometrii}").pack(pady=5) # Co 100 geometrii - cykl czyszczenia dyszy
    tk.Label(result_window, text=f"Suma obwodów geometrii: {round(obwod_geometrii, 1)}").pack(pady=5)
    if require_material:
        tk.Label(result_window, text=f"Powierzchnia: {round(max_area, 1)}").pack(pady=5)

def calculate_lwpolyline_length(lwpolyline):
    # Obliczanie długości wieloboku
    length = 0.0
    points = lwpolyline.get_points()
    for i in range(len(points) - 1):
        x1, y1 = points[i][:2]
        x2, y2 = points[i + 1][:2]
        segment_length = sqrt((x2 - x1)**2 + (y2 - y1)**2)
        length += round(segment_length, 1)
    # Dodawanie długości ostatniego segmentu, jeśli wielobok jest zamknięty ( problem z kwadratem )
    if lwpolyline.closed:
        x1, y1 = points[-1][:2]
        x2, y2 = points[0][:2]
        segment_length = sqrt((x2 - x1)**2 + (y2 - y1)**2)
        length += round(segment_length, 1)
    return length

def calculate_area(entity):
    # Obliczanie powierzchni dla okręgów i wieloboków
    if entity.dxftype() == 'CIRCLE':
        area = pi * entity.dxf.radius**2
        return area
    elif entity.dxftype() == 'LWPOLYLINE':
        if hasattr(entity, 'get_points'):
            points = entity.get_points()
            area = 0.0
            for i in range(len(points) - 1):
                x1, y1 = points[i][:2]
                x2, y2 = points[i + 1][:2]
                area += (x2 - x1) * (y1 + y2) / 2.0
            return abs(area)
        else:
            return "Cos poszlo nie tak"
    elif entity.dxftype() == 'SPLINE':
        return "spline"
    else:
        return "Nieznany ksztalt"

def update_thickness_options(*args):
    # Aktualizacja opcji dla grubości materiału
    material = material_combobox.get()
    thickness_combobox['values'] = thickness_options[material]
    thickness_combobox.set(thickness_options[material][0])

def choose_file():
    # Wybór pliku DXF
    material = material_combobox.get()
    thickness = thickness_combobox.get()
    require_material = require_material_checkbox_var.get()
    file_path = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])
    if file_path:
        analyze_dxf(file_path, material, thickness, require_material)

def save_thickness():
    # Zapisanie wybranej grubości
    thickness = thickness_combobox.get()
    return thickness

def close_program():
    # Zamknięcie programu
    root.destroy()

# Tworzenie głównego okna
root = tk.Tk()
root.title("Analiza pliku DXF")

# Tworzenie checkboxa do wyboru wymagania materiału
require_material_checkbox_var = tk.BooleanVar()
require_material_checkbox = tk.Checkbutton(root, text="Potrzebuję materiału", variable=require_material_checkbox_var)
require_material_checkbox.pack(pady=10)

# Tworzenie opcji wyboru materiału i grubości
material_options = ["stal ocynkowana", "stal nierdzewna", "stal czarna"]
thickness_options = {
    "stal ocynkowana": ["0.5mm", "1mm", "3mm"],
    "stal nierdzewna": ["1mm", "1.5mm", "2mm", "3mm", "4mm", "5mm", "6mm", "8mm"],
    "stal czarna": ["1mm", "1.5mm", "2mm", "3mm", "4mm", "5mm", "6mm", "8mm", "10mm"]
}

# Tworzenie Comboboxa do wyboru materiału
material_label = tk.Label(root, text="Rodzaj materiału:")
material_combobox = ttk.Combobox(root, values=material_options)
material_combobox.set(material_options[0])
material_combobox.pack(pady=10)
material_label.pack(pady=10)
material_combobox.bind('<<ComboboxSelected>>', update_thickness_options)

# Tworzenie Comboboxa do wyboru grubości materiału
thickness_label = tk.Label(root, text="Grubość materiału:")
thickness_combobox = ttk.Combobox(root, values=thickness_options[material_options[0]])
thickness_combobox.set(thickness_options[material_options[0]][0])
thickness_combobox.pack(pady=10)
thickness_label.pack(pady=10)

# Tworzenie przycisku do analizy pliku DXF
button_analyze = tk.Button(root, text="Analizuj plik DXF", command=choose_file)
button_analyze.pack(pady=20)

# Tworzenie przycisku do zakończenia programu
button_exit = tk.Button(root, text="Zakończ", command=close_program)
button_exit.pack(pady=20)

# Uruchamianie głównego okna
root.mainloop()