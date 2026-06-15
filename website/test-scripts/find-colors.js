const fs = require('fs');

const file = 'c:\\Users\\ArnavBhatia\\Desktop\\arnav\\New Projects\\automated_posts\\website\\app\\dashboard\\page.tsx';
if (!fs.existsSync(file)) {
  console.log('File not found:', file);
  process.exit(1);
}

const lines = fs.readFileSync(file, 'utf8').split('\n');
console.log(`Loaded ${lines.length} lines.`);

const keywords = ['violet', 'fuchsia', 'purple'];
let count = 0;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const matched = keywords.filter(k => line.toLowerCase().includes(k));
  if (matched.length > 0) {
    console.log(`Line ${i + 1}: ${line.trim()} (matches: ${matched.join(', ')})`);
    count++;
  }
}
console.log(`Total matching lines: ${count}`);
