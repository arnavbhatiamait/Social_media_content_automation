const fs = require('fs');

const logFile = 'C:\\Users\\ArnavBhatia\\.gemini\\antigravity-ide\\brain\\34f109b0-c1e5-4195-b539-f82b6f797710\\.system_generated\\logs\\transcript.jsonl';
if (!fs.existsSync(logFile)) {
  console.log('Log file not found:', logFile);
  process.exit(1);
}

const lines = fs.readFileSync(logFile, 'utf8').split('\n');
let printNext = false;
let stepIdx = -1;

for (const line of lines) {
  if (!line.trim()) continue;
  try {
    const obj = JSON.parse(line);
    if (obj.tool_calls) {
      const hasConsoleLogCall = obj.tool_calls.some(c => c.name === 'capture_browser_console_logs');
      if (hasConsoleLogCall) {
        printNext = true;
        stepIdx = obj.step_index;
        console.log(`\n=================== STEP ${stepIdx} CALL ===================`);
      }
    } else if (printNext && obj.source === 'SYSTEM') {
      console.log(`=================== STEP ${stepIdx} RESPONSE ===================`);
      console.log(obj.content || JSON.stringify(obj, null, 2));
      printNext = false;
    }
  } catch (err) {}
}
