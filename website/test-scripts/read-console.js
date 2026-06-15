const fs = require('fs');
const path = require('path');

const logFile = 'C:\\Users\\ArnavBhatia\\.gemini\\antigravity-ide\\brain\\34f109b0-c1e5-4195-b539-f82b6f797710\\.system_generated\\logs\\transcript.jsonl';

if (!fs.existsSync(logFile)) {
  console.log('Log file not found:', logFile);
  process.exit(1);
}

const lines = fs.readFileSync(logFile, 'utf8').split('\n');
console.log(`Total transcript lines: ${lines.length}`);

for (const line of lines) {
  if (!line.trim()) continue;
  try {
    const obj = JSON.parse(line);
    // Look for console log captures
    if (obj.tool_calls) {
      for (const call of obj.tool_calls) {
        if (call.ToolName === 'capture_browser_console_logs' || call.toolAction === 'Capturing browser console logs') {
          console.log(`--- STEP ${obj.step_index} CONSOLE LOG CALL ---`);
        }
      }
    }
    if (obj.source === 'SYSTEM' && obj.content && (obj.content.includes('console') || obj.content.includes('error') || obj.content.includes('status'))) {
      if (obj.content.includes('Console logs') || obj.content.includes('logs') || obj.content.includes('status":"DONE"')) {
        console.log(`--- STEP ${obj.step_index} SYSTEM RESPONSE ---`);
        console.log(obj.content.substring(0, 1000));
      }
    }
  } catch (err) {
    // Ignore parse errors
  }
}
