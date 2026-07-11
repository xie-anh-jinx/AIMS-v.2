/**
 * KHSExtractor — Extracts KHS (Kartu Hasil Studi) data.
 */
export class KHSExtractor {
    constructor(browserAdapter, selectors, logger) {
        this.browser = browserAdapter;
        this.selectors = selectors;
        this.logger = logger;
    }

    async extract() {
        this.logger?.info('Extracting KHS data...');

        if (this.selectors.loading?.spinner) {
            await this.browser.waitForHidden(this.selectors.loading.spinner);
        }

        const rowSelector = this.selectors.table?.khs;
        if (!rowSelector) throw new Error('Selector "table.khs" not defined in selectors.yml');

        const data = await this.browser.extractTableWithHeaders(rowSelector);
        this.logger?.info(`Extracted ${data.length} KHS rows.`);
        return data;
    }
}
