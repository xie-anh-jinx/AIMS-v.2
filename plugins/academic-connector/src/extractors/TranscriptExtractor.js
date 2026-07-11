/**
 * TranscriptExtractor — Extracts transcript data from an academic portal page.
 */
export class TranscriptExtractor {
    constructor(browserAdapter, selectors, logger) {
        this.browser = browserAdapter;
        this.selectors = selectors;
        this.logger = logger;
    }

    async extract() {
        this.logger?.info('Extracting transcript data...');

        // Wait for loading spinner to disappear (if any)
        if (this.selectors.loading?.spinner) {
            await this.browser.waitForHidden(this.selectors.loading.spinner);
        }

        const rowSelector = this.selectors.table?.transcript;
        if (!rowSelector) throw new Error('Selector "table.transcript" not defined in selectors.yml');

        const data = await this.browser.extractTableWithHeaders(rowSelector);
        this.logger?.info(`Extracted ${data.length} transcript rows.`);
        return data;
    }
}
