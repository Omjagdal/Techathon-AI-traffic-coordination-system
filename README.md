
---

# 🚦 AI-Powered Traffic Signal Simulation
This project uses YOLO-based vehicle detection and LSTM-based traffic prediction to optimize traffic light control. The simulation dynamically adjusts signal timings based on real-time vehicle counts from video feeds.
## 📌 Problem Statement  
Traditional traffic signals operate on fixed timers, leading to inefficiencies such as unnecessary waiting times and congestion. This project aims to develop an **AI-powered adaptive traffic management system** that dynamically adjusts signal timings based on real-time traffic conditions detected using YOLOv8.  

---

## 🔧 **Implementation Details**  
### **1️⃣ Vehicle Detection Module**  
- Uses **YOLOv8** to detect vehicles in live traffic feeds.  
- Classifies detected vehicles into **cars, bikes, buses, trucks, and rickshaws**.  

### **2️⃣ Signal Switching Algorithm**  
- Dynamically adjusts **red, yellow, and green signal durations**.  
- Takes into account:  
  ✅ **Vehicle count per lane**  
  ✅ **Vehicle type (car, bus, etc.)**  
  ✅ **Average vehicle speed**  

### **3️⃣ Simulation Module**  
- Built using **[Pygame](https://www.pygame.org/news)** to simulate:  
  ✅ **Traffic signals**  
  ✅ **Vehicle movements**  
  ✅ **Signal timing adjustments**  

For more details on the **object detection model**, **algorithm**, and **simulation**, refer to the documentation.  

---

## 🚀 **Features**  
✅ **YOLOv8-Based Vehicle Detection** – Detects vehicles from real-time traffic video feeds.  
✅ **LSTM-Based Traffic Prediction** – Forecasts future congestion trends.  
✅ **Automated Traffic Signal Control** – Adjusts green light durations dynamically.  
✅ **Multiple Simulation Runs** – Runs the simulation multiple times and saves data.  
✅ **Excel Report Output** – Stores final traffic analysis results.  

---

## 🛠 **How It Works**  
1. **Vehicle Detection:** YOLOv8 detects vehicles from live video feeds.  
2. **Traffic Data Processing:** The detected vehicle counts are analyzed.  
3. **Signal Adjustment:** Green light durations are set based on vehicle density.  
4. **Prediction with LSTM:** Future congestion trends are forecasted.  
5. **Simulation Execution:** The model is tested through multiple runs.  
6. **Result Storage:** Data is saved in an **Excel sheet** for further analysis.
[![Traffic Simulation Demo](https://github.com/Zem-0/AI-Powered-Smart-Traffic-Management-System/blob/main/ezgif.com-video-to-gif-converter.gif)]

   
  


---

## 📊 Demo and Results
[![Traffic Simulation Demo](https://github.com/Zem-0/AI-Powered-Smart-Traffic-Management-System/blob/main/ezgif.com-speed.gif)]

- **Real-time traffic simulation with vehicle movements**  
- **Signal timing adjustments based on YOLO vehicle detection**  
- **Excel report (`simulation_results.xlsx`) summarizing results**

![Traffic Simulation](https://github.com/Zem-0/AI-Powered-Smart-Traffic-Management-System/blob/main/Screenshot%202025-02-11%20120803.png)



---

## 📂 **Project Structure**  
```
├── simulation.py          # Main traffic simulation logic  
├── run_simulation.py      # Runs multiple simulations & saves results  
├── signal_results.csv     # Stores vehicle detection results per signal  
├── simulation_results.xlsx # Aggregated results from multiple runs  
├── README.md              # Project documentation  
```

---

## 🛠 **Installation**  
### **1️⃣ Clone the Repository**  
```sh
git clone https://github.com/your-username/traffic-simulation.git
cd traffic-simulation
```
### **2️⃣ Install Dependencies**  
```sh
pip install -r requirements.txt
```

---

## ▶️ **Running the Project**  
### **Run a Single Simulation**  
```sh
python simulation.py
```
### **Run Multiple Simulations (15 runs, save results to Excel)**  
```sh
python run_simulation.py
```

---

## 🤖 **Future Enhancements**  
🔹 **Integrate live traffic camera feeds** for real-world deployment.  
🔹 **Implement Reinforcement Learning (RL)** for improved signal optimization.  
🔹 **Enhance visualization with a web-based dashboard**.  

---

## 📜 **License**  
This project is open-source under the **MIT License**.  

---

## 🤝 **Contributing**  
Pull requests are welcome! Feel free to **improve the simulation logic** or **add new features**.  

---

## 📧 **Contact**  
For questions or contributions, contact **parinith99@gmail.com** or open an issue on GitHub.  

---

🚦 **Optimizing Traffic, One Signal at a Time!** 🚦  

---

