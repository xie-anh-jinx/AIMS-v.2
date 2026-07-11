/**
 * IntelligentScheduler — Replaces simplistic cron with self-healing, queuing mechanism.
 */
export class IntelligentScheduler {
    constructor(logger) {
        this.logger = logger;
        this.priorityQueue = [];
        this.retryQueue = [];
        this.deadLetterQueue = [];
        this.isRunning = false;
    }

    enqueue(accountTask) {
        accountTask.attempts = 0;
        this.priorityQueue.push(accountTask);
        this.logger?.debug(`[Scheduler] Account ${accountTask.id} added to Priority Queue.`);
    }

    async start(taskExecutorCallback) {
        this.isRunning = true;
        this.logger?.info('[Scheduler] Main Loop started.');

        while (this.isRunning && (this.priorityQueue.length > 0 || this.retryQueue.length > 0)) {
            // Process Priority Queue first
            if (this.priorityQueue.length > 0) {
                const task = this.priorityQueue.shift();
                await this._safeExecute(task, taskExecutorCallback);
                continue;
            }

            // Retry Queue with simulated delay backoff
            if (this.retryQueue.length > 0) {
                const task = this.retryQueue.shift();
                task.attempts += 1;
                this.logger?.warn(`[Scheduler] Retrying Task for ${task.id} (Attempt: ${task.attempts})`);
                await this._safeExecute(task, taskExecutorCallback);
            }
        }
        
        this.logger?.info('[Scheduler] All queues drained. Dead Letter Queue count: ' + this.deadLetterQueue.length);
        this.isRunning = false;
    }

    async _safeExecute(task, executor) {
        try {
            await executor(task);
            this.logger?.info(`[Scheduler] Task for ${task.id} completed successfully.`);
        } catch (error) {
            this.logger?.error(`[Scheduler] Task for ${task.id} failed: ${error.message}`);
            
            if (task.attempts < 3) {
                this.retryQueue.push(task);
            } else {
                this.logger?.audit(`[Scheduler] Account ${task.id} moved to DEAD LETTER QUEUE (Quarantined) - Last Error: ${error.message}`);
                this.deadLetterQueue.push(task);
            }
        }
    }
}
