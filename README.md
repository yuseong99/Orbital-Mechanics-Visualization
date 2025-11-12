# An Interactive Orbital Visualization System for Educational Purposes

An interactive 3D educational tool for understanding orbital mechanics, developed as a final projecㅆ at Purdue University. This system allows users to observe celestial body motion and interactively modify core physical parameters such as solar mass, the gravitational constant, and orbital elements like eccentricity and inclination. By providing immediate visual feedback on these modifications, the tool makes abstract astrodynamics concepts more tangible and understandable.

**Published as an IEEE-format academic paper**: [Interactive Orbital Mechanics Visualization Report.pdf]

## Abstract

This interactive 3D orbital visualization system is designed as an educational tool to explain fundamental principles of orbital mechanics. The system, developed in Python using VTK for graphics and PyQt5 for the user interface, allows users to observe celestial body motion and crucially to interactively modify core physical parameters. By providing immediate visual feedback on these modifications, the tool aims to make abstract astrodynamics concepts more tangible and understandable for students.

Traditional teaching methods often rely on static diagrams and equations, which may not fully convey the dynamic and interconnected nature of orbital parameters. This tool bridges the gap between theoretical concepts and intuitive understanding through interactive "what-if" experimentation.

## Features

### Realistic Keplerian Orbital Mechanics
- **Accurate Position Calculations**: Planetary positions calculated using Keplerian orbital elements with iterative solution of Kepler's equation (M = E - e sin E)
- **NASA Data Sources**: Real astronomical data from NASA/JPL Solar System Dynamics and Planetary Fact Sheets
- **Time-based Simulation**: Orbital element propagation from J2000 epoch (January 1, 2000) extending 27+ years
- **Geocentric Moon Orbit**: Accurate Earth-Moon system with moon position calculated geocentrically and transformed to heliocentric coordinates

### Interactive Physics Parameter Manipulation
The core educational feature - allowing users to experiment with fundamental physical laws:

- **Sun Mass (Msun)**: Modify 0.1x - 3.0x
  - Directly impacts gravitational parameter μ = GMsun
  - Affects orbital periods via T² ∝ a³/μ
  - Visual size of Sun scales dynamically (∝ mass^0.33)

- **Gravitational Constant (G)**: Adjust multiplier 0.1x - 5.0x
  - Scales G, directly impacting μ and orbital periods
  - Demonstrates fundamental role of G in gravitational dynamics

- **Eccentricity (e)**: Scale orbital eccentricity 0.1x - 5.0x
  - Transforms circular orbits into elliptical ones
  - Capped at e < 0.95 to prevent unstable orbits

- **Inclination (i)**: Adjust orbital tilt 0.0x - 5.0x
  - Modifies the tilt of orbital planes relative to the ecliptic
  - Visualizes 3D nature of solar system

### Advanced Visualization Features
- **Textured Celestial Bodies**: High-resolution planetary textures from Solar System Scope
- **Rotation Animation**: Accurate rotation periods including retrograde rotation (Venus, Uranus)
- **Axial Tilt Visualization**: Separate axis actors showing planetary tilt angles
- **Orbital Path Rendering**: 100-point polylines for smooth orbit visualization
- **Billboard Text Labels**: Camera-facing labels that remain readable from any angle
- **Immersive Starfield**: Textured sphere background for spatial context
- **Dynamic Lighting**: Primary light source at Sun position with ambient lighting

### Comprehensive User Interface
- **Time Controls**:
  - Slider for precise date selection
  - Play/Pause animation with variable speed (1x, 5x, 10x, 50x, 100x)
  - Reset to current date
  - Date display showing current simulation time

- **Planet Selection & Focus**:
  - Dropdown menu for all celestial bodies
  - Automatic camera focusing with intelligent positioning for each planet
  - Special focus handling for Mercury, Uranus, and Neptune

- **Information Display Panel**:
  - Physical properties (mass, radius, rotation period, axial tilt)
  - Current orbital elements (a, e, i, N, ω, M)
  - Real-time position in both meters and display units
  - Active physics modifiers
  - Position calculation methodology explanation

- **Physics Parameter Controls**:
  - Spin boxes with precise value control
  - "Apply Physics Changes" for real-time updates
  - "Reset Physics" to restore default values

