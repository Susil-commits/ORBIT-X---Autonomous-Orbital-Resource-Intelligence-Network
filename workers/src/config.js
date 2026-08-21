import dotenv from 'dotenv';
dotenv.config();

export const config = {
  redis: {
    host: process.env.REDIS_HOST || '127.0.0.1',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD || undefined,
    maxRetriesPerRequest: null, // Required by BullMQ
  },
  server: {
    port: parseInt(process.env.WORKER_PORT || '4000', 10),
  },
  defaultJobOptions: {
    attempts: 5,
    backoff: {
      type: 'exponential',
      delay: 1000,
    },
    removeOnComplete: {
      count: 200,
      age: 3600, // 1 hour
    },
    removeOnFail: {
      count: 500,
      age: 86400, // 24 hours (DLQ retention)
    },
  },
};
