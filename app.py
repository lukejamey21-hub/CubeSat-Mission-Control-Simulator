from argparse import Action
from unittest import signals

from altair import Latitude
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import random   

st.set_page_config(page_title="CubeSat Mission Control", layout="wide")

st.title("🛰️ CubeSat Mission Control System")
st.caption("Interactive beginner CubeSat simulator")

left, right = st.columns([1, 2])

with left:
    st.header("Control Panel")

    mission_hours = st.slider("Mission Duration (hours)", 6, 72, 24)
    altitude = st.slider(
        "Orbit Altitude (km)",
        min_value=300,
        max_value=1200,
        value=500,
    )
    battery_drain = st.slider("Battery Drain Rate", 1, 12, 4)
    solar_charge = st.slider("Solar Charge Rate", 0, 10, 3)
    solar_panel_area = st.slider(
        "Solar Panel Area (m²)",
        min_value=0.01,
        max_value=0.20,
        value=0.05,
    )

    solar_efficiency = st.slider(
        "Solar Panel Efficiency (%)",
        min_value=10,
        max_value=35,
        value=25,
    )

    battery_capacity_wh = st.slider(
        "Battery Capacity (Wh)",
        min_value=20,
        max_value=200,
        value=80,
    )

    signal_noise = st.slider("Signal Interference", 0, 80, 30)
    signal_noise = st.slider(
        "Signal noise",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.01,
    )

    payload = st.selectbox(
        "Payload mode",
        ["off", "science payload", "payload power"],
    )

    science_data = 0
    if payload == "science payload":
        science_data = mission_hours * 3
        battery_drain += 2
    elif payload == "payload power":
        science_data = mission_hours
        battery_drain += 1

    launch = st.button("Launch Mission")

with right:
    st.header("Telemetry")

    t = np.arange(0, mission_hours + 1, 1)

    # Orbit model - speed now visibly changes number of loops
    earth_radius = 6371
    mu = 398600

    orbit_radius = earth_radius + altitude
    orbital_period = 2 * np.pi * np.sqrt(orbit_radius**3 / mu)
    orbital_period_hours = orbital_period / 3600
    orbit_speed = 2 * np.pi / orbital_period_hours
    angle = orbit_speed * t
    x = np.cos(angle)
    y = np.sin(angle)
    st.divider()
    st.header("⚠️ Mission Event")

    # Sunlight/eclipse model
    eclipse_fraction = 0.35
    orbit_phase = (t % orbital_period_hours) / orbital_period_hours
    sunlight = orbit_phase > eclipse_fraction

    fuel = []
    fuel_level = 100

    battery = []
    charge = 100

    for sun in sunlight:

        if sun:
            charge += solar_charge

        else:
            charge -= battery_drain

        charge = max(0, min(100, charge))
        battery.append(charge)

        fuel_level -= 0.03
        fuel_level = max(0, fuel_level)

        fuel.append(fuel_level)

    battery = np.array(battery)

    # Signal model - interference slider now clearly affects signal
    signal = 100 - (np.abs(np.sin(angle)) * signal_noise)
    signal = np.clip(signal, 0, 100)
    # Realistic power budget model
solar_constant = 1361  # W/m² from the Sun near Earth

solar_power_generated = (
    solar_constant
    * solar_panel_area
    * (solar_efficiency / 100)
)

base_satellite_power = 5  # W

if payload == "science payload":
    payload_power_required = 8

elif payload == "payload power":
    payload_power_required = 4

else:
    payload_power_required = 0

total_power_required = base_satellite_power + payload_power_required

if sunlight[-1]:
    net_power = solar_power_generated - total_power_required
