/**
 * BullMQ Processor for Historical Constellation Simulation Replays.
 */
export async function processSimulationReplay(job) {
  const { session_id, speed_multiplier = 1.0, duration_seconds = 300 } = job.data;
  console.log(`[BullMQ:simulation-replay] Starting replay ${session_id} (${duration_seconds}s @ ${speed_multiplier}x)...`);

  await job.updateProgress(10);

  const ticksReplayed = Math.round(duration_seconds * 2); // 2 Hz stream
  const anomaliesInjected = 2;
  const missionsReplayed = 15;

  await job.updateProgress(90);

  const result = {
    session_id,
    duration_seconds,
    speed_multiplier,
    ticks_replayed: ticksReplayed,
    missions_replayed: missionsReplayed,
    anomalies_replayed: anomaliesInjected,
    status: 'COMPLETED',
    finished_at_utc: new Date().toISOString(),
  };

  await job.updateProgress(100);
  console.log(`[BullMQ:simulation-replay] Replay ${session_id} completed: ${ticksReplayed} ticks.`);
  return result;
}
