/**
 * Metrics — Collects runtime telemetry from SDK operations.
 */
export class Metrics {
    constructor() {
        this._counters = {};
        this._timers = {};
    }

    increment(name, value = 1) {
        this._counters[name] = (this._counters[name] || 0) + value;
    }

    startTimer(name) {
        this._timers[name] = Date.now();
    }

    endTimer(name) {
        if (!this._timers[name]) return 0;
        const elapsed = Date.now() - this._timers[name];
        delete this._timers[name];
        this.increment(`${name}_total_ms`, elapsed);
        return elapsed;
    }

    getAll() {
        return {
            counters: { ...this._counters },
            activeTimers: Object.keys(this._timers)
        };
    }

    reset() {
        this._counters = {};
        this._timers = {};
    }
}
