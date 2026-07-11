import fs from 'fs';
import path from 'path';

export class ScreenshotManager {
    constructor(options = {}, logger) {
        this.enabled = options.enabled ?? true;
        this.outputDir = options.path || './screenshots';
        this.logger = logger;

        if (this.enabled) {
            fs.mkdirSync(path.resolve(this.outputDir), { recursive: true });
        }
    }

    async capture(page, name = '') {
        if (!this.enabled || !page) return null;

        const filename = `${name || 'capture'}-${Date.now()}.png`;
        const filepath = path.resolve(this.outputDir, filename);

        await page.screenshot({ path: filepath, fullPage: true });
        this.logger?.info(`Screenshot disimpan: ${filepath}`);
        return filepath;
    }

    async captureOnError(page, error) {
        const filepath = await this.capture(page, 'error');
        this.logger?.error(`Screenshot error (${error.message}): ${filepath}`);
        return filepath;
    }
}
