import { chromium } from "playwright";
import { TokenExtractor } from '../auth/TokenExtractor.js';

/**
 * BrowserAdapter (V3) — Reduced completely to a throw-away login bot.
 * Captures tokens and immediately closes itself to save memory.
 */
export class BrowserAdapter {
    constructor(config, logger) {
        this.config = config;
        this.logger = logger;
    }

    async captureSessionToken(accountCtx) {
        this.logger?.info(`[BrowserAdapter] Booting Chrome for ${accountCtx.id}...`);
        
        const browser = await chromium.launch({
            headless: this.config.browser.headless,
            slowMo: 100
        });

        const context = await browser.newContext();
        const page = await context.newPage();
        const tokenExtractor = new TokenExtractor(page, this.logger);
        
        // Start listening to HTTP Headers
        await tokenExtractor.startInterception();

        try {
            this.logger?.info(`[BrowserAdapter] Navigating to Portal...`);
            await page.goto(this.config.routes.login_portal, { waitUntil: 'domcontentloaded', timeout: 90000 });
            
            // Login credentials inject
            await page.fill('input[type="text"], input[name="username"], #userId', accountCtx.username);
            await page.fill('input[type="password"], input[name="password"]', accountCtx.password);
            
            this.logger?.info(`[BrowserAdapter] Submitting login...`);
            await Promise.all([
                page.waitForNavigation({ waitUntil: 'networkidle', timeout: 90000 }).catch(() => {
                    this.logger?.warn(`[BrowserAdapter] Navigation timeout suppressed (Intercepted Token will be checked).`);
                }),
                page.click('button[type="submit"], input[type="submit"], .btn-login')
            ]);
            await page.waitForTimeout(3000); // Buffer for XHR requests
            
            this.logger?.info(`[BrowserAdapter] Login Navigation Complete, extracting Tokens...`);
            return await tokenExtractor.extract();
            
        } catch (err) {
            this.logger?.error(`[BrowserAdapter] Login Sequence Failed for ${accountCtx.id}: ${err.message}`);
            throw err;
        } finally {
            await browser.close();
            this.logger?.info(`[BrowserAdapter] Chrome Closed for ${accountCtx.id}.`);
        }
    }
}
