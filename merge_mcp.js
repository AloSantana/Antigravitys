const fs = require('fs');
const path = require('path');

const localPath = 'opencode.json';
const globalPath = path.join(process.env.HOME, '.config', 'opencode', 'opencode.json');

const localData = JSON.parse(fs.readFileSync(localPath, 'utf8'));
const globalData = JSON.parse(fs.readFileSync(globalPath, 'utf8'));

if (localData.mcp) {
    globalData.mcp = localData.mcp;
    fs.writeFileSync(globalPath, JSON.stringify(globalData, null, 2));
    console.log("Successfully merged MCP config to global opencode.json");
}