else:
    net_power = -total_power_required
    
    ground_stations = pd.DataFrame({
    "Station": ["Bristol", "Tokyo", "Houston"],
    "lat": [51.45, 35.68, 29.76],
    "lon": [-2.59, 139.69, -95.36]
})

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Final Battery", f"{battery[-1]:.0f}%")
    col2.metric("Final Signal", f"{signal[-1]:.0f}%")
    col3.metric("Fuel", f"{fuel[-1]:.0f}%")
    col4.metric("Altitude", f"{altitude} km")
    col5.metric("Orbital Period", f"{orbital_period_hours:.2f} h")
    col5.metric("Mission Time", f"{mission_hours}h")

    if battery[-1] <= 0:
        st.error("🔴 Mission Failed: Battery depleted")
    elif battery[-1] < 30:
        st.warning("🟡 Mission Warning: Low battery")
    else:
        st.success("🟢 Mission Stable: Systems nominal")

    tab1, tab2, tab3 = st.tabs(["Orbit", "Battery", "Signal"])

    with tab1:
        fig1, ax1 = plt.subplots()
        ax1.plot(x, y)
        ax1.scatter(x[0], y[0], label="Start")
        ax1.scatter(x[-1], y[-1], label="Current")
        ax1.set_title("Orbit Path")
        ax1.set_xlabel("X Position")
        ax1.set_ylabel("Y Position")
        ax1.axis("equal")
        ax1.legend()
        st.pyplot(fig1)

    with tab2:
        fig2, ax2 = plt.subplots()
        ax2.plot(t, battery)
        ax2.set_title("Battery Level Over Mission")
        ax2.set_xlabel("Time (hours)")
        ax2.set_ylabel("Battery (%)")
        ax2.set_ylim(0, 105)
        st.pyplot(fig2)

    with tab3:
        fig3, ax3 = plt.subplots()
        ax3.plot(t, signal)
        ax3.set_title("Signal Strength Over Mission")
        ax3.set_xlabel("Time (hours)")
        ax3.set_ylabel("Signal (%)")
        ax3.set_ylim(0, 105)
        st.pyplot(fig3)

        st.divider()

st.header("Mission Report")

st.divider()
st.header("⚠️ Mission Event")
event = st.selectbox(
    "Training Event",
    [
        "None",
        "Solar Storm",
        "Ground Station Failure",
        "Camera Overheating",
        "Reaction Wheel Fault",
        "Extended Eclipse"
    ],
    key="training_event."
)
if event == "Solar Storm":
    st.warning("Solar storm detected. Signal interference increased.")
    signal_noise += 25

action = st.radio(
    "Student Response",
    [
        "Hold current settings",
        "Reduce science payload",
        "Increase transmitter power",
        "Enter low power mode"
    ]
)
if event == "Ground Station Failure":
    st.warning("Ground station issue detected. Signal reduced.")
    signal_noise += 35
elif event == "Camera Overheating":
    st.warning("Payload overheating. Battery drain increased.")
    battery_drain += 3

elif event == "Reaction Wheel Fault":
    st.warning("Attitude control issue. Orbit stability reduced.")
    signal_noise += 10

elif event == "Extended Eclipse":
    st.warning("Longer eclipse period. Battery drain increased.")
    battery_drain += 4


if action == "Reduce science payload":
    st.info("Payload reduced. Battery drain lowered, but mission data collection is reduced.")
    battery_drain = max(1, battery_drain - 3)

elif action == "Increase transmitter power":
    st.info("Transmitter boosted. Signal improves, but battery drain increases.")
    signal_noise = max(0, signal_noise - 25)
    battery_drain += 2

elif action == "Enter low power mode":
    st.info("Low power mode active. Battery protected, but signal performance reduced.")
    battery_drain = max(1, battery_drain - 4)
    signal_noise += 15

else:
    st.info("No corrective action taken.")

average_signal = signal.mean()
final_battery = battery[-1]

if final_battery > 30 and average_signal > 60:
    st.success("✅ Mission Passed")
else:
    st.error("❌ Mission Failed")

st.write(f"Final battery level: {final_battery:.0f}%")
st.write(f"Average signal strength: {average_signal:.0f}%")

