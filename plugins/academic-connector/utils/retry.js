/**
 * Exponential Backoff Retry with Jitter, Timeout, and Callback support.
 * 
 * @param {Function} operation - The async function to retry.
 * @param {Object} options - Retry configuration.
 * @param {number} options.maxAttempts - Maximum number of retry attempts (default: 3).
 * @param {number} options.delay - Base delay in ms (default: 1000).
 * @param {boolean} options.exponential - Use exponential backoff (default: true).
 * @param {boolean} options.jitter - Add random jitter to avoid thundering herd (default: false).
 * @param {number} options.timeout - Per-attempt timeout in ms (default: 30000).
 * @param {Function} options.onRetry - Callback invoked on each retry with (error, attempt).
 * @param {Object} logger - Logger instance.
 */
export async function withRetry(operation, options = {}, logger = console) {
    const {
        maxAttempts = 3,
        delay = 1000,
        exponential = true,
        jitter = false,
        timeout = 30000,
        onRetry = null
    } = options;

    let lastError;
    let currentDelay = delay;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            // Wrap operation with timeout
            const result = await Promise.race([
                operation(),
                new Promise((_, reject) =>
                    setTimeout(() => reject(new Error(`Timeout setelah ${timeout}ms`)), timeout)
                )
            ]);
            return result;
        } catch (error) {
            lastError = error;

            if (attempt === maxAttempts) break;

            // Calculate delay with optional jitter
            let waitTime = exponential ? currentDelay * Math.pow(2, attempt - 1) : currentDelay;
            if (jitter) {
                const jitterAmount = waitTime * 0.3 * Math.random();
                waitTime += jitterAmount;
            }

            logger.warn?.(`[Retry ${attempt}/${maxAttempts}] Gagal: ${error.message}. Menunggu ${Math.round(waitTime)}ms...`);

            if (typeof onRetry === 'function') {
                await onRetry(error, attempt);
            }

            await new Promise(resolve => setTimeout(resolve, waitTime));
        }
    }

    logger.error?.(`[Retry] Seluruh ${maxAttempts} percobaan gagal.`);
    throw lastError;
}
