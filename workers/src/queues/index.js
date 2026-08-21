import { Queue } from 'bullmq';
import { config } from '../config.js';

export const QUEUE_NAMES = {
  TLE_REFRESH: 'tle-refresh',
  MISSION_REPORT: 'mission-report',
  BENCHMARK_RUN: 'benchmark-run',
  ANOMALY_REPORT: 'anomaly-report',
  SIMULATION_REPLAY: 'simulation-replay',
};

export const queues = {
  tleRefresh: new Queue(QUEUE_NAMES.TLE_REFRESH, { connection: config.redis, defaultJobOptions: config.defaultJobOptions }),
  missionReport: new Queue(QUEUE_NAMES.MISSION_REPORT, { connection: config.redis, defaultJobOptions: config.defaultJobOptions }),
  benchmarkRun: new Queue(QUEUE_NAMES.BENCHMARK_RUN, { connection: config.redis, defaultJobOptions: config.defaultJobOptions }),
  anomalyReport: new Queue(QUEUE_NAMES.ANOMALY_REPORT, { connection: config.redis, defaultJobOptions: config.defaultJobOptions }),
  simulationReplay: new Queue(QUEUE_NAMES.SIMULATION_REPLAY, { connection: config.redis, defaultJobOptions: config.defaultJobOptions }),
};

export async function addTleRefreshJob(data, jobId) {
  return queues.tleRefresh.add('tle-refresh-job', data, { jobId });
}

export async function addMissionReportJob(data, jobId) {
  return queues.missionReport.add('mission-report-job', data, { jobId });
}

export async function addBenchmarkJob(data, jobId) {
  return queues.benchmarkRun.add('benchmark-run-job', data, { jobId });
}

export async function addAnomalyReportJob(data, jobId) {
  return queues.anomalyReport.add('anomaly-report-job', data, { jobId });
}

export async function addSimulationReplayJob(data, jobId) {
  return queues.simulationReplay.add('simulation-replay-job', data, { jobId });
}