mission_data = pd.DataFrame({
    "Time (hours)": t,
    "Battery (%)": battery,
    "Signal (%)": signal,
    "Sunlight": sunlight
})
events = []

for i in range(len(t)):
    if battery[i] < 20:
        events.append(f"Hour {t[i]}: Critical battery warning")

    if signal[i] < 50:
        events.append(f"Hour {t[i]}: Weak communication signal")

    if sunlight[i] == False:
        events.append(f"Hour {t[i]}: CubeSat entered eclipse")

csv = mission_data.to_csv(index=False)

st.download_button(
    label="Download Mission Data CSV",
    data=csv,
    file_name="cubesat_mission_data.csv",
    mime="text/csv"
)
st.subheader("Mission Briefing")

scenario = st.selectbox(
    "Choose Training Scenario,",
    [
        "72-Hour Survival Orbit",
        "High Data Earth Imaging",
        "Emergency Low Power Mode",
        "Comms Blackout Recovery"
    ],
    key="training_scenario"
)

if scenario == "72-Hour Survival Orbit":
    st.info("""
    Objective: Keep the CubeSat alive for 72 hours.

    Student directive:
    Balance orbit speed, battery drain, and solar charging.
    Your mission passes if final battery stays above 25%
    and average signal stays above 60%.
    """)

elif scenario == "High Data Earth Imaging":
    st.info("""
    Objective: Simulate an imaging mission with high power use.

    Student directive:
    Expect faster battery drain. Adjust settings to survive
    while keeping signal above 65%.
    """)

elif scenario == "Emergency Low Power Mode":
    st.info("""
    Objective: Recover a CubeSat with low remaining power.

    Student directive:
    Reduce battery drain and maximise solar charge.
    Your goal is to avoid battery dropping below 15%.
    """)

elif scenario == "Comms Blackout Recovery":
    st.info("""
    Objective: Recover communication after signal interference.

    Student directive:
    Lower signal interference and maintain average signal above 70%.
    """)
    st.header("Mission Objectives")

final_battery = battery[-1]
average_signal = signal.mean()
min_battery = battery.min()
st.divider()
st.header("🛰 Mission Control Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Battery", f"{final_battery:.0f}%")

with col2:
    st.metric("Signal", f"{average_signal:.0f}%")

with col3:
    st.metric("Mission Hours", mission_hours)

if scenario == "72-Hour Survival Orbit":
    pass_mission = final_battery > 25 and average_signal > 60
    st.write("✅ Keep final battery above 25%")
    st.write("✅ Keep average signal above 60%")

elif scenario == "High Data Earth Imaging":
    pass_mission = final_battery > 20 and average_signal > 65
    st.write("✅ Final battery above 20%")
    st.write("✅ Average signal above 65%")

elif scenario == "Emergency Low Power Mode":
    pass_mission = min_battery > 15
    st.write("✅ Battery must never drop below 15%")

elif scenario == "Comms Blackout Recovery":
    pass_mission = average_signal > 70
    st.write("✅ Average signal above 70%")

if pass_mission:
    st.success("🎉 Mission Passed")
else:
    st.error("❌ Mission Failed — adjust your controls and try again")
    st.divider()
st.header("🏆 Mission Scoreboard")

battery_score = min(25, int(final_battery / 4))
signal_score = min(25, int(average_signal / 4))
survival_score = 25 if min_battery > 15 else 10
decision_score = 25 if action != "Hold current settings" and event != "None" else 10

total_score = battery_score + signal_score + survival_score + decision_score

col1, col2, col3, col4 = st.columns(4)

col1.metric("Battery Score", f"{battery_score}/25")
col2.metric("Signal Score", f"{signal_score}/25")
col3.metric("Survival Score", f"{survival_score}/25")
col4.metric("Decision Score", f"{decision_score}/25")


st.subheader("Final Mission Score")
st.progress(total_score / 100)

if total_score >= 85:
    st.success(f"Grade A — Excellent mission control: {total_score}/100")
