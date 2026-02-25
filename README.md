
---

# 🚦 AI-Powered Smart Traffic Management System

An intelligent traffic simulation that uses **YOLOv8** vehicle detection, **LSTM** traffic prediction, and multiple AI modules to dynamically optimize signal timings — all visualized through a **Pygame simulation** and a **React dashboard**.

---

## 📌 Problem Statement

Traditional traffic signals operate on fixed timers, causing unnecessary waiting and congestion. This project develops an **AI-powered adaptive traffic management system** that dynamically adjusts signal timings based on real-time traffic conditions.

---

## 🚀 Features

✅ **YOLOv8 Vehicle Detection** — Detects cars, bikes, buses, trucks, rickshaws, and ambulances from video feeds  
✅ **LSTM Traffic Prediction** — Forecasts future congestion trends  
✅ **Adaptive Signal Timing** — AI adjusts green light durations based on vehicle density  
✅ **Emergency Green Corridor** — Priority routing for ambulances with automatic signal preemption  
✅ **Pollution-Aware Optimization** — Factors in AQI for signal decisions  
✅ **Junction Coordination** — Syncs adjacent intersections for traffic flow  
✅ **Real-time Dashboard** — React-based web dashboard with live traffic metrics  
✅ **Professional Pygame Simulation** — Smooth 60 FPS simulation with AI HUD overlay  

---

## 🔧 AI Modules

| Module | File | Description |
|--------|------|-------------|
| Adaptive Timing | `ai_adaptive_timing.py` | Dynamically adjusts green time based on vehicle count & wait time |
| Green Corridor | `ai_green_corridor.py` | Emergency vehicle priority routing & signal preemption |
| Pollution Aware | `ai_pollution.py` | Integrates AQI data into signal optimization |
| Junction Coordination | `ai_junction_coordination.py` | Synchronizes adjacent intersections |
| AI HUD | `ai_hud.py` | On-screen AI status panel for the simulation |
| Configuration | `ai_config.py` | Centralized AI parameters and thresholds |

---

## 📂 Project Structure

```
AI-Powered-Smart-Traffic-Management-System/
├── simulation.py                  # Main Pygame traffic simulation
├── server.py                      # FastAPI WebSocket backend server
├── app.py                         # Streamlit visualization app
├── stream.py                      # Video stream processing
├── data.py                        # Data handling utilities
├── image_loader.py                # Image loading with Pillow fallback
│
├── ai_adaptive_timing.py          # AI: Adaptive signal timing
├── ai_green_corridor.py           # AI: Emergency green corridor
├── ai_pollution.py                # AI: Pollution-aware optimization
├── ai_junction_coordination.py    # AI: Junction coordination
├── ai_hud.py                      # AI: HUD overlay for simulation
├── ai_config.py                   # AI: Configuration & parameters
│
├── images/                        # Vehicle & signal sprite images
│   ├── right/                     # Right-facing vehicle sprites
│   ├── down/                      # Down-facing vehicle sprites
│   ├── left/                      # Left-facing vehicle sprites
│   ├── up/                        # Up-facing vehicle sprites
│   └── signals/                   # Traffic signal images
│
├── models/                        # ML model weights
│   └── yolov8n.pt
├── yolov5s.pt                     # YOLOv5 model weights
├── traffic_prediction_model.keras # LSTM prediction model
│
├── dashboard/                     # React web dashboard
│   ├── src/
│   │   ├── pages/                 # Dashboard pages
│   │   ├── components/            # Reusable UI components
│   │   ├── hooks/                 # Custom React hooks
│   │   └── data/                  # Static data
│   ├── package.json
│   └── vite.config.js
│
├── data/                          # Traffic data CSVs
├── vids/                          # Sample traffic video feeds
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 🛠 Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/AI-Powered-Smart-Traffic-Management-System.git
cd AI-Powered-Smart-Traffic-Management-System
```

### 2️⃣ Set Up Python Environment
```sh
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 3️⃣ Set Up Dashboard
```sh
cd dashboard
npm install
cd ..
```

---

## ▶️ Running the Project

### Run the Pygame Simulation
```sh
source venv/bin/activate
python3 simulation.py
```
**Keyboard Controls:**
- `1-4` → Spawn ambulance in RIGHT / DOWN / LEFT / UP direction
- `H` → Toggle AI HUD panel

### Run the Backend Server + Dashboard
```sh
# Terminal 1 — Backend
source venv/bin/activate
python3 server.py

# Terminal 2 — Dashboard
cd dashboard
npm run dev
```
Then open **http://localhost:5173** in your browser.

### Run the Streamlit App
```sh
source venv/bin/activate
streamlit run app.py
```

---

## 📊 Demo

![Traffic Simulation](https://github.com/Zem-0/AI-Powered-Smart-Traffic-Management-System/blob/main/ezgif.com-video-to-gif-converter.gif)

![Traffic Simulation](https://github.com/Zem-0/AI-Powered-Smart-Traffic-Management-System/blob/main/ezgif.com-speed.gif)

![Screenshot](https://github.com/Zem-0/AI-Powered-Smart-Traffic-Management-System/blob/main/Screenshot%202025-02-11%20120803.png)

---

## 🤖 Future Enhancements

🔹 Integrate live traffic camera feeds for real-world deployment  
🔹 Implement Reinforcement Learning (RL) for improved signal optimization  
🔹 Add multi-junction simulation with coordinated signal networks  

---

## 📜 License

This project is open-source under the **MIT License**.


---

🚦 **Optimizing Traffic, One Signal at a Time!** 🚦
