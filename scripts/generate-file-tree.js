/**
 * @fileoverview Script to generate file-tree.json files for code directories
 * 
 * Usage:
 * node generate-file-tree.js <directory-to-scan> <output-path>
 * 
 * Example:
 * node generate-file-tree.js ./src/pages/code-samples ./src/pages/code-samples/file-tree.json
 */

const fs = require('fs');
const path = require('path');

// Get command line arguments
const directoryToScan = process.argv[2];
const outputPath = process.argv[3];

if (!directoryToScan) {
  console.error('Please provide a directory to scan');
  process.exit(1);
}

const finalOutputPath = outputPath || path.join(directoryToScan, 'file-tree.json');

/**
 * Creates a file tree structure by recursively scanning a directory
 * @param {string} dir - Directory to scan
 * @param {string} relativePath - Path relative to the base directory
 * @returns {Object} File tree structure
 */
function createFileTree(dir, relativePath = '') {
  const name = path.basename(dir);
  const currentPath = relativePath ? relativePath : name;
  
  const stats = fs.statSync(dir);
  
  if (!stats.isDirectory()) {
    return {
      name,
      path: currentPath,
      type: 'file'
    };
  }
  
  const children = fs.readdirSync(dir)
    .filter(file => !file.startsWith('.') && file !== 'file-tree.json') // Skip hidden files and the output file
    .map(file => {
      const filePath = path.join(dir, file);
      const fileRelativePath = path.join(currentPath, file).replace(/\\/g, '/');
      return createFileTree(filePath, fileRelativePath);
    })
    .sort((a, b) => {
      // Sort directories first, then files alphabetically
      if (a.type === 'directory' && b.type === 'file') return -1;
      if (a.type === 'file' && b.type === 'directory') return 1;
      return a.name.localeCompare(b.name);
    });
  
  return {
    name,
    path: currentPath,
    type: 'directory',
    children
  };
}

try {
  // Ensure the directory exists
  if (!fs.existsSync(directoryToScan)) {
    console.error(`Directory not found: ${directoryToScan}`);
    process.exit(1);
  }
  
  // Create the file tree
  const fileTree = createFileTree(directoryToScan);
  
  // Ensure output directory exists
  const outputDir = path.dirname(finalOutputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Write the result to a JSON file
  fs.writeFileSync(finalOutputPath, JSON.stringify(fileTree, null, 2));
  
  console.log(`File tree generated successfully at: ${finalOutputPath}`);
} catch (error) {
  console.error('Error generating file tree:', error);
  process.exit(1);
}