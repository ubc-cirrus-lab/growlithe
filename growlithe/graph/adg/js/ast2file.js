const fs = require('fs');
const escodegen = require('escodegen');


const inputFile = process.argv[2];
const outputFile = process.argv[3];

const ast = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
const code = escodegen.generate(ast);

fs.writeFileSync(outputFile, code);