# CubeSat Mission Control Training Simulator

A web-based CubeSat mission control simulator built with Python and Streamlit.

This project is designed as a beginner-friendly aerospace training tool that helps students understand CubeSat mission operations, telemetry monitoring, orbital behaviour, spacecraft power budgets, and mission failure response.

## Live Demo

https://cubesat-mission-control-simulator.streamlit.app

## Project Overview

The simulator allows users to control mission parameters and observe how they affect CubeSat performance during a mission. Users can adjust mission duration, orbital altitude, battery drain, solar charging, signal interference, payload mode, solar panel area, solar efficiency, and battery capacity.

The app then generates mission telemetry including battery level, signal strength, fuel level, orbital behaviour, mission events, and spacecraft power budget.

## Key Features

* Interactive CubeSat mission control dashboard
* Mission duration and altitude controls
* Orbital period calculation based on altitude
* Battery, signal, and fuel telemetry
* Spacecraft power budget model
* Solar panel area and efficiency controls
* Payload mode selection
* Mission events and fault scenarios
* Mission scoring and feedback
* Animated mission playback
* Ground station network concept
* CSV mission data export

## Technologies Used

* Python
* Streamlit
* NumPy
* Pandas
* Plotly
* Matplotlib

## Aerospace Concepts Demonstrated

This project introduces several aerospace engineering concepts:

* CubeSat mission operations
* Orbital altitude and orbital period
* Telemetry monitoring
* Battery charging and eclipse periods
* Solar power generation
* Payload power demand
* Mission failure response
* Ground station communication concepts
* Mission scoring and post-mission analysis

## Purpose

I built this project to strengthen my understanding of aerospace engineering, spacecraft systems, and mission operations while developing practical programming skills.

The long-term goal is to turn this into a beginner CubeSat training platform for students, colleges, outreach teams, and university aerospace societies.

## Future Improvements

Planned upgrades include:

* More realistic spacecraft power model
* Ground station pass windows
* Instructor mode
* Student mission worksheets
* AI mission analyst for failure explanations
* More detailed CubeSat subsystem modelling
* Improved user interface
* Login and classroom mode

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/lukejamey21-hub/CubeSat-Mission-Control-Simulator.git
```

Install requirements:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## Author

Created by Luke Jamey as an aerospace engineering learning and portfolio project.
