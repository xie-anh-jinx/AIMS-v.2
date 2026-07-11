import fs from 'fs';
import path from 'path';
import YAML from 'yaml';

/**
 * ProviderRegistry — Auto-loads provider configs from providers/ directory.
 */
export class ProviderRegistry {
    constructor(providersDir, logger) {
        this.providersDir = path.resolve(providersDir);
        this.providers = new Map();
        this.logger = logger;
    }

    scan() {
        if (!fs.existsSync(this.providersDir)) {
            this.logger?.warn(`Providers directory not found: ${this.providersDir}`);
            return;
        }

        const dirs = fs.readdirSync(this.providersDir, { withFileTypes: true })
            .filter(d => d.isDirectory())
            .map(d => d.name);

        for (const name of dirs) {
            const providerPath = path.join(this.providersDir, name);
            const configFile = path.join(providerPath, 'config.yml');
            const selectorsFile = path.join(providerPath, 'selectors.yml');
            const mappingFile = path.join(providerPath, 'mapping.yml');

            const provider = { name, path: providerPath };

            if (fs.existsSync(configFile)) {
                provider.config = YAML.parse(fs.readFileSync(configFile, 'utf8'));
            }
            if (fs.existsSync(selectorsFile)) {
                provider.selectors = YAML.parse(fs.readFileSync(selectorsFile, 'utf8'));
            }
            if (fs.existsSync(mappingFile)) {
                provider.mapping = YAML.parse(fs.readFileSync(mappingFile, 'utf8'));
            }

            this.providers.set(name, provider);
            this.logger?.info(`Provider registered: ${name}`);
        }
    }

    get(name) {
        return this.providers.get(name) || null;
    }

    list() {
        return [...this.providers.keys()];
    }

    has(name) {
        return this.providers.has(name);
    }
}
