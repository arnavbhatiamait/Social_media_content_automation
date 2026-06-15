const fs = require('fs');

const logFile = 'C:\\Users\\ArnavBhatia\\.gemini\\antigravity-ide\\brain\\34f109b0-c1e5-4195-b539-f82b6f797710\\.system_generated\\logs\\transcript.jsonl';
const lines = fs.readFileSync(logFile, 'utf8').split('\n');

for (let i = 0; i < Math.min(10, lines.length); i++) {
  console.log(`LINE ${i}:`, lines[i].substring(0, 300));
}
