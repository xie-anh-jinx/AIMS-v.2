import fs from 'fs';
import path from 'path';

/**
 * CsvAdapter — Parse CSV/Excel dump files from university SFTP/Email exports.
 */
export class CsvAdapter {
    constructor(config, logger) {
        this.config = config;
        this.logger = logger;
    }

    async loadFile(filePath) {
        this.logger?.info(`Loading CSV: ${filePath}`);
        const absolute = path.resolve(filePath);

        if (!fs.existsSync(absolute)) {
            throw new Error(`File not found: ${absolute}`);
        }

        const content = fs.readFileSync(absolute, 'utf8');
        return this._parse(content);
    }

    _parse(csvString) {
        const lines = csvString.trim().split('\n');
        if (lines.length < 2) return [];

        const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/\s+/g, '_'));
        const records = [];

        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const record = {};
            headers.forEach((header, idx) => {
                record[header] = values[idx] || null;
            });
            records.push(record);
        }

        this.logger?.info(`Parsed ${records.length} records from CSV.`);
        return records;
    }

    async loadDirectory(dirPath, pattern = '*.csv') {
        const dir = path.resolve(dirPath);
        const files = fs.readdirSync(dir).filter(f => f.endsWith('.csv'));
        const allRecords = [];

        for (const file of files) {
            const records = await this.loadFile(path.join(dir, file));
            allRecords.push(...records);
        }

        return allRecords;
    }
}
