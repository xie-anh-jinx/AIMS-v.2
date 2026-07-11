/**
 * HealthCheck — Reports system readiness status.
 */
export class HealthCheck {
    constructor(connector) {
        this.connector = connector;
    }

    async check() {
        const report = {
            timestamp: new Date().toISOString(),
            status: 'healthy',
            checks: {}
        };

        // State check
        const state = this.connector.stateManager?.getState() || 'unknown';
        report.checks.state = { status: state === 'IDLE' || state === 'DONE' ? 'ok' : 'busy', value: state };

        // Cache check
        const cacheStats = this.connector.cache?.stats() || {};
        report.checks.cache = { status: 'ok', ...cacheStats };

        // Provider check
        const providers = this.connector.providerRegistry?.list() || [];
        report.checks.providers = { status: providers.length > 0 ? 'ok' : 'warn', count: providers.length };

        // Metrics check
        const metrics = this.connector.metrics?.getAll() || {};
        report.checks.metrics = metrics;

        // Overall
        const hasWarning = Object.values(report.checks).some(c => c.status === 'warn');
        const hasError = Object.values(report.checks).some(c => c.status === 'error');
        if (hasError) report.status = 'unhealthy';
        else if (hasWarning) report.status = 'degraded';

        return report;
    }
}