- **Display Options**:
  - Toggle orbital path visibility
  - Toggle planet label visibility

## Technologies Used

- **Python 3.x**
- **VTK (Visualization Toolkit)**: For 3D graphics rendering
- **PyQt5**: For GUI components
- **NumPy**: For numerical calculations
- **Keplerian Orbital Mechanics**: For accurate position calculations

## Installation

### Prerequisites

```bash
pip install vtk PyQt5 numpy
```

### Required Assets

The following texture files should be in the same directory as the script:
- `sun_texture.jpg`
- `mercury_texture.jpg`
- `venus_texture.jpg`
- `earth_texture.jpg`
- `moon_texture.jpg`
- `mars_texture.jpg`
- `jupiter_texture.jpg`
- `saturn_texture.jpg`
- `uranus_texture.jpg`
- `neptune_texture.jpg`
- `background_stars.jpg`

## Usage

Run the application:

```bash
python orbital_fw.py
```

### Controls

1. **Time Navigation**
   - Use the horizontal slider to move through time
   - Click "Play" to start animation
   - Adjust speed with the dropdown menu (1x - 100x)
   - Click "Reset" to return to current date

2. **Physics Manipulation**
   - Adjust physics parameters using spin boxes
   - Click "Apply Physics Changes" to update the simulation
   - Click "Reset Physics" to restore default values

3. **Viewing Options**
   - Select a planet from the dropdown to focus camera
   - Toggle "Orbital Paths" checkbox to show/hide orbits
   - Toggle "Planet Labels" checkbox to show/hide labels
   - Use mouse to rotate, zoom, and pan the 3D view

## Scientific Accuracy

### Orbital Elements
The simulation uses the following Keplerian orbital elements:
- **a**: Semi-major axis (AU)
- **e**: Eccentricity
- **i**: Inclination (degrees)
- **N**: Longitude of ascending node (degrees)
- **w**: Argument of perihelion (degrees)
- **M**: Mean anomaly (degrees)

### Position Calculation
Planet positions are calculated through:
1. Solving Kepler's equation to find Eccentric Anomaly (E)
2. Converting to orbital plane coordinates
3. Applying 3D rotations based on orbital elements
4. Converting from AU to meters

### Supported Celestial Bodies
- Sun
- Mercury
- Venus
- Earth
- Moon (with accurate orbit around Earth)
- Mars
- Jupiter
- Saturn
- Uranus
- Neptune

## Project Structure

```
orbital_fw.py           # Main application file
*.jpg                   # Planet and background textures
README.md              # This file
```

## Key Classes and Methods

### `SolarSystemApp`
Main application class inheriting from `QMainWindow`

**Key Methods:**
- `initialize_planets()`: Set up all celestial bodies with physical properties
- `update_orbital_elements()`: Calculate time-dependent orbital parameters
- `calculate_position_from_elements()`: Convert orbital elements to 3D positions
- `create_orbit_paths()`: Generate orbital path visualizations
- `on_physics_change()`: Handle physics parameter modifications
- `focus_camera_on_planet()`: Automatic camera positioning

## Physics Modifiers

The application allows experimentation with fundamental physics parameters:

- **Sun Mass**: Affects all orbital periods through Kepler's third law (T² ∝ a³/M)
- **G Multiplier**: Changes the gravitational constant's effect on orbits
- **Eccentricity**: Controls how elliptical the orbits are
- **Inclination**: Adjusts the tilt of orbital planes

## Performance Considerations

- Orbit paths use 100 points for smooth rendering
- Background sphere radius: 5000 units
- Scale factor: 1e10 for appropriate display units
- Iterative solver for Kepler's equation with 10 iterations

## Educational Applications

This visualization is ideal for:
- Understanding Keplerian orbital mechanics
- Visualizing the effects of physics parameters on orbits
- Demonstrating planetary motion over time
- Exploring the Solar System's 3D structure
- Teaching computational astronomy

## Future Enhancements

Potential improvements could include:
- Additional moons for other planets
- Asteroid belt visualization
- Comet trajectories
- N-body gravitational interactions
- Export of orbital data
