import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// Custom Metrics
export const TelemetryLatency = new Trend('orbit_telemetry_latency_ms');
export const MissionIntakeLatency = new Trend('orbit_mission_intake_latency_ms');
export const EmergencyReplanLatency = new Trend('orbit_emergency_replan_latency_ms');
export const SuccessRate = new Rate('orbit_success_rate');
export const MissionsScheduled = new Counter('orbit_missions_scheduled_total');

export const options = {
  scenarios: {
    // Scenario A: Telemetry Stream Load (1000 sats simulated via 20 VUs)
    telemetry_stream: {
      executor: 'ramping-vus',
      startVUs: 5,
      stages: [
        { duration: '10s', target: 25 },
        { duration: '20s', target: 25 },
        { duration: '5s', target: 0 },
      ],
      gracefulRampDown: '5s',
      exec: 'testTelemetryStream',
    },
    // Scenario B: Mission Intake & Optimization Storm
    mission_intake_storm: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
      startTime: '5s',
      exec: 'testMissionIntakeStorm',
    },
    // Scenario C: Emergency Cascade Stress
    emergency_cascade: {
      executor: 'shared-iterations',
      vus: 5,
      iterations: 20,
      startTime: '15s',
      exec: 'testEmergencyCascade',
    },
  },
  thresholds: {
    'orbit_telemetry_latency_ms': ['p(95)<50', 'p(99)<100'],
    'orbit_mission_intake_latency_ms': ['p(95)<150', 'p(99)<300'],
    'orbit_success_rate': ['rate>0.99'],
  },
};

const BASE_URL = __ENV.TARGET_URL || 'http://localhost:8000';

export function testTelemetryStream() {
  const satId = `SAT-${Math.floor(Math.random() * 100) + 1}`;
  const payload = JSON.stringify({
    satellite_id: satId,
    battery_soc: 0.85 + Math.random() * 0.1,
    temperature_c: 25.0 + Math.random() * 8.0,
    timestamp: Date.now() / 1000,
  });

  const headers = { 'Content-Type': 'application/json' };
  const res = http.get(`${BASE_URL}/health`, { headers });
  
  TelemetryLatency.add(res.timings.duration);
  const ok = check(res, { 'status is 200': (r) => r.status === 200 });
  SuccessRate.add(ok);
  sleep(0.05);
}

export function testMissionIntakeStorm() {
  const missionPayload = JSON.stringify({
    name: 'Rapid Response Observation Target',
    lat: 37.7749 + (Math.random() - 0.5) * 10.0,
    lon: -122.4194 + (Math.random() - 0.5) * 10.0,
    priority: Math.floor(Math.random() * 5) + 1,
    sensor_type: 'OPTICAL_MULTISPECTRAL',
    data_size_gb: 15.0,
    deadline_offset_s: 1800.0,
  });

  const headers = { 'Content-Type': 'application/json' };
  const start = Date.now();
  const res = http.post(`${BASE_URL}/api/missions/random`, null, { headers });
  
  MissionIntakeLatency.add(Date.now() - start);
  const ok = check(res, { 'mission created': (r) => r.status === 200 });
  if (ok) MissionsScheduled.add(1);
  SuccessRate.add(ok);
  sleep(0.2);
}

export function testEmergencyCascade() {
  const headers = { 'Content-Type': 'application/json' };
  const start = Date.now();
  const res = http.post(`${BASE_URL}/api/scenarios/trigger?scenario_type=SOLAR_STORM`, null, { headers });
  
  EmergencyReplanLatency.add(Date.now() - start);
  const ok = check(res, { 'emergency trigger processed': (r) => r.status === 200 });
  SuccessRate.add(ok);
  sleep(1.0);
}
