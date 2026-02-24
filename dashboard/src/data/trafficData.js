// ==============================================================================
// Traffic Data — Embedded from CSV files and AI config
// ==============================================================================

// From signal_results.csv
export const experimentData = [
  { exp: 1, lane1: 128, lane2: 132, lane3: 33, lane4: 33, total: 326, manual: 270 },
  { exp: 2, lane1: 116, lane2: 136, lane3: 31, lane4: 29, total: 312, manual: 257 },
  { exp: 3, lane1: 142, lane2: 92, lane3: 30, lane4: 26, total: 290, manual: 255 },
  { exp: 4, lane1: 125, lane2: 118, lane3: 34, lane4: 27, total: 304, manual: 280 },
  { exp: 5, lane1: 126, lane2: 140, lane3: 40, lane4: 21, total: 327, manual: 255 },
  { exp: 6, lane1: 132, lane2: 123, lane3: 25, lane4: 31, total: 311, manual: 240 },
  { exp: 7, lane1: 126, lane2: 121, lane3: 32, lane4: 36, total: 315, manual: 260 },
  { exp: 8, lane1: 121, lane2: 118, lane3: 27, lane4: 32, total: 298, manual: 255 },
  { exp: 9, lane1: 126, lane2: 124, lane3: 34, lane4: 28, total: 312, manual: 257 },
  { exp: 10, lane1: 125, lane2: 123, lane3: 33, lane4: 27, total: 308, manual: 261 },
  { exp: 11, lane1: 132, lane2: 103, lane3: 25, lane4: 30, total: 290, manual: 269 },
  { exp: 12, lane1: 131, lane2: 102, lane3: 24, lane4: 29, total: 296, manual: 269 },
];

// Sampled vehicle counts from data/vehicle_counts.csv (every ~1s)
export const vehicleTimeSeries = [
  { time: 0, count: 3 }, { time: 1, count: 2 }, { time: 2, count: 2 },
  { time: 3, count: 2 }, { time: 4, count: 3 }, { time: 5, count: 3 },
  { time: 6, count: 4 }, { time: 7, count: 5 }, { time: 8, count: 4 },
  { time: 9, count: 4 }, { time: 10, count: 4 }, { time: 11, count: 5 },
  { time: 12, count: 5 }, { time: 13, count: 4 }, { time: 14, count: 4 },
  { time: 15, count: 3 }, { time: 16, count: 3 }, { time: 17, count: 3 },
  { time: 18, count: 3 }, { time: 19, count: 3 }, { time: 20, count: 3 },
  { time: 21, count: 3 }, { time: 22, count: 2 }, { time: 23, count: 2 },
  { time: 24, count: 3 }, { time: 25, count: 3 }, { time: 26, count: 2 },
  { time: 27, count: 2 }, { time: 28, count: 3 }, { time: 29, count: 4 },
  { time: 30, count: 5 }, { time: 31, count: 4 }, { time: 32, count: 3 },
  { time: 33, count: 4 }, { time: 34, count: 5 }, { time: 35, count: 6 },
  { time: 36, count: 5 }, { time: 37, count: 4 }, { time: 38, count: 3 },
  { time: 39, count: 4 }, { time: 40, count: 5 }, { time: 41, count: 6 },
  { time: 42, count: 5 }, { time: 43, count: 4 }, { time: 44, count: 3 },
  { time: 45, count: 3 }, { time: 46, count: 4 }, { time: 47, count: 5 },
  { time: 48, count: 4 }, { time: 49, count: 3 }, { time: 50, count: 3 },
  { time: 51, count: 4 }, { time: 52, count: 5 }, { time: 53, count: 4 },
  { time: 54, count: 3 }, { time: 55, count: 4 }, { time: 56, count: 5 },
  { time: 57, count: 6 }, { time: 58, count: 5 }, { time: 59, count: 4 },
  { time: 60, count: 3 }, { time: 61, count: 4 }, { time: 62, count: 5 },
  { time: 63, count: 6 }, { time: 64, count: 7 }, { time: 65, count: 6 },
  { time: 66, count: 5 }, { time: 67, count: 4 }, { time: 68, count: 3 },
  { time: 69, count: 4 }, { time: 70, count: 5 }, { time: 71, count: 4 },
  { time: 72, count: 3 }, { time: 73, count: 4 }, { time: 74, count: 5 },
  { time: 75, count: 4 }, { time: 76, count: 3 }, { time: 77, count: 3 },
  { time: 78, count: 4 }, { time: 79, count: 5 }, { time: 80, count: 6 },
];

// Add rolling averages
export const vehicleTimeSeriesWithAvg = vehicleTimeSeries.map((d, i, arr) => {
  const window10 = arr.slice(Math.max(0, i - 9), i + 1);
  const window20 = arr.slice(Math.max(0, i - 19), i + 1);
  return {
    ...d,
    avg10: +(window10.reduce((s, v) => s + v.count, 0) / window10.length).toFixed(1),
    avg20: +(window20.reduce((s, v) => s + v.count, 0) / window20.length).toFixed(1),
  };
});