elif total_score >= 70:
    st.success(f"Grade B — Strong mission performance: {total_score}/100")
elif total_score >= 50:
    st.warning(f"Grade C — Mission survived but needs improvement: {total_score}/100")
else:
    st.error(f"Fail — Mission objectives not met: {total_score}/100")

st.subheader("Flight Director Feedback")
st.subheader("🛰️ Satellite Health")

if final_battery > 70:
    st.success("Battery Systems: NOMINAL")
elif final_battery > 30:
    st.warning("Battery Systems: CAUTION")
else:
    st.error("Battery Systems: CRITICAL")

if average_signal > 80:
    st.success("Communications: NOMINAL")
elif average_signal > 50:
    st.warning("Communications: DEGRADED")
else:
    st.error("Communications: CRITICAL")

if battery_score < 15:
    st.write("🔋 Improve battery management. Reduce drain or increase solar charge.")

if signal_score < 15:
    st.write("📡 Improve communication performance. Reduce interference or boost signal.")

if survival_score < 25:
    st.write("🚨 CubeSat entered dangerous power levels. Use safe mode earlier.")

if decision_score < 25:
    st.write("🧠 You did not respond effectively to mission events. Pick a corrective action next time.")

if total_score >= 85:
    st.write("🚀 Excellent work. This mission profile is suitable for advanced operations training.")

    st.divider()
st.header("Animated Mission Playback")

st.divider()
st.header("🎬 Mission Playback")

# Smooth animation timeline
t_anim = np.linspace(0, mission_hours, mission_hours * 10)

angle_anim = t_anim * orbit_speed * 0.25

x_anim = np.cos(angle_anim)
y_anim = np.sin(angle_anim)

sunlight_anim = np.sin(angle_anim) > 0

battery_anim = []
charge_anim = 100

for sun in sunlight_anim:

    if sun:
        charge_anim += solar_charge / 10

    else:
        charge_anim -= battery_drain / 10

    charge_anim = max(0, min(100, charge_anim))
    battery_anim.append(charge_anim)

battery_anim = np.array(battery_anim)

signal_anim = 100 - (
    np.abs(np.sin(angle_anim))
    * signal_noise
)

signal_anim = np.clip(signal_anim, 0, 100)

animation_data = pd.DataFrame({

    "Time":
    np.round(
        t_anim,
        1
    ).astype(str),

    "Battery":
    battery_anim,

    "Signal":
    signal_anim,

    "X":
    x_anim,

    "Y":
    y_anim

})

animation_data["Battery Status"] = np.where(

    animation_data["Battery"] < 20,

    "Critical",

    np.where(

        animation_data["Battery"] < 50,

        "Low",

        "Nominal"

    )

)

mission_events = {
    random.randint(10, 20): "Solar Storm",
    random.randint(25, 40): "Reaction Wheel Fault",
    random.randint(40, 55): "Ground Station Failure",
    random.randint(55, 70): "Extended Eclipse"
}
animated_orbit = px.scatter(

    animation_data,

    x="X",

    y="Y",

    animation_frame="Time",

    color="Battery Status",

    size="Signal",

    range_x=[-1.5, 1.5],

    range_y=[-1.5, 1.5],

    title="Animated CubeSat Orbit"

)

st.plotly_chart(
    animated_orbit,
    use_container_width=True
)

st.header("Mission Objective Progress")

battery_goal = battery[-1] > 25
signal_goal = signal.mean() > 60

st.progress(
    min(
        int(
            battery[-1]
        ),
        100
    )
)

if battery_goal:

    st.success(
        "Battery objective complete"
    )

else:

    st.error(
        "Battery objective failed"
    )

if signal_goal:

    st.success(
        "Signal objective complete"
    )

else:

    st.error(
        "Signal objective failed"
    )

    st.divider()
st.divider()
st.header("🛰️ Ground Control Network")

selected_station = st.selectbox(
    "Active Ground Station",
    ground_stations["Station"]
)

