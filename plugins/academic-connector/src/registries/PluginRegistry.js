/**
 * PluginRegistry — Supports loading additional third-party modules.
 */
export class PluginRegistry {
    constructor(logger) {
        this.plugins = new Map();
        this.logger = logger;
    }

    register(name, pluginInstance) {
        this.plugins.set(name, pluginInstance);
        this.logger?.info(`Plugin registered: ${name}`);
    }

    get(name) {
        return this.plugins.get(name) || null;
    }

    list() {
        return [...this.plugins.keys()];
    }

    async initAll(context) {
        for (const [name, plugin] of this.plugins) {
            if (typeof plugin.init === 'function') {
                this.logger?.info(`Initializing plugin: ${name}`);
                await plugin.init(context);
            }
        }
    }
}
