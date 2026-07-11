/**
 * TokenExtractor — Injects into Playwright to intercept headers and steal Bearer/Cookies tokens.
 */
export class TokenExtractor {
    constructor(page, logger) {
        this.page = page;
        this.logger = logger;
        this.bearerToken = null;
        this.cookies = null;
    }

    async startInterception() {
        this.logger?.info('[Auth] Starting Token Interception...');
        this.page.on('request', request => {
            const headers = request.headers();
            if (headers['authorization'] && headers['authorization'].startsWith('Bearer')) {
                if (!this.bearerToken) {
                    this.bearerToken = headers['authorization'];
                    this.logger?.debug('[Auth] Bearer Token Intercepted!');
                }
            }
        });
    }

    async extract() {
        if (!this.bearerToken) {
           this.logger?.warn('[Auth] No Bearer token found during interception.');
        }
        const playCookies = await this.page.context().cookies();
        // Convert playwright cookies to string 
        this.cookies = playCookies.map(c => `${c.name}=${c.value}`).join('; ');
        
        return {
            bearerToken: this.bearerToken,
            cookies: this.cookies
        };
    }
}
