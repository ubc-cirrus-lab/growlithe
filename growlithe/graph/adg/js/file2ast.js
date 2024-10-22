const fs = require('fs');
const acorn = require('acorn');


const inputFile = process.argv[2];
const code = fs.readFileSync(inputFile, 'utf8');
const ast = acorn.parse(code, { ecmaVersion: 2020, sourceType: 'module', locations: true });

const outputFile = "tmp.json";
fs.writeFileSync(outputFile, JSON.stringify(ast, null, 2));