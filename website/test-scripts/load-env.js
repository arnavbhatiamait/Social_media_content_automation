const fs = require('fs');
const path = require('path');

function loadEnv() {
  // Try website/.env.local first
  let envPath = path.join(__dirname, '..', '.env.local');
  if (!fs.existsSync(envPath)) {
    // Fall back to root .env
    envPath = path.join(__dirname, '..', '..', '.env');
  }
  
  if (!fs.existsSync(envPath)) {
    console.warn('Could not find .env.local or root .env file');
    return;
  }

  try {
    const envContent = fs.readFileSync(envPath, 'utf8');
    const lines = envContent.split(/\r?\n/);
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const parts = trimmed.split('=');
        if (parts.length >= 2) {
          const key = parts[0].trim();
          let val = parts.slice(1).join('=').trim();
          // Strip surrounding quotes if present
          if (
            (val.startsWith('"') && val.endsWith('"')) ||
            (val.startsWith("'") && val.endsWith("'"))
          ) {
            val = val.substring(1, val.length - 1);
          }
          if (process.env[key] === undefined) {
            process.env[key] = val;
          }
        }
      }
    }
  } catch (error) {
    console.error('Error loading environment variables:', error);
  }
}

loadEnv();
