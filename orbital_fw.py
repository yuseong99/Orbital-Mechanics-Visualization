import vtk
import numpy as np
import math
from datetime import datetime, timedelta
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox, QTextEdit, QGroupBox, QFormLayout, QDoubleSpinBox, QCheckBox, QGridLayout
from PyQt5.QtCore import Qt, QDate, QTimer
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import sys

class SolarSystemApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.AU = 149.6e9  # in meters
        self.G = 6.67430e-11  # Gravitational constant
        self.G_multiplier = 1.0
        self.ecc_multiplier = 1.0
        self.inc_multiplier = 1.0
        self.scale_factor = 1e10
        self.sun_mass_scale = 1.0
        self.bodies = {}
        
        # Store original orbit
        self.original_orbital_elements = {}
        self.current_date = datetime.now()
        self.day_number = self.calculate_day_number(self.current_date)
        

        self.selected_planet = "Sun"
        
        # 
        self.setup_ui()
        self.setup_time_controls()
        self.setup_vtk()
        
        self.initialize_planets()
        self.update_orbital_elements()
        self.store_original_orbital_elements()
        self.calculate_planet_positions()
        self.create_orbit_paths()
        self.add_labels()
        #self.add_gravity_field_glyphs()
        self.vtk_widget.GetRenderWindow().Render()
    
    def setup_ui(self):
      self.setWindowTitle("Solar System_Yuseong_Choi")
      self.central = QWidget()
      self.setCentralWidget(self.central)
      

      main_layout = QHBoxLayout(self.central)
      left_panel = QWidget()
      self.layout = QVBoxLayout(left_panel)
      
      self.date_label = QLabel()
      self.layout.addWidget(self.date_label)
      
      # Time 
      self.slider = QSlider(Qt.Horizontal)
      today_days = self.compute_initial_days()
      self.slider.setMinimum(today_days)
      self.slider.setMaximum(today_days + 10000)
      self.slider.setValue(today_days)
      self.slider.valueChanged.connect(self.on_slider_change)
      self.layout.addWidget(self.slider)
      
 
      physics_box = QGroupBox("Physics Parameters")
      physics_layout = QGridLayout()
      physics_layout.setHorizontalSpacing(15)
      
      # first col
      physics_layout.addWidget(QLabel("Sun Mass:"), 0, 0)
      physics_layout.addWidget(QLabel("G Multiplier:"), 1, 0)
      
      # First row of controls (second column)
      self.mass_spin = QDoubleSpinBox()
      self.mass_spin.setRange(0.1, 3.0)
      self.mass_spin.setValue(1.0)  # Default 100% of current mass
      self.mass_spin.setSingleStep(0.05)
      self.mass_spin.setDecimals(2)
      self.mass_spin.setSuffix("x")
      self.mass_spin.valueChanged.connect(self.on_sun_mass_change_spin)
      physics_layout.addWidget(self.mass_spin, 0, 1)
      
      self.g_spin = QDoubleSpinBox()
      self.g_spin.setRange(0.1, 5.0)
      self.g_spin.setValue(1.0)
      self.g_spin.setSingleStep(0.1)
      self.g_spin.setDecimals(2)
      self.g_spin.setSuffix("x")
      self.g_spin.valueChanged.connect(self.on_physics_change)
      physics_layout.addWidget(self.g_spin, 1, 1)
      
      # third col
      physics_layout.addWidget(QLabel("Eccentricity:"), 0, 2)
      physics_layout.addWidget(QLabel("Inclination:"), 1, 2)
      
      # Second row
      self.ecc_spin = QDoubleSpinBox()
      self.ecc_spin.setRange(0.1, 5.0)
      self.ecc_spin.setValue(1.0)
      self.ecc_spin.setSingleStep(0.1)
      self.ecc_spin.setDecimals(2)
      self.ecc_spin.setSuffix("x")
      self.ecc_spin.valueChanged.connect(self.on_physics_change)
      physics_layout.addWidget(self.ecc_spin, 0, 3)
      
      self.inc_spin = QDoubleSpinBox()
      self.inc_spin.setRange(0.0, 5.0)
      self.inc_spin.setValue(1.0)
      self.inc_spin.setSingleStep(0.1)
      self.inc_spin.setDecimals(2)
      self.inc_spin.setSuffix("x")
      self.inc_spin.valueChanged.connect(self.on_physics_change)
      physics_layout.addWidget(self.inc_spin, 1, 3)
      
      btn_layout = QHBoxLayout()
      self.apply_physics_btn = QPushButton("Apply Physics Changes")
      self.apply_physics_btn.clicked.connect(self.apply_physics_changes)
      btn_layout.addWidget(self.apply_physics_btn)
      self.reset_physics_btn = QPushButton("Reset Physics")
      self.reset_physics_btn.clicked.connect(self.reset_physics)
      btn_layout.addWidget(self.reset_physics_btn)

      physics_layout.addLayout(btn_layout, 2, 0, 1, 4)
      
      physics_box.setLayout(physics_layout)
      self.layout.addWidget(physics_box)

      display_box = QGroupBox("Display Options")
      display_layout = QGridLayout()
      display_layout.setHorizontalSpacing(15)

      display_layout.addWidget(QLabel("Visibility:"), 0, 0)
      
      # Orbit paths checkbox
      self.show_orbits_checkbox = QCheckBox("Orbital Paths")
      self.show_orbits_checkbox.setChecked(True)
      self.show_orbits_checkbox.stateChanged.connect(self.toggle_orbit_visibility)
      display_layout.addWidget(self.show_orbits_checkbox, 0, 1)
      
      # Planet labels checkbox
      self.show_labels_checkbox = QCheckBox("Planet Labels")
      self.show_labels_checkbox.setChecked(True) 
      self.show_labels_checkbox.stateChanged.connect(self.toggle_label_visibility)
      display_layout.addWidget(self.show_labels_checkbox, 0, 2)
      
      display_box.setLayout(display_layout)
      self.layout.addWidget(display_box)
      
      planet_selection_layout = QHBoxLayout()
      planet_selection_layout.addWidget(QLabel("Select Planet:"))
      self.planet_combo = QComboBox()
      planet_selection_layout.addWidget(self.planet_combo)
      self.layout.addLayout(planet_selection_layout)
      
      self.vtk_widget = QVTKRenderWindowInteractor(self.central)
      self.layout.addWidget(self.vtk_widget)
      main_layout.addWidget(left_panel, 7)
      
      self.planet_info = QTextEdit()
      self.planet_info.setReadOnly(True)
      self.planet_info.setMinimumWidth(250)
      self.planet_info.setText("Select a planet to view details")
      main_layout.addWidget(self.planet_info, 3)
      
      new_date = datetime(2000, 1, 1) + timedelta(days=today_days)
      self.date_label.setText(f"Date: {new_date:%Y-%m-%d}")
    
    def compute_initial_days(self):
        return QDate(2000, 1, 1).daysTo(QDate.currentDate())

    def on_sun_mass_change_spin(self, value):

        self.sun_mass_scale = value
        self.update_sun_size()
        self.calculate_planet_positions()

        # Rebuild orbit paths new semi‑major axes
        self.remove_orbit_paths()
        self.create_orbit_paths()

        self.vtk_widget.GetRenderWindow().Render()
    
    def update_sun_size(self):
        if "Sun" in self.bodies:
            sun = self.bodies["Sun"]
            original_scale = 3.0
            
            new_scale = original_scale * (self.sun_mass_scale ** 0.33)
            if sun['actor']:
                sun['actor'].SetScale(new_scale / original_scale)

                if 'axis_actor' in sun:
                    axis = sun['axis_actor']
                    if axis:
                        axis.SetScale(new_scale / original_scale)
    
    def on_slider_change(self, days):
        new_date = datetime(2000, 1, 1) + timedelta(days=days)
        self.date_label.setText(f"Date: {new_date:%Y-%m-%d}")
        self.current_date = new_date
        self.day_number = self.calculate_day_number(new_date)
        self.update_orbital_elements()
        self.calculate_planet_positions()
        
        if self.selected_planet and self.selected_planet != "Sun":
            self.focus_camera_on_planet(self.selected_planet)
        
        self.vtk_widget.GetRenderWindow().Render()
    
    def calculate_day_number(self, date):
        jan_2000 = datetime(2000, 1, 1)
        days = (date - jan_2000).total_seconds() / 86400.0
        return days
    
    def setup_vtk(self):

        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.0, 0.0, 0.0)
        self.render_window = self.vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = self.vtk_widget
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)
        
        self.add_stars_background()
        
        # Add light for sun
        self.sun_light = vtk.vtkLight()
        self.sun_light.SetPosition(0, 0, 0)
        self.sun_light.SetColor(1.0, 1.0, 1.0)
        self.sun_light.SetIntensity(3.0)
        self.renderer.AddLight(self.sun_light)
        ambient_light = vtk.vtkLight()
        ambient_light.SetColor(1.0, 1.0, 1.0)
        ambient_light.SetIntensity(0.8)
        ambient_light.SetPositional(False)
        self.renderer.AddLight(ambient_light)

        headlight = vtk.vtkLight()
        headlight.SetLightTypeToHeadlight()
        headlight.SetIntensity(0.6)
        headlight.SetColor(1.0, 1.0, 1.0)
        self.renderer.AddLight(headlight)

        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(40, -60, 40)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        camera.Azimuth(30)
        camera.Elevation(20)
        self.renderer.ResetCameraClippingRange()
        self.vtk_widget.Initialize()
    
    
    def add_stars_background(self):
        try:
            stars_reader = vtk.vtkJPEGReader()
            stars_reader.SetFileName("background_stars.jpg")
            stars_reader.Update()

            sphere = vtk.vtkSphereSource()
            sphere.SetThetaResolution(32)
            sphere.SetPhiResolution(32)
            sphere.SetRadius(5000)
            sphere.Update()
            
            sphere_texture = vtk.vtkTextureMapToSphere()
            sphere_texture.SetInputConnection(sphere.GetOutputPort())
            sphere_texture.PreventSeamOn()
            
            #map
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_texture.GetOutputPort())
            #actor
            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)
            # texture
            texture = vtk.vtkTexture()
            texture.SetInputConnection(stars_reader.GetOutputPort())
            texture.InterpolateOn()
            sphere_actor.SetTexture(texture)

            sphere_actor.GetProperty().SetOpacity(1.0)
            sphere_actor.GetProperty().SetAmbient(1.0)
            sphere_actor.GetProperty().BackfaceCullingOff()
            sphere_actor.GetProperty().FrontfaceCullingOn()
            
            # Add to renderer
            self.renderer.AddActor(sphere_actor)
            print("Stars background added")
        except Exception as e:
            print(f"Error stars background: {e}")
    
    def initialize_planets(self):
      self.add_celestial_body(
          name="Sun",
          mass=1.989e30,
          radius=696340000,
          color=(1.0, 1.0, 0.7),
          visual_scale=3.0,
          texture_path="sun_texture.jpg",
          rotation_period=609.6,  #  ~25.4 day
          axial_tilt=7.25
      )
      
      # Mercury
      self.add_celestial_body(
          name="Mercury",
          mass=0.330e24,
          radius=4879000/2,
          color=(0.8, 0.8, 0.8),
          visual_scale=3.0,
          texture_path="mercury_texture.jpg",
          rotation_period=1407.6,
          axial_tilt=0.03
      )
      
      # Venus
      self.add_celestial_body(
          name="Venus",
          mass=4.87e24,
          radius=12104000/2,
          color=(0.9, 0.8, 0.6),
          visual_scale=3.0,
          texture_path="venus_texture.jpg",
          rotation_period=-5832.5,
          axial_tilt=2.64
      )
      
      # Earth
      self.add_celestial_body(
          name="Earth",
          mass=5.97e24,
          radius=12756000/2,
          color=(0.2, 0.4, 0.8),
          visual_scale=3.0,
          texture_path="earth_texture.jpg",
          rotation_period=23.9,
          axial_tilt=23.44
      )
      
      self.add_celestial_body(
        name="Moon",
        mass=7.34767309e22,
        radius=3476000/2,
        color=(0.8, 0.8, 0.8),
        visual_scale=3.0,
        texture_path="moon_texture.jpg",
        rotation_period=655.7,
        axial_tilt=6.68,
        parent_body="Earth"
    )
      
      # Mars
      self.add_celestial_body(
          name="Mars",
          mass=0.642e24,
          radius=6792000/2,
          color=(0.9, 0.3, 0.2),
          visual_scale=3.0,
          texture_path="mars_texture.jpg",
          rotation_period=24.6,
          axial_tilt=25.19
      )
      
      # Jupiter
      self.add_celestial_body(
          name="Jupiter",
          mass=1898e24,  # From fact sheet
          radius=142984000/2,  # From fact sheet
          color=(0.9, 0.75, 0.6),
          visual_scale=3.0,
          texture_path="jupiter_texture.jpg",
          rotation_period=9.9,  # Very fast rotation
          axial_tilt=3.13
      )
      
      # Saturn
      self.add_celestial_body(
          name="Saturn",
          mass=568e24,  # From fact sheet
          radius=120536000/2,  # From fact sheet
          color=(0.9, 0.8, 0.6),
          visual_scale=3.0,
          texture_path="saturn_texture.jpg",
          rotation_period=10.7,  # Also fast rotation
          axial_tilt=26.73
      )
      
      
      # Uranus
      self.add_celestial_body(
          name="Uranus",
          mass=86.8e24,  # From fact sheet
          radius=51118000/2,  # From fact sheet
          color=(0.6, 0.8, 0.9),
          visual_scale=3.0,
          texture_path="uranus_texture.jpg",
          rotation_period=-17.2,  # Negative indicates retrograde rotation
          axial_tilt=82.23
      )
      
      # Neptune
      self.add_celestial_body(
          name="Neptune",
          mass=102e24,  # From fact sheet
          radius=49528000/2,  # From fact sheet
          color=(0.2, 0.3, 0.9),
          visual_scale=3.0,
          texture_path="neptune_texture.jpg",
          rotation_period=16.1,
          axial_tilt=28.32
      )
      
      # After adding all planets, populate the selection dropdown
      self.populate_planet_dropdown()
    
    def populate_planet_dropdown(self):
        """Populate the planet selection dropdown"""
        # Clear the dropdown first
        self.planet_combo.clear()
        
        # Add all bodies to the dropdown
        for name in self.bodies.keys():
            self.planet_combo.addItem(name)
            
        # Connect the selection change signal
        self.planet_combo.currentTextChanged.connect(self.display_planet_info)
    
    def display_planet_info(self, planet_name):
        """Display detailed information about the selected planet"""
        if not planet_name or planet_name not in self.bodies:
            self.planet_info.setText("No planet selected")
            return

        self.selected_planet = planet_name
            
        body = self.bodies[planet_name]
        
        # Format 
        info = f"<h3>{planet_name}</h3>"
        info += f"<b>Physical Properties:</b><br>"
        info += f"Mass: {body['mass']:.3e} kg<br>"
        info += f"Radius: {body['radius']:.0f} m<br>"
        if 'rotation_period' in body:
            info += f"Rotation Period: {abs(body['rotation_period']):.1f} hours"
            if body['rotation_period'] < 0:
                info += " (retrograde)<br>"
            else:
                info += "<br>"
        info += f"Axial Tilt: {body['axial_tilt']:.2f}°<br>"

        if planet_name != "Sun":
            info += f"<br><b>Orbital Elements:</b><br>"
            info += f"Semi-major Axis (a): {body['a']:.6f} AU<br>"
            info += f"Eccentricity (e): {body['e']:.6f}<br>"
            info += f"Inclination (i): {body['i']:.4f}°<br>"
            info += f"Longitude of Ascending Node (N): {body['N']:.4f}°<br>"
            info += f"Argument of Perihelion (w): {body['w']:.4f}°<br>"
            info += f"Mean Anomaly (M): {body['M']:.4f}°<br>"
            
            # Physics modifier
            info += f"<br><b>Physics Modifiers:</b><br>"
            info += f"Sun Mass: {self.sun_mass_scale:.2f}x<br>"
            info += f"G Multiplier: {self.G_multiplier:.2f}x<br>"
            info += f"Eccentricity Mult: {self.ecc_multiplier:.2f}x<br>"
            info += f"Inclination Mult: {self.inc_multiplier:.2f}x<br>"
            
            # Position calculation 
            info += f"<br><b>Position Calculation:</b><br>"
            info += "1. Calculate Eccentric Anomaly (E) from Mean Anomaly (M)<br>"
            info += "2. Calculate coordinates in orbital plane<br>"
            info += "3. Apply 3D rotations (w, i, N)<br>"
            
            # Current 
            if 'position' in body:
                pos = body['position']
                info += f"<br><b>Current Position (m):</b><br>"
                info += f"X: {pos[0]:.3e}<br>Y: {pos[1]:.3e}<br>Z: {pos[2]:.3e}<br>"
                
                # Add scaled position
                scaled = pos / self.scale_factor
                info += f"<br><b>Scaled Position (display units):</b><br>"
                info += f"X: {scaled[0]:.3f}<br>Y: {scaled[1]:.3f}<br>Z: {scaled[2]:.3f}<br>"
 
        self.planet_info.setHtml(info)
        self.focus_camera_on_planet(planet_name)
    
    def focus_camera_on_planet(self, planet_name):
        if planet_name not in self.bodies:
            return
            
        body = self.bodies[planet_name]

        scaled_position = body['position'] / self.scale_factor
        
        camera = self.renderer.GetActiveCamera()
        
        if planet_name == "Sun":
            distance = 100
            camera.SetPosition(distance, -distance, distance)
            camera.SetFocalPoint(0, 0, 0)
        elif planet_name == "Mercury":
            pos = np.array([scaled_position[0], scaled_position[1], scaled_position[2]])
            
            distance = np.linalg.norm(pos)
            direction = pos / (distance + 1e-10)
            
            mercury_semimajor = self.bodies['Mercury']['a'] * self.AU / self.scale_factor
            
            camera_distance = mercury_semimajor * 6.0
            
            camera_pos = pos - direction * camera_distance
            camera_pos[2] += camera_distance * 0.7
            
            camera.SetPosition(camera_pos)
            
            focal_offset = direction * mercury_semimajor * 0.5
            focal_point = scaled_position - focal_offset
            camera.SetFocalPoint(focal_point)
        elif planet_name in ["Uranus", "Neptune"]:
            pos = np.array([scaled_position[0], scaled_position[1], scaled_position[2]])
            
            distance = np.linalg.norm(pos)
            
            direction = pos / (distance + 1e-10)
            
            camera_distance = distance * 0.5
            
            camera_pos = pos - direction * (camera_distance * 0.3)
            camera_pos[2] += camera_distance * 0.3
            
            camera.SetPosition(camera_pos)
            camera.SetFocalPoint(scaled_position)
            
            print(f"Focusing on {planet_name} at position: {scaled_position}")
            print(f"Camera position: {camera_pos}")
        else:
            pos = np.array([scaled_position[0], scaled_position[1], scaled_position[2]])

            direction = pos / (np.linalg.norm(pos) + 1e-10)
            distance = np.linalg.norm(pos)
            
            camera_distance = min(40, max(15, distance * 2.5))
            
            camera_pos = pos - direction * camera_distance * 0.7
            camera_pos[2] += camera_distance * 0.6
            
            camera.SetPosition(camera_pos)
            
            offset = direction * distance * 0.3
            focal_point = scaled_position - (offset * 0.2)
            camera.SetFocalPoint(focal_point)
        
        camera.SetViewUp(0, 0, 1)
        
        self.renderer.ResetCameraClippingRange()
        
        self.vtk_widget.GetRenderWindow().Render()
    
    def add_celestial_body(self, name, mass, radius, color, visual_scale=1.0, texture_path=None, rotation_period=24.0, axial_tilt=0.0,parent_body=None):

        body = {
            'name': name,
            'mass': mass,
            'radius': radius,
            'color': color,
            'texture_path': texture_path,
            'rotation_period': rotation_period,  # Add rotat
            'rotation_angle': 0.0,
            'axial_tilt': axial_tilt,
            'parent_body': parent_body,
            'a': 0.0,  # Semi-major axis (AU)
            'e': 0.0,  # Eccentricity
            'i': 0.0,  # Inclination (degrees)
            'N': 0.0,  # Longitude of ascending node (degrees)
            'w': 0.0,  # Argument of perihelion (degrees)
            'M': 0.0,  # Mean anomaly (degrees)
            'actor': None,
            'orbit_actor': None
        }
        
        sphere = vtk.vtkSphereSource()
        
        visual_radius = 0.3 * math.log10(1 + radius / 1e6) * visual_scale
        if name == "Moon":
          visual_radius *= 1.0
        sphere.SetRadius(visual_radius)
        sphere.SetThetaResolution(30)
        sphere.SetPhiResolution(30)
        sphere.Update()
        
        text_map = vtk.vtkTextureMapToSphere()
        text_map.SetInputConnection(sphere.GetOutputPort())
        text_map.PreventSeamOn()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(text_map.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        if texture_path and os.path.exists(texture_path):
            try:
                extension = texture_path.split('.')[-1].lower()
                if extension == 'jpg' or extension == 'jpeg':
                    reader = vtk.vtkJPEGReader()
                elif extension == 'png':
                    reader = vtk.vtkPNGReader()
                else:
                    raise ValueError(f"Unsupported texture format: {extension}")
                
                reader.SetFileName(texture_path)
                reader.Update()
                
                texture = vtk.vtkTexture()
                texture.SetInputConnection(reader.GetOutputPort())
                texture.InterpolateOn()
                
                actor.SetTexture(texture)
                
                #print(f"Texture applied to {name} successfully")
            except Exception as e:
                #print(f"Error loading texture for {name}: {e}. Using color instead.")
                actor.GetProperty().SetColor(color)
        else:
            print(f"Texture file for {name} not found at {texture_path}. Using color.")
            actor.GetProperty().SetColor(color)
        
        actor.GetProperty().SetAmbient(0.3)
        actor.GetProperty().SetDiffuse(0.8)
        actor.GetProperty().SetSpecular(0.2)
        actor.GetProperty().SetSpecularPower(10)
        self.renderer.AddActor(actor)
        body['actor'] = actor

        vis = visual_radius
        axis_mapper = vtk.vtkPolyDataMapper()
        cyl = vtk.vtkCylinderSource()
        cyl.SetRadius(vis * 0.02)
        cyl.SetHeight(vis * 3.0)
        cyl.SetResolution(12)
        cyl.Update()
        axis_mapper.SetInputConnection(cyl.GetOutputPort())
        axis_actor = vtk.vtkActor()
        axis_actor.SetMapper(axis_mapper)
        axis_actor.GetProperty().SetColor(1.0, 0.2, 0.2)
        axis_actor.GetProperty().SetAmbient(1.0)
        axis_actor.RotateX(90)
        self.renderer.AddActor(axis_actor)
        body['axis_actor'] = axis_actor
        
        self.bodies[name] = body
        
        print(f"Added {name}")
        return body
    def setup_time_controls(self):
      time_controls = QHBoxLayout()
      
      self.play_button = QPushButton("▶ Play")
      self.play_button.clicked.connect(self.toggle_animation)
      time_controls.addWidget(self.play_button)
      
      speed_label = QLabel("Speed:")
      time_controls.addWidget(speed_label)
      
      self.speed_combo = QComboBox()
      self.speed_combo.addItems(["1x", "5x", "10x", "50x", "100x"])
      self.speed_combo.currentTextChanged.connect(self.change_speed)
      time_controls.addWidget(self.speed_combo)
      
      reset_button = QPushButton("Reset")
      reset_button.clicked.connect(self.reset_time)
      time_controls.addWidget(reset_button)
      
      self.layout.addLayout(time_controls)
      
      self.animation_timer = QTimer()
      self.animation_timer.timeout.connect(self.advance_time)
      self.animation_speed = 1  # days per step
      self.animation_active = False

    def toggle_animation(self):
        if self.animation_active:
            self.animation_timer.stop()
            self.animation_active = False
            self.play_button.setText("▶ Play")
        else:
            self.animation_timer.start(50)
            self.animation_active = True
            self.play_button.setText("⏸ Pause")

    def change_speed(self, speed_text):
        speed = int(speed_text.replace('x', ''))
        self.animation_speed = speed

    def advance_time(self):
        current_day = self.slider.value()
        new_day = current_day + self.animation_speed
        
        self.update_planet_rotations(self.animation_speed)
        
        if new_day > self.slider.maximum():
            new_day = self.slider.minimum()
        
        self.slider.setValue(new_day)

    def reset_time(self):
        self.slider.setValue(self.compute_initial_days())
        if self.animation_active:
            self.toggle_animation()
            
    def update_planet_rotations(self, time_step=1.0):
      for name, body in self.bodies.items():
          if 'rotation_period' in body and body['rotation_period'] != 0:
              if abs(body['rotation_period']) < 0.001:
                  continue
                  
              rotation_per_day = 24.0 / abs(body['rotation_period'])
              
              rotation_increment = rotation_per_day * 360.0 * time_step
              
              if body['rotation_period'] < 0:
                  rotation_increment = -rotation_increment
              
              if 'rotation_angle' not in body:
                  body['rotation_angle'] = 0.0
              
              body['rotation_angle'] = (body['rotation_angle'] + rotation_increment) % 360.0
              
                  
    def update_orbital_elements(self):
        d = self.day_number
        
        self.bodies['Mercury']['N'] = 48.3313 + 3.24587e-5 * d
        # Mercury
        self.bodies['Mercury']['N'] = 48.3313 + 3.24587e-5 * d
        self.bodies['Mercury']['i'] = 7.0047 + 5.00e-8 * d
        self.bodies['Mercury']['w'] = 29.1241 + 1.01444e-5 * d
        self.bodies['Mercury']['a'] = 0.387098
        self.bodies['Mercury']['e'] = 0.205635 + 5.59e-10 * d
        self.bodies['Mercury']['M'] = 168.6562 + 4.0923344368 * d
        
        # Venus
        self.bodies['Venus']['N'] = 76.6799 + 2.46590e-5 * d
        self.bodies['Venus']['i'] = 3.3946 + 2.75e-8 * d
        self.bodies['Venus']['w'] = 54.8910 + 1.38374e-5 * d
        self.bodies['Venus']['a'] = 0.723330
        self.bodies['Venus']['e'] = 0.006773 - 1.302e-9 * d
        self.bodies['Venus']['M'] = 48.0052 + 1.6021302244 * d
        
        # Earth
        self.bodies['Earth']['N'] = 0.0
        self.bodies['Earth']['i'] = 0.0
        self.bodies['Earth']['w'] = 282.9404 + 4.70935e-5 * d
        self.bodies['Earth']['a'] = 1.000000
        self.bodies['Earth']['e'] = 0.016709 - 1.151e-9 * d
        self.bodies['Earth']['M'] = 356.0470 + 0.9856002585 * d
        
        # Mars
        self.bodies['Mars']['N'] = 49.5574 + 2.11081e-5 * d
        self.bodies['Mars']['i'] = 1.8497 - 1.78e-8 * d
        self.bodies['Mars']['w'] = 286.5016 + 2.92961e-5 * d
        self.bodies['Mars']['a'] = 1.523688
        self.bodies['Mars']['e'] = 0.093405 + 2.516e-9 * d
        self.bodies['Mars']['M'] = 18.6021 + 0.5240207766 * d
        
        # Jupiter
        self.bodies['Jupiter']['N'] = 100.4542 + 2.76854e-5 * d
        self.bodies['Jupiter']['i'] = 1.3030 - 1.557e-7 * d
        self.bodies['Jupiter']['w'] = 273.8777 + 1.64505e-5 * d
        self.bodies['Jupiter']['a'] = 5.20256
        self.bodies['Jupiter']['e'] = 0.048498 + 4.469e-9 * d
        self.bodies['Jupiter']['M'] = 19.8950 + 0.0830853001 * d
        
        # Saturn
        self.bodies['Saturn']['N'] = 113.6634 + 2.38980e-5 * d
        self.bodies['Saturn']['i'] = 2.4886 - 1.081e-7 * d
        self.bodies['Saturn']['w'] = 339.3939 + 2.97661e-5 * d
        self.bodies['Saturn']['a'] = 9.55475
        self.bodies['Saturn']['e'] = 0.055546 - 9.499e-9 * d
        self.bodies['Saturn']['M'] = 316.9670 + 0.0334442282 * d
        
        # Uranus
        self.bodies['Uranus']['N'] = 74.0005 + 1.3978e-5 * d
        self.bodies['Uranus']['i'] = 0.7733 + 1.9e-8 * d
        self.bodies['Uranus']['w'] = 96.6612 + 3.0565e-5 * d
        self.bodies['Uranus']['a'] = 19.18171 - 1.55e-8 * d
        self.bodies['Uranus']['e'] = 0.047318 + 7.45e-9 * d
        self.bodies['Uranus']['M'] = 142.5905 + 0.011725806 * d
        
        # Neptune
        self.bodies['Neptune']['N'] = 131.7806 + 3.0173e-5 * d
        self.bodies['Neptune']['i'] = 1.7700 - 2.55e-7 * d
        self.bodies['Neptune']['w'] = 272.8461 - 6.027e-6 * d
        self.bodies['Neptune']['a'] = 30.05826 + 3.313e-8 * d
        self.bodies['Neptune']['e'] = 0.008606 + 2.15e-9 * d
        self.bodies['Neptune']['M'] = 260.2471 + 0.005995147 * d
        
        # Normalize all angles to 0-360 degrees
        for body in self.bodies.values():
            if body['name'] != 'Sun':
                body['N'] = body['N'] % 360
                body['i'] = body['i'] % 360
                body['w'] = body['w'] % 360
                body['M'] = body['M'] % 360
        self.update_moon_orbital_elements()
    
    def calculate_planet_positions(self):
        for name, body in self.bodies.items():
            if body.get('parent_body') is None:
                body['position'] = self.calculate_position_from_elements(body)

        for name, body in self.bodies.items():
            parent_name = body.get('parent_body')
            if parent_name:
                parent_body = self.bodies[parent_name]
                rel_pos = self.calculate_position_from_elements(body)
                if body['name'] == 'Moon':
                    rel_pos = rel_pos * 50.0
                body['position'] = parent_body['position'] + rel_pos

        for name, body in self.bodies.items():
            self.update_actor_position(body)

        #Reposition 
        for name, body in self.bodies.items():
            orbit_actor = body.get('orbit_actor')
            parent = body.get('parent_body')
            if orbit_actor is not None and parent is not None:
                parent_scaled = self.bodies[parent]['position'] / self.scale_factor
                orbit_actor.SetPosition(parent_scaled)
    def calculate_position_from_elements(self, body):
        a = body['a']
        if body.get('parent_body') is None:
            a = a / (self.sun_mass_scale ** (1.0 / 3.0))
        e = body['e']
        i = np.radians(body['i'])
        N = np.radians(body['N'])
        w = np.radians(body['w'])
        M = np.radians(body['M'])
        
        if e < 0.8:
            E = M
        else:
            E = np.pi
        
        # Iterat Kepler's equation
        for _ in range(10):
            E_next = M + e * np.sin(E)
            if abs(E_next - E) < 1e-8:
                break
            E = E_next
        
        x_orbit = a * (np.cos(E) - e)
        y_orbit = a * np.sqrt(1 - e*e) * np.sin(E)
        z_orbit = 0.0
        
        # Rotate
        x_temp = x_orbit * np.cos(w) - y_orbit * np.sin(w)
        y_temp = x_orbit * np.sin(w) + y_orbit * np.cos(w)
        z_temp = z_orbit
        
        x_temp2 = x_temp
        y_temp2 = y_temp * np.cos(i) - z_temp * np.sin(i)
        z_temp2 = y_temp * np.sin(i) + z_temp * np.cos(i)
        
        # rotate
        x = x_temp2 * np.cos(N) - y_temp2 * np.sin(N)
        y = x_temp2 * np.sin(N) + y_temp2 * np.cos(N)
        z = z_temp2
        
        #to meters
        position = np.array([x, y, z]) * self.AU
        
        return position
    
    def update_actor_position(self, body):
      if body['actor'] is not None:
          scaled_position = body['position'] / self.scale_factor
          body['actor'].SetPosition(0, 0, 0)
          body['actor'].SetOrientation(0, 0, 0)
          
          # Apply rotation
          if 'rotation_angle' in body:
              body['actor'].RotateZ(body['rotation_angle'])
              
          # Apply axial tilt
          if 'axial_tilt' in body:
              body['actor'].RotateY(body['axial_tilt'])

          #set pos
          body['actor'].SetPosition(scaled_position)

      if 'axis_actor' in body:
          ax = body['axis_actor']
          ax.SetPosition(scaled_position)
          # Orient axis Y to Z, then apply tilt
          tilt = body.get('axial_tilt', 0.0)
          ax.SetOrientation(90 + tilt, 0.0, 0.0)

    def create_orbit_paths(self):
        for name, body in self.bodies.items():
            if name == 'Sun':
                continue
            
            num_points = 100
            
            current_M = body['M']
            
            points = vtk.vtkPoints()
            
            if body.get('parent_body') is None:
                reference_pos = np.array([0, 0, 0])
            else:
                parent_name = body['parent_body']
                parent_pos = self.bodies[parent_name]['position']
                reference_pos = parent_pos / self.scale_factor
            
            for i in range(num_points):
                body['M'] = i * 360.0 / num_points
                
                if body.get('parent_body') is None:
                    position = self.calculate_position_from_elements(body)
                    scaled_position = position / self.scale_factor
                else:
                    relative_position = self.calculate_position_from_elements(body)
                    if body['name'] == 'Moon':
                        relative_position = relative_position * 50.0
                    scaled_position = relative_position / self.scale_factor
                
                points.InsertNextPoint(scaled_position)
            
            # loop close
            body['M'] = 0
            if body.get('parent_body') is None:
                position = self.calculate_position_from_elements(body)
                scaled_position = position / self.scale_factor
            else:
                relative_position = self.calculate_position_from_elements(body)
                if body['name'] == 'Moon':
                    relative_position = relative_position * 50.0
                scaled_position = relative_position / self.scale_factor
            points.InsertNextPoint(scaled_position)
            
            #  mean anomaly restore
            body['M'] = current_M
            
            line = vtk.vtkPolyLine()
            line.GetPointIds().SetNumberOfIds(num_points + 1)
            for i in range(num_points + 1):
                line.GetPointIds().SetId(i, i)

            cells = vtk.vtkCellArray()
            cells.InsertNextCell(line)

            polydata = vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetLines(cells)
            
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(polydata)
            
            orbit_actor = vtk.vtkActor()
            orbit_actor.SetMapper(mapper)
            
            # Set color
            r, g, b = body['color']
            orbit_actor.GetProperty().SetColor(r, g, b)
            orbit_actor.GetProperty().SetOpacity(0.5)
            orbit_actor.GetProperty().SetLineWidth(2.0)
            
            # parent  orbit 
            if body.get('parent_body') is not None:
                parent_scaled = self.bodies[body['parent_body']]['position'] / self.scale_factor
                orbit_actor.SetPosition(parent_scaled)

            if hasattr(self, 'show_orbits_checkbox'):
                if self.show_orbits_checkbox.isChecked():
                    orbit_actor.VisibilityOn()
                else:
                    orbit_actor.VisibilityOff()

            self.renderer.AddActor(orbit_actor)

            body['orbit_actor'] = orbit_actor

    def remove_orbit_paths(self):
        for body in self.bodies.values():
            actor = body.get('orbit_actor')
            if actor is not None:
                self.renderer.RemoveActor(actor)
                body['orbit_actor'] = None
            
    # def add_gravity_field_glyphs(self):
    #   print("Adding balanced gravity field visualization...")
    #   import vtk
    #   import numpy as np
      
    #   # Create points in spherical shells with reduced density
    #   points = vtk.vtkPoints()
    #   vectors = vtk.vtkDoubleArray()
    #   vectors.SetNumberOfComponents(3)
    #   vectors.SetName("GravityField")
      
    #   # Use fewer points and larger spacing between shells
    #   total_points = 150  # Significantly reduced from 600
      
    #   # Use specific radii for better visual organization
    #   radii = [2.0, 4.0, 7.0]  # Fewer shells, at strategic distances
      
    #   for radius in radii:
    #       # Calculate points per shell - more for outer shells
    #       points_this_shell = int(total_points * radius / 15)
          
    #       # Generate evenly distributed points on this shell
    #       # Using Fibonacci sphere algorithm for even distribution
    #       golden_ratio = (1 + 5**0.5) / 2
    #       for i in range(points_this_shell):
    #           # Generate even distribution on sphere
    #           i_float = float(i)
    #           theta = 2 * np.pi * i_float / golden_ratio
    #           phi = np.arccos(1 - 2 * (i_float + 0.5) / points_this_shell)
              
    #           # Calculate position, compressing z-axis slightly
    #           pos_x = radius * np.sin(phi) * np.cos(theta)
    #           pos_y = radius * np.sin(phi) * np.sin(theta)
    #           pos_z = radius * np.cos(phi) * 0.6  # Compress z-axis
              
    #           # Skip points too close to planets (with larger threshold)
    #           too_close = False
    #           for name, body in self.bodies.items():
    #               if name != 'Sun' and 'position' in body:
    #                   planet_pos = body['position'] / self.scale_factor
    #                   dist = np.sqrt((pos_x-planet_pos[0])**2 + 
    #                                 (pos_y-planet_pos[1])**2 + 
    #                                 (pos_z-planet_pos[2])**2)
    #                   # Use larger clearance radius around planets
    #                   if dist < 1.0:  
    #                       too_close = True
    #                       break
              
    #           if too_close:
    #               continue
              
    #           # Add point
    #           points.InsertNextPoint(pos_x, pos_y, pos_z)
              
    #           # Calculate gravity vector
    #           direction = np.array([-pos_x, -pos_y, -pos_z])
    #           r = np.linalg.norm(direction)
              
    #           if r > 0:
    #               # Normalize direction
    #               direction = direction / r
                  
    #               # More reasonable magnitude scaling - gentler falloff
    #               magnitude = 1.0 / (1.0 + 0.3 * r)
    #               vector = direction * magnitude * 1.5  # Reduced scaling factor
    #               vectors.InsertNextTuple(vector)
      
    #   # Create polydata
    #   polydata = vtk.vtkPolyData()
    #   polydata.SetPoints(points)
    #   polydata.GetPointData().SetVectors(vectors)
      
    #   # Create arrow glyph with more reasonable dimensions
    #   arrow = vtk.vtkArrowSource()
    #   arrow.SetTipResolution(12)
    #   arrow.SetShaftResolution(12)
    #   arrow.SetTipLength(0.3)
    #   arrow.SetTipRadius(0.1)
    #   arrow.SetShaftRadius(0.03)
      
    #   # Create glyph with moderate scaling
    #   glyph = vtk.vtkGlyph3D()
    #   glyph.SetSourceConnection(arrow.GetOutputPort())
    #   glyph.SetInputData(polydata)
    #   glyph.SetVectorModeToUseVector()
    #   glyph.SetScaleModeToScaleByVector()
    #   glyph.SetScaleFactor(1.2)  # Moderate scale
    #   glyph.OrientOn()
    #   glyph.Update()
      
    #   # Create mapper and actor
    #   mapper = vtk.vtkPolyDataMapper()
    #   mapper.SetInputConnection(glyph.GetOutputPort())
    #   mapper.ScalarVisibilityOff()
      
    #   actor = vtk.vtkActor()
    #   actor.SetMapper(mapper)
      
    #   # Use a more subtle color
    #   actor.GetProperty().SetColor(1.0, 0.7, 0.2)  # Less intense orange
    #   actor.GetProperty().SetOpacity(0.7)  # More transparency
      
    #   # Add to renderer
    #   self.renderer.AddActor(actor)
    #   self.gravity_glyph_actor = actor
      
    #   print(f"Added balanced gravity field visualization")
    #   self.vtk_widget.GetRenderWindow().Render()
      
    def add_labels(self):
        for name, body in self.bodies.items():
            text_actor = vtk.vtkTextActor()
            text_actor.SetInput(name)
            text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
            text_actor.GetTextProperty().SetFontSize(14)
            text_actor.GetTextProperty().SetJustificationToCentered()
            text_actor.GetTextProperty().SetVerticalJustificationToCentered()
            text_actor.GetTextProperty().SetBold(True)

            pos = list(body['actor'].GetPosition())
            pos[2] += 0.3
            
            follower = vtk.vtkBillboardTextActor3D()
            follower.SetInput(name)
            follower.SetPosition(pos)
            follower.GetTextProperty().SetColor(1.0, 1.0, 1.0)
            follower.GetTextProperty().SetFontSize(14)
            follower.GetTextProperty().SetJustificationToCentered()
            follower.GetTextProperty().SetVerticalJustificationToCentered()
            follower.GetTextProperty().SetBold(True)
            
            if hasattr(self, 'show_labels_checkbox'):
                if self.show_labels_checkbox.isChecked():
                    follower.VisibilityOn()
                else:
                    follower.VisibilityOff()
            
            self.renderer.AddActor(follower)
            body['label'] = follower
            
    def update_moon_orbital_elements(self):
      d = self.day_number
      
      # from NASA fact sheets   
      self.bodies['Moon']['N'] = 125.1228 - 0.0529538083 * d  # Longitude of ascending node 
      self.bodies['Moon']['i'] = 5.1454  # Inclination to ecliptic  
      self.bodies['Moon']['w'] = 318.0634 + 0.1643573223 * d  # Argument of perigee
      self.bodies['Moon']['a'] = 384400000 / self.AU  # Convert meters to AU
      
      self.bodies['Moon']['e'] = 0.0549  # Eccentricity
      self.bodies['Moon']['M'] = 115.3654 + 13.0649929509 * d  # Mean anomaly

      for element in ['N', 'i', 'w', 'M']:
          self.bodies['Moon'][element] = self.bodies['Moon'][element] % 360
            
    def store_original_orbital_elements(self):
        for name, body in self.bodies.items():
            if name != "Sun":
                self.original_orbital_elements[name] = {
                    'a': body['a'],
                    'e': body['e'],
                    'i': body['i'],
                    'N': body['N'],
                    'w': body['w'],
                    'M': body['M']
                }
    
    def on_physics_change(self):
        self.G_multiplier = self.g_spin.value()
        self.ecc_multiplier = self.ecc_spin.value()
        self.inc_multiplier = self.inc_spin.value()
    
    def apply_physics_changes(self):
        camera = self.renderer.GetActiveCamera()
        old_position = camera.GetPosition()
        old_focal_point = camera.GetFocalPoint()
        
        self.update_orbital_elements_phy()
        
        self.update_sun_size()
        
        self.calculate_planet_positions()
        
        self.remove_orbit_paths()
        self.create_orbit_paths()
        
        if self.selected_planet:
            self.display_planet_info(self.selected_planet)
        
        
        # to origin
        camera.SetPosition(old_position)
        camera.SetFocalPoint(old_focal_point)
        self.vtk_widget.GetRenderWindow().Render()
    
    def reset_physics(self):
        self.g_spin.setValue(1.0)
        self.ecc_spin.setValue(1.0)
        self.inc_spin.setValue(1.0)
        self.mass_spin.setValue(1.0)
        
        self.G_multiplier = 1.0
        self.ecc_multiplier = 1.0
        self.inc_multiplier = 1.0
        self.sun_mass_scale = 1.0
        self.update_sun_size()
        self.reset_orbital_elements()

        self.calculate_planet_positions()
        self.remove_orbit_paths()
        self.create_orbit_paths()
        if self.selected_planet:
            self.display_planet_info(self.selected_planet)

        self.vtk_widget.GetRenderWindow().Render()
    
    def reset_orbital_elements(self):
        for name, elements in self.original_orbital_elements.items():
            if name in self.bodies:
                for key, value in elements.items():
                    self.bodies[name][key] = value
    
    def update_orbital_elements_phy(self):
        self.update_orbital_elements()
        
        for name, body in self.bodies.items():
            if name != "Sun":
                if self.G_multiplier != 1.0:
                    body['a'] = body['a'] / self.G_multiplier
                
                if self.ecc_multiplier != 1.0:
                    original_e = self.original_orbital_elements[name]['e']
                    body['e'] = min(0.95, original_e * self.ecc_multiplier)
                
                if self.inc_multiplier != 1.0:
                    original_i = self.original_orbital_elements[name]['i']
                    body['i'] = original_i * self.inc_multiplier
    
    def toggle_orbit_visibility(self, state):
        for name, body in self.bodies.items():
            if 'orbit_actor' in body and body['orbit_actor'] is not None:
                if state == Qt.Checked:
                    body['orbit_actor'].VisibilityOn()
                else:
                    body['orbit_actor'].VisibilityOff()

        self.vtk_widget.GetRenderWindow().Render()

    def toggle_label_visibility(self, state):
        for name, body in self.bodies.items():
            if 'label' in body and body['label'] is not None:
                if state == Qt.Checked:
                    body['label'].VisibilityOn()
                else:
                    body['label'].VisibilityOff()

        self.vtk_widget.GetRenderWindow().Render()

def main():
    app = QApplication(sys.argv)
    window = SolarSystemApp()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()