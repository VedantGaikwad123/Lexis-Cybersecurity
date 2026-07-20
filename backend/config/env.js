/**
 * Centralized Environment & Secrets Validation Module for LEXIS Backend
 * Validates required security and runtime variables on application startup.
 * Fails fast with clear actionable error messages if requirements are not met.
 */

const fs = require('fs');
const path = require('path');

// Basic .env parser in standard JS to avoid external runtime dependency issues
function loadEnvFile() {
  const envPath = path.resolve(process.cwd(), '.env');
  if (fs.existsSync(envPath)) {
    const content = fs.readFileSync(envPath, 'utf8');
    content.split('\n').forEach((line) => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
        const [key, ...valParts] = trimmed.split('=');
        const value = valParts.join('=').trim().replace(/^["']|["']$/g, '');
        if (!process.env[key.trim()]) {
          process.env[key.trim()] = value;
        }
      }
    });
  }
}

function validateEnv() {
  loadEnvFile();

  const env = process.env.NODE_ENV || 'development';
  const errors = [];
  const warnings = [];

  console.log(`[ENV VALIDATION] Initializing configuration validation for environment: '${env}'...`);

  // 1. Validate NODE_ENV
  const validEnvironments = ['development', 'test', 'staging', 'production'];
  if (!validEnvironments.includes(env)) {
    errors.push(`NODE_ENV must be one of [${validEnvironments.join(', ')}]. Received: '${env}'`);
  }

  // 2. Validate PORT
  const port = parseInt(process.env.PORT || '5000', 10);
  if (isNaN(port) || port <= 0 || port > 65535) {
    errors.push(`PORT must be a valid port number between 1 and 65535. Received: '${process.env.PORT}'`);
  }

  // 3. Security Requirements: JWT Secrets
  const jwtSecret = process.env.JWT_SECRET;
  const jwtRefreshSecret = process.env.JWT_REFRESH_SECRET;

  if (!jwtSecret) {
    errors.push('JWT_SECRET is missing. Secure authentication token signing requires JWT_SECRET.');
  } else if (env === 'production' && jwtSecret.length < 32) {
    errors.push(`CRITICAL SECURITY FAILURE: Production JWT_SECRET must be at least 32 characters long. Current length: ${jwtSecret.length}`);
  } else if (jwtSecret.length < 16) {
    warnings.push(`JWT_SECRET length is short (${jwtSecret.length} chars). Minimum 32 chars recommended.`);
  }

  if (!jwtRefreshSecret) {
    errors.push('JWT_REFRESH_SECRET is missing. Token rotation requires JWT_REFRESH_SECRET.');
  } else if (env === 'production' && jwtRefreshSecret.length < 32) {
    errors.push(`CRITICAL SECURITY FAILURE: Production JWT_REFRESH_SECRET must be at least 32 characters long. Current length: ${jwtRefreshSecret.length}`);
  }

  // 4. Validate Database URIs
  const mongoUri = process.env.MONGO_URI;
  if (!mongoUri) {
    errors.push('MONGO_URI is missing. Primary persistence layer requires a MongoDB connection URI.');
  } else if (!mongoUri.startsWith('mongodb://') && !mongoUri.startsWith('mongodb+srv://')) {
    errors.push(`MONGO_URI format invalid. Must start with 'mongodb://' or 'mongodb+srv://'. Received: '${mongoUri}'`);
  }

  // 5. Validate Redis & Qdrant
  const redisUrl = process.env.REDIS_URL;
  if (!redisUrl) {
    warnings.push('REDIS_URL missing. Rate limiting and session caching will fall back to in-memory store.');
  }

  const qdrantUrl = process.env.QDRANT_URL;
  if (!qdrantUrl) {
    warnings.push('QDRANT_URL missing. AI Vector search capability will be unavailable.');
  }

  // 6. Validate Key Encryption Secret
  const encryptionKey = process.env.ENCRYPTION_KEY;
  if (env === 'production' && (!encryptionKey || encryptionKey.length < 32)) {
    errors.push('CRITICAL SECURITY FAILURE: Production ENCRYPTION_KEY must be configured (min 32 bytes / 64 hex chars).');
  }

  // Report Warnings
  if (warnings.length > 0) {
    console.warn('\n[ENV VALIDATION WARNINGS]');
    warnings.forEach((w) => console.warn(`  ⚠️  ${w}`));
  }

  // Report Errors & Fail Fast
  if (errors.length > 0) {
    console.error('\n[ENV VALIDATION ERRORS - STARTUP TERMINATED]');
    errors.forEach((e) => console.error(`  ❌ ${e}`));
    console.error('\nPlease update your environment variables in `.env` or CI secrets according to `.env.example`.\n');
    if (require.main === module) {
      process.exit(1);
    }
    throw new Error(`Environment validation failed with ${errors.length} error(s).`);
  }

  console.log('[ENV VALIDATION SUCCESS] All required environment variables and security constraints verified cleanly.');

  return {
    NODE_ENV: env,
    PORT: port,
    API_PREFIX: process.env.API_PREFIX || '/api/v1',
    CLIENT_URL: process.env.CLIENT_URL || 'http://localhost:3000',
    JWT_SECRET: jwtSecret,
    JWT_REFRESH_SECRET: jwtRefreshSecret,
    JWT_EXPIRES_IN: process.env.JWT_EXPIRES_IN || '15m',
    JWT_REFRESH_EXPIRES_IN: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
    MONGO_URI: mongoUri,
    REDIS_URL: redisUrl,
    QDRANT_URL: qdrantUrl,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    SARVAM_API_KEY: process.env.SARVAM_API_KEY,
    SMS_PROVIDER_KEY: process.env.SMS_PROVIDER_KEY,
    ALLOWED_ORIGINS: (process.env.ALLOWED_ORIGINS || '').split(',').map((o) => o.trim())
  };
}

if (require.main === module) {
  try {
    validateEnv();
  } catch (err) {
    process.exit(1);
  }
}

module.exports = { validateEnv };
