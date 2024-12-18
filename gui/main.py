import customtkinter as ctk
import tkinter as tk
import requests
import svgwrite
import base64
import io
import cairosvg
from PIL import Image, ImageTk
from owlready2 import *
import os


class GeometricAreaCalculator:
    def __init__(self):
        # configure the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # create main window
        self.root = ctk.CTk()
        self.root.title("ITS - Geometric Area Calculator")
        self.setup_window()
        self.create_layout()
        onto_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), "ontology", "ontology.owl")

        try:
            self.onto = get_ontology(onto_path).load()
            print("Ontology loaded successfully in GUI:", self.onto)
        except Exception as e:
            print(f"Error loading ontology in GUI: {e}")
            self.onto = None

        # Initialize entries as an empty dictionary
        self.entries = {}

        # # Initialize ontology_label here
        # self.ontology_label = ctk.CTkLabel(
        #     self.right_frame, text="", justify=tk.LEFT)
        # self.ontology_label.pack(pady=(10, 0), padx=10, anchor="nw")

        # Initialize ontology_label here with text wrapping
        self.ontology_label = ctk.CTkLabel(
            self.right_frame,
            text="",
            justify=tk.LEFT,
            wraplength=250  # Adjust this value as needed
        )

        # Configure grid row to expand
        # Assuming ontology_label is in about the 5th row (adjust index if necessary)
        self.right_frame.grid_rowconfigure(5, weight=1)
        # onto info row, and change sticky from "nw" to "nsew"
        self.ontology_label.grid(
            row=5, column=0, pady=(10, 0), padx=10, sticky="nw")

    def setup_window(self):
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(700, 500)

    def create_layout(self):
        # main container frame
        self.main_container = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_container.pack(padx=20, pady=20, fill="both", expand=True)

        # split into two columns
        self.left_frame = ctk.CTkFrame(
            self.main_container, fg_color="transparent")
        self.left_frame.pack(side="left", padx=10, pady=10,
                             fill="both", expand=True)

        self.right_frame = ctk.CTkFrame(
            self.main_container, fg_color="transparent", width=300)
        self.right_frame.pack(side="right", padx=10, pady=10, fill="y")

        # title
        title_label = ctk.CTkLabel(
            self.left_frame,
            # text="geometric area calculator",
            text="",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(20, 10))

        # shape selection frame
        shape_selection_frame = ctk.CTkFrame(
            self.left_frame, fg_color="transparent")
        shape_selection_frame.pack(pady=10, padx=20, fill="x")

        # shape dropdown
        shape_label = ctk.CTkLabel(
            shape_selection_frame,
            text="Select Shape:",
            font=("Arial", 16)
        )
        shape_label.pack(side="left", padx=(0, 10))

        self.shape_var = ctk.StringVar(value="Select a Shape")
        self.shape_dropdown = ctk.CTkOptionMenu(
            shape_selection_frame,
            values=["Square", "Circle", "Rectangle", "Triangle"],
            command=self.show_shape_inputs,
            width=200
        )
        self.shape_dropdown.pack(side="left")

        # dynamic input frame
        self.input_frame = ctk.CTkFrame(
            self.left_frame, fg_color="transparent")
        self.input_frame.pack(pady=10, padx=20, fill="x")

        # result label
        self.result_label = ctk.CTkLabel(
            self.left_frame,
            text="",
            font=("Arial", 18)
        )
        self.result_label.pack(pady=10)

        # calculate button
        self.calculate_btn = ctk.CTkButton(
            self.left_frame,
            text="Calculate Area",
            command=self.calculate_area,
            font=("Arial", 16)
        )
        self.calculate_btn.pack(pady=10)

        # # shape visualization frame (in right frame)
        # self.shape_image_label = ctk.CTkLabel(
        #     self.right_frame,
        #     # text="shape visualization",
        #     text="",
        #     font=("Arial", 24, "bold")
        # )
        # self.shape_image_label.pack(pady=(20, 10))

        # # svg display
        # self.svg_label = ctk.CTkLabel(
        #     self.right_frame,
        #     text="",
        #     width=250,
        #     height=250
        # )
        # self.svg_label.pack(pady=10)

        # shape visualization frame (in right frame)
        self.shape_image_label = ctk.CTkLabel(
            self.right_frame,
            text="",
            font=("Arial", 24, "bold")
        )
        self.shape_image_label.grid(
            row=0, column=0, pady=(20, 10), sticky="ew")

        # svg display
        self.svg_label = ctk.CTkLabel(
            self.right_frame,
            text="",
            width=250,
            height=250
        )
        self.svg_label.grid(row=1, column=0, pady=10, sticky="ew")

        # Configure right_frame's grid weights
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)  # Title row
        self.right_frame.grid_rowconfigure(1, weight=0)  # SVG row
        self.right_frame.grid_rowconfigure(2, weight=0)
        self.right_frame.grid_rowconfigure(3, weight=0)
        self.right_frame.grid_rowconfigure(4, weight=0)
        # Ontology label row (make this one expandable)
        self.right_frame.grid_rowconfigure(5, weight=1)

    def generate_shape_svg(self, shape, dimensions):
        # create svg drawing
        dwg = svgwrite.Drawing(size=(250, 250))

        # add white background
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))

        # common styling
        stroke_width = 2
        font_size = 12

        if shape == "Square":
            side = dimensions.get('side', 50)
            # scale the shape to fit within the image
            scale = min(200 / side, 1)
            rect_size = side * scale
            x1 = (250 - rect_size) / 2
            y1 = (250 - rect_size) / 2

            # draw the square
            dwg.add(dwg.rect(
                insert=(x1, y1),
                size=(rect_size, rect_size),
                fill='none',
                stroke='blue',
                stroke_width=stroke_width
            ))

            # add dimension text
            dwg.add(dwg.text(
                f"Side: {side}",
                insert=(10, 20),
                fill='black',
                font_size=font_size
            ))

        elif shape == "Circle":
            radius = dimensions.get('radius', 50)
            # scale the shape to fit within the image
            scale = min(200 / (2 * radius), 1)
            scaled_radius = radius * scale

            # draw the circle
            dwg.add(dwg.circle(
                center=(125, 125),
                r=scaled_radius,
                fill='none',
                stroke='green',
                stroke_width=stroke_width
            ))

            # add dimension text
            dwg.add(dwg.text(
                f"Radius: {radius}",
                insert=(10, 20),
                fill='black',
                font_size=font_size
            ))

        elif shape == "Rectangle":
            length = dimensions.get('length', 100)
            width = dimensions.get('width', 50)

            # scale the shape to fit within the image
            scale = min(200 / max(length, width), 1)
            scaled_length = length * scale
            scaled_width = width * scale

            # calculate position to center the rectangle
            x1 = (250 - scaled_length) / 2
            y1 = (250 - scaled_width) / 2

            # draw the rectangle
            dwg.add(dwg.rect(
                insert=(x1, y1),
                size=(scaled_length, scaled_width),
                fill='none',
                stroke='orange',
                stroke_width=stroke_width
            ))

            # add dimension text
            dwg.add(dwg.text(
                f"Length: {length}",
                insert=(10, 20),
                fill='black',
                font_size=font_size
            ))
            dwg.add(dwg.text(
                f"Width: {width}",
                insert=(10, 35),
                fill='black',
                font_size=font_size
            ))

        elif shape == "Triangle":
            base = dimensions.get('base', 100)
            height = dimensions.get('height', 50)

            # scale the shape to fit within the image
            scale = min(200 / max(base, height), 1)
            scaled_base = base * scale
            scaled_height = height * scale

            # calculate triangle points
            points = [
                (125, 50),  # top
                (125 - scaled_base/2, 250 - 50),  # bottom left
                (125 + scaled_base/2, 250 - 50)   # bottom right
            ]

            # draw the triangle
            dwg.add(dwg.polygon(
                points=points,
                fill='none',
                stroke='red',
                stroke_width=stroke_width
            ))

            # add dimension text
            dwg.add(dwg.text(
                f"Base: {base}",
                insert=(10, 20),
                fill='black',
                font_size=font_size
            ))
            dwg.add(dwg.text(
                f"Height: {height}",
                insert=(10, 35),
                fill='black',
                font_size=font_size
            ))

        # save svg to string
        svg_string = dwg.tostring()

        # convert svg to png using cairosvg
        png_data = cairosvg.svg2png(bytestring=svg_string)

        # create pil image
        pil_image = Image.open(io.BytesIO(png_data))

        # resize image if needed
        pil_image = pil_image.resize((250, 250), Image.LANCZOS)

        # convert to tkinter-compatible image
        tk_image = ImageTk.PhotoImage(pil_image)

        # update the label with the image
        self.svg_label.configure(image=tk_image)
        self.svg_label.image = tk_image  # keep a reference

    def show_shape_inputs(self, shape=None):
        # clear previous inputs
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        shape = self.shape_dropdown.get()
        self.entries = {}  # reset the entries dictionary

        shapes_inputs = {
            "Square": [("Side", "side")],
            "Circle": [("Radius", "radius")],
            "Rectangle": [("Length", "length"), ("Width", "width")],
            "Triangle": [("Base", "base"), ("Height", "height")]
        }

        if shape in shapes_inputs:
            for i, (label_text, entry_name) in enumerate(shapes_inputs[shape]):
                # create a frame for each input to align properly
                input_row = ctk.CTkFrame(
                    self.input_frame, fg_color="transparent")
                input_row.pack(pady=5, fill="x")

                label = ctk.CTkLabel(
                    input_row,
                    text=f"{label_text}:",
                    font=("Arial", 16),
                    width=100,
                    anchor="w"
                )
                label.pack(side="left", padx=(0, 10))

                entry = ctk.CTkEntry(
                    input_row,
                    width=200,
                    font=("Arial", 16)
                )
                entry.pack(side="left")
                entry.param_name = entry_name
                # store entry by parameter name
                self.entries[entry_name] = entry

    def calculate_area(self):
        shape = self.shape_dropdown.get()
        if shape == "Select a Shape":
            self.result_label.configure(
                text="Please select a shape", text_color="red")
            return

        try:
            dimensions = {}
            for entry_name, entry in self.entries.items():
                value = float(entry.get())
                dimensions[entry_name] = value

            # generate shape visualization
            self.generate_shape_svg(shape, dimensions)

            response = requests.get(
                f"http://127.0.0.1:8000/calculate_area/",
                params={"shape_name": shape, **dimensions}
            )
            response.raise_for_status()

            # Display the formula and area
            data = response.json()
            self.result_label.configure(
                text=f"Formula: {data['formula']}\nArea: {data['area']:.2f}",
                text_color="white",
                justify=tk.LEFT
            )

            # Display ontology information
            if self.onto:
                shape_iri = next(
                    (c.iri for c in self.onto.classes() if c.name == shape), None)
                if shape_iri:
                    ontology_info = f"Ontology Class: {shape_iri}\n"
                    individual = self.onto.search_one(iri=f"*{shape}_1")
                    if individual:
                        for prop in individual.get_properties():
                            for value in prop[individual]:
                                ontology_info += f"{prop.name}: {value}\n"
                    self.ontology_label.configure(text=ontology_info)
                else:
                    self.ontology_label.configure(
                        text="Ontology information not found for this shape.")
            else:
                self.ontology_label.configure(text="Ontology not loaded.")

        except ValueError:
            self.result_label.configure(
                text="Please enter valid numeric values",
                text_color="red"
            )
        except requests.exceptions.RequestException as e:
            self.result_label.configure(
                text=f"Network Error: {str(e)}",
                text_color="red"
            )

    def run(self):
        self.root.mainloop()


def main():
    app = GeometricAreaCalculator()
    app.run()


if __name__ == "__main__":
    main()
