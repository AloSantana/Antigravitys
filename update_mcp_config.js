const fs = require('fs');
const path = require('path');

const filePaths = [
    'opencode.json',
    path.join(process.env.HOME, '.config', 'opencode', 'opencode.json')
];

for (const filePath of filePaths) {
    try {
        if (!fs.existsSync(filePath)) continue;
        
        let raw = fs.readFileSync(filePath, 'utf8');
        let data = JSON.parse(raw);
        
        if (data.mcp) {
            for (const key in data.mcp) {
                data.mcp[key].enabled = true;
            }
            fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
            console.log(`Updated ${filePath}`);
        }
    } catch (e) {
        console.error(`Failed to update ${filePath}:`, e);
    }
}