station_data = ground_stations[
    ground_stations["Station"] == selected_station
].iloc[0]

st.write(f"Latitude: {station_data['lat']}")
st.write(f"Longitude: {station_data['lon']}")

if average_signal > 80:
    st.success("Excellent communication link")
elif average_signal > 60:
    st.warning("Moderate communication quality")
else:
    st.error("Poor communication quality")

contact_time = int(average_signal * 0.8)

st.metric(
    "Estimated Contact Time",
    f"{contact_time} min/orbit"
)
st.header("🕒 Mission Timeline Playback")

timeline_hour = st.slider(
    "Mission Hour",
    0,
    mission_hours,
    0
)

st.divider()
st.header("Mission Log")
mission_log = []
mission_log.append("hour 0: launch succesful. Systems nominal.")
for hour, event_name in mission_events.items():
    if hour <= timeline_hour:
        mission_log.append(f"hour {hour}: {event_name} detected.")
for log in sorted(mission_log):
    st.write(log)

battery_now = battery[min(timeline_hour, len(battery)-1)]
signal_now = signal[min(timeline_hour, len(signal)-1)]

st.metric("Current Battery", f"{battery_now:.0f}%")
st.metric("Current Signal", f"{signal_now:.0f}%")

import random
if timeline_hour == 0:
    st.info("🚀 Launch successful. All systems nominal.")
elif timeline_hour in mission_events:
    current_event = mission_events[timeline_hour]
    st.warning(f"⚠️ Event: {current_event}")
elif timeline_hour >= 72:
    st.success("Good job operative.")

if timeline_hour in [12, 24, 36, 48, 60]:
    timeline_action = st.radio(
        "Mission Response",
        [
            "Do Nothing",
            "Reduce Payload Power",
            "Boost Communications",
            "Enter Safe Mode"
        ],
        key=f"timeline_{timeline_hour}"
    )

    if timeline_action == "Reduce Payload Power":
        st.success("Battery consumption reduced.")

    elif timeline_action == "Boost Communications":
        st.success("Signal improved.")

    elif timeline_action == "Enter Safe Mode":
        st.success("Satellite protected.")

        st.divider()
st.header("🌍 Animated Earth Orbit View")

earth_x = [0]
earth_y = [0]

orbit_frames = []

for i in range(len(t)):
    status = "Nominal"

    if battery[i] < 20:
        status = "Critical"
    elif battery[i] < 50:
        status = "Low"

    orbit_frames.append(
        go.Frame(
            data=[
                go.Scatter(
                    x=[0],
                    y=[0],
                    mode="markers",
                    marker=dict(size=80),
                    name="Earth"
                ),
                go.Scatter(
                    x=[x[i]],
                    y=[y[i]],
                    mode="markers",
                    marker=dict(size=18),
                    name=f"CubeSat | Battery: {battery[i]:.0f}% | Signal: {signal[i]:.0f}%"
                )
            ],
            name=str(i)
        )
    )

fig_earth = go.Figure(
    data=[
        go.Scatter(
            x=[0],
            y=[0],
            mode="markers",
            marker=dict(size=80),
            name="Earth"
        ),
        go.Scatter(
            x=[x[0]],
            y=[y[0]],
            mode="markers",
            marker=dict(size=18),
            name="CubeSat"
        ),
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name="Orbit Path"
        )
    ],
    frames=orbit_frames
)

fig_earth.update_layout(
    title="CubeSat Orbiting Earth",
    xaxis=dict(range=[-1.5, 1.5]),
    yaxis=dict(range=[-1.5, 1.5]),
    height=600,
    updatemenus=[
        dict(
            type="buttons",
            buttons=[
                dict(
                    label="Play Orbit",
                    method="animate",
                    args=[
                        None,
                        {
                            "frame": {"duration": 80, "redraw": True},
                            "fromcurrent": True
                        }
                    ]
                )
            ]
        )
    ]
)

st.plotly_chart(fig_earth, use_container_width=True)