// Count distribution for histogram
export const countDistribution = (() => {
  const freq = {};
  vehicleTimeSeries.forEach(d => {
    freq[d.count] = (freq[d.count] || 0) + 1;
  });
  return Object.entries(freq)
    .map(([count, frequency]) => ({ count: +count, frequency }))
    .sort((a, b) => a.count - b.count);
})();

// AI metrics per direction (synthetic, based on ai_config.py constants)
export const directions = ['Right', 'Down', 'Left', 'Up'];
export const directionColors = {
  Right: '#FB923C',
  Down: '#4A8CFF',
  Left: '#34D399',
  Up: '#FBBF24',
};

export const aiMetricsPerDirection = [
  { direction: 'Right', aiScore: 12.4, waitTime: 3.2, queueLength: 8, co2: 18.5, throughput: 42 },
  { direction: 'Down', aiScore: 9.8, waitTime: 2.1, queueLength: 5, co2: 12.3, throughput: 38 },
  { direction: 'Left', aiScore: 7.2, waitTime: 1.5, queueLength: 3, co2: 8.7, throughput: 22 },
  { direction: 'Up', aiScore: 6.5, waitTime: 1.8, queueLength: 4, co2: 9.1, throughput: 25 },
];

// AI score trends over 20 cycles
export const aiScoreTrends = Array.from({ length: 20 }, (_, i) => ({
  cycle: i + 1,
  Right: +(8 + Math.sin(i * 0.5) * 4 + Math.random() * 2).toFixed(1),
  Down: +(6 + Math.cos(i * 0.4) * 3 + Math.random() * 1.5).toFixed(1),
  Left: +(5 + Math.sin(i * 0.3 + 1) * 2.5 + Math.random() * 1).toFixed(1),
  Up: +(4.5 + Math.cos(i * 0.6 + 2) * 2 + Math.random() * 1.2).toFixed(1),
}));

// CO2 trends over time
export const co2Trends = Array.from({ length: 20 }, (_, i) => ({
  cycle: i + 1,
  Right: +(15 + Math.sin(i * 0.4) * 8 + Math.random() * 3).toFixed(1),
  Down: +(10 + Math.cos(i * 0.3) * 5 + Math.random() * 2).toFixed(1),
  Left: +(7 + Math.sin(i * 0.5 + 1) * 4 + Math.random() * 1.5).toFixed(1),
  Up: +(8 + Math.cos(i * 0.4 + 2) * 3.5 + Math.random() * 2).toFixed(1),
}));

// AI weights from ai_config.py (for radar chart)
export const aiWeights = [
  { factor: 'Vehicle Count', weight: 0.4, fullMark: 1 },
  { factor: 'Wait Time', weight: 0.3, fullMark: 1 },
  { factor: 'Queue Length', weight: 0.2, fullMark: 1 },
  { factor: 'Throughput', weight: 0.1, fullMark: 1 },
  { factor: 'Pollution', weight: 0.15, fullMark: 1 },
];

// Emission rates
export const emissionRates = [
  { type: 'Car', rate: 2.3, color: '#4A8CFF' },
  { type: 'Bus', rate: 5.0, color: '#FF825A' },
  { type: 'Truck', rate: 6.0, color: '#FF4646' },
  { type: 'Rickshaw', rate: 1.0, color: '#32D27A' },
  { type: 'Bike', rate: 0.5, color: '#FFC83D' },
  { type: 'Ambulance', rate: 4.0, color: '#E040FB' },
];

// Signal timing config
export const signalConfig = {
  defaultRed: 150,
  defaultYellow: 5,
  defaultGreen: 20,
  defaultMinimum: 10,
  defaultMaximum: 60,
  pollutionThreshold: 50.0,
};

// KPI calculations
export const kpis = (() => {
  const totalExperiments = experimentData.length;
  const avgYoloTotal = +(experimentData.reduce((s, d) => s + d.total, 0) / totalExperiments).toFixed(0);
  const avgManualTotal = +(experimentData.reduce((s, d) => s + d.manual, 0) / totalExperiments).toFixed(0);
  const improvement = +(((avgYoloTotal - avgManualTotal) / avgManualTotal) * 100).toFixed(1);
  const bestExp = experimentData.reduce((a, b) => a.total > b.total ? a : b);
  const avgThroughput = +(avgYoloTotal / 300).toFixed(2); // 300s sim time
  const totalAQI = 12.2; // synthetic average
  const syncScore = 72; // synthetic junction sync score

  return {
    totalExperiments,
    avgYoloTotal,
    avgManualTotal,
    improvement,
    bestExp: bestExp.exp,
    bestExpTotal: bestExp.total,
    avgThroughput,
    totalAQI,
    syncScore,
  };
})();
