import http from 'http';
import { Worker } from 'bullmq';
import { config } from './config.js';
import { QUEUE_NAMES, queues } from './queues/index.js';
import { processTleRefresh } from './processors/tle.processor.js';
import { processMissionReport } from './processors/report.processor.js';
import { processBenchmarkRun } from './processors/benchmark.processor.js';
import { processAnomalyReport } from './processors/anomaly.processor.js';
import { processSimulationReplay } from './processors/replay.processor.js';

console.log('='.repeat(65));
console.log('   ORBIT-X BULLMQ PRODUCTION BACKGROUND WORKER SERVICE');
console.log('='.repeat(65));

// Initialize Workers
const workers = [
  new Worker(QUEUE_NAMES.TLE_REFRESH, processTleRefresh, {
    connection: config.redis,
    concurrency: 5,
  }),
  new Worker(QUEUE_NAMES.MISSION_REPORT, processMissionReport, {
    connection: config.redis,
    concurrency: 10,
  }),
  new Worker(QUEUE_NAMES.BENCHMARK_RUN, processBenchmarkRun, {
    connection: config.redis,
    concurrency: 2,
  }),
  new Worker(QUEUE_NAMES.ANOMALY_REPORT, processAnomalyReport, {
    connection: config.redis,
    concurrency: 10,
  }),
  new Worker(QUEUE_NAMES.SIMULATION_REPLAY, processSimulationReplay, {
    connection: config.redis,
    concurrency: 3,
  }),
];

let jobsCompleted = 0;
let jobsFailed = 0;

workers.forEach((worker) => {
  worker.on('completed', (job) => {
    jobsCompleted++;
    console.log(`[Worker:${worker.name}] Job ${job.id} completed successfully.`);
  });

  worker.on('failed', (job, err) => {
    jobsFailed++;
    console.error(`[Worker:${worker.name}] Job ${job?.id} failed: ${err.message}`);
  });

  worker.on('error', (err) => {
    // Gracefully report redis connection errors during local dev/tests
    if (err.message.includes('ECONNREFUSED')) {
      // Quiet down repeat offline logs
    } else {
      console.warn(`[Worker:${worker.name}] Warning: ${err.message}`);
    }
  });
});

// Built-in HTTP Health and Management Server
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);

  res.setHeader('Content-Type', 'application/json');

  if (url.pathname === '/health' || url.pathname === '/ready') {
    res.writeHead(200);
    res.end(
      JSON.stringify({
        status: 'UP',
        service: 'orbitx-workers',
        uptime_seconds: process.uptime(),
        queues: Object.keys(QUEUE_NAMES).length,
        jobs_completed: jobsCompleted,
        jobs_failed: jobsFailed,
      })
    );
    return;
  }

  if (url.pathname === '/metrics') {
    res.writeHead(200);
    res.end(
      JSON.stringify({
        bullmq_jobs_completed_total: jobsCompleted,
        bullmq_jobs_failed_total: jobsFailed,
        active_workers: workers.length,
      })
    );
    return;
  }

  if (url.pathname === '/submit' && req.method === 'POST') {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', async () => {
      try {
        const payload = JSON.parse(body || '{}');
        const { queue_name, data, job_id } = payload;
        const targetQueue = Object.values(queues).find((q) => q.name === queue_name);
        if (!targetQueue) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: `Queue '${queue_name}' not found.` }));
          return;
        }
        const job = await targetQueue.add(`${queue_name}-job`, data, { jobId: job_id });
        res.writeHead(202);
        res.end(JSON.stringify({ status: 'ENQUEUED', job_id: job.id, queue: queue_name }));
      } catch (err) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Endpoint Not Found' }));
});

const PORT = config.server.port;
server.listen(PORT, () => {
  console.log(`Worker service HTTP health server listening on port ${PORT}`);
});

// Graceful Shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received: Shutting down BullMQ workers...');
  await Promise.all(workers.map((w) => w.close()));
  server.close();
  process.exit(0);
});

export { server, workers, queues };
