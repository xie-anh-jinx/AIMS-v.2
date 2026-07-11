import fetch from 'node-fetch';

/**
 * HttpClient — Base class for making raw HTTP requests with retries and logging.
 */
export class HttpClient {
    constructor(logger) {
        this.logger = logger;
    }

    async post(endpoint, data, headers = {}) {
        this.logger?.debug(`HTTP POST to ${endpoint}`);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...headers
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP Error ${response.status}: ${await response.text()}`);
        }

        return await response.json();
    }
}
