import test from 'node:test';
import assert from 'node:assert/strict';
import { processTleRefresh } from '../src/processors/tle.processor.js';
import { processMissionReport } from '../src/processors/report.processor.js';
import { processBenchmarkRun } from '../src/processors/benchmark.processor.js';
import { processAnomalyReport } from '../src/processors/anomaly.processor.js';
import { processSimulationReplay } from '../src/processors/replay.processor.js';

// Mock job helper
function createMockJob(id, data) {
  return {
    id,
    data,
    updateProgress: async () => {},
  };
}

test('processTleRefresh correctly updates constellation TLE elements', async () => {
  const job = createMockJob('job-tle-1', { group: 'starlink', count: 12 });
  const result = await processTleRefresh(job);

  assert.equal(result.job_id, 'job-tle-1');
  assert.equal(result.satellites_synced, 12);
  assert.equal(result.group, 'starlink');
  assert.ok(result.sample.satellite_id.startsWith('SAT-'));
});

test('processMissionReport generates complete executive mission metrics and hash', async () => {
  const job = createMockJob('job-rep-1', { mission_id: 'M-500', requested_by: 'operator-1' });
  const result = await processMissionReport(job);

  assert.equal(result.mission_id, 'M-500');
  assert.equal(result.summary.status, 'SUCCESS');
  assert.equal(result.summary.completion_rate_pct, 100.0);
  assert.ok(result.verification_hash.startsWith('sha256-'));
});

test('processBenchmarkRun calculates latency percentiles and throughput', async () => {
  const job = createMockJob('job-bench-1', { constellation_size: 100, num_missions: 50 });
  const result = await processBenchmarkRun(job);

  assert.equal(result.constellation_size, 100);
  assert.ok(result.metrics.p50_latency_ms > 0);
  assert.ok(result.metrics.throughput_req_per_sec > 0);
  assert.equal(result.metrics.success_rate_pct, 99.8);
});

test('processAnomalyReport compiles root cause analysis and SHAP feature attribution', async () => {
  const job = createMockJob('job-anom-1', { satellite_id: 'SAT-008', anomaly_type: 'BATTERY_THERMAL_OVERHEAT', severity: 'CRITICAL' });
  const result = await processAnomalyReport(job);

  assert.equal(result.satellite_id, 'SAT-008');
  assert.equal(result.root_cause_analysis.subsystem, 'EPS_POWER');
  assert.equal(result.root_cause_analysis.recommendation, 'TRIGGER_DYNAMIC_EMERGENCY_REPLAN');
});

test('processSimulationReplay calculates replayed ticks and status', async () => {
  const job = createMockJob('job-rep-1', { session_id: 'SES-99', duration_seconds: 60 });
  const result = await processSimulationReplay(job);

  assert.equal(result.session_id, 'SES-99');
  assert.equal(result.ticks_replayed, 120);
  assert.equal(result.status, 'COMPLETED');
});
