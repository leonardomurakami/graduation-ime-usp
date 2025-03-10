/**
 * Script to generate JSON files in static directory for code files
 * This version uses full paths from the static directory
 * Save this as scripts/generate-static-json.js
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Configuration
const staticDir = path.join(__dirname, '../static'); // Static directory root
const outputDir = path.join(staticDir, 'code-json'); // Output directory for JSON files

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Find all file-tree.json files in the static directory recursively
const fileTreeFiles = glob.sync('**/file-tree.json', { cwd: staticDir });

console.log(`Found ${fileTreeFiles.length} file-tree.json files in static directory`);
fileTreeFiles.forEach(file => console.log(`- ${file}`));

// Process each file tree
let totalFilesProcessed = 0;
let totalErrors = 0;

for (const fileTreeRelativePath of fileTreeFiles) {
  // Construct the full path to the file-tree.json
  const fileTreePath = path.join(staticDir, fileTreeRelativePath);
  const fileTreeDir = path.dirname(fileTreePath);
  
  // Get the relative path from static directory to this file tree directory
  const relativeTreeDir = path.relative(staticDir, fileTreeDir);
  
  console.log(`\nProcessing file tree: ${fileTreeRelativePath}`);
  console.log(`File tree directory: ${relativeTreeDir}`);
  
  try {
    // Read and parse the file tree
    const fileTreeContent = fs.readFileSync(fileTreePath, 'utf8');
    const fileTree = JSON.parse(fileTreeContent);
    
    // Extract file paths from this file tree
    const filePaths = [];
    function extractFilePaths(node) {
      if (!node) return;
      
      if (node.type === 'file' && node.path) {
        filePaths.push(node.path);
      }
      
      if (node.children && Array.isArray(node.children)) {
        for (const child of node.children) {
          extractFilePaths(child);
        }
      }
    }
    
    extractFilePaths(fileTree);
    console.log(`Found ${filePaths.length} files in ${fileTreeRelativePath}`);
    
    // Process each file in this file tree
    let successCount = 0;
    let errorCount = 0;
    
    for (const filePath of filePaths) {
      try {
        // IMPORTANT FIX: Check for and fix path duplication
        // Extract the first directory from filePath
        const firstDir = filePath.split('/')[0];
        
        // Check if the fileTreeDir already ends with this directory
        const dirEndsWithFirstDir = fileTreeDir.endsWith(firstDir);
        
        let sourceFilePath;
        if (dirEndsWithFirstDir) {
          // Remove the duplicated directory from the path
          const pathWithoutFirstDir = filePath.substring(firstDir.length + 1); // +1 for the slash
          sourceFilePath = path.join(fileTreeDir, pathWithoutFirstDir);
        } else {
          // Use the path as is
          sourceFilePath = path.join(fileTreeDir, filePath);
        }
        
        // Create the full path identifier for output
        // This combines the relative directory of the file tree with the file path
        let fullPathIdentifier;
        if (relativeTreeDir) {
          if (dirEndsWithFirstDir) {
            // If we removed a duplicated directory, just use the relative tree dir
            const pathWithoutFirstDir = filePath.substring(firstDir.length + 1);
            fullPathIdentifier = path.join(relativeTreeDir, pathWithoutFirstDir);
          } else {
            // Otherwise, combine the relative tree dir with the file path
            fullPathIdentifier = path.join(relativeTreeDir, filePath);
          }
        } else {
          fullPathIdentifier = filePath;
        }
        
        // Normalize the path to use forward slashes consistently
        fullPathIdentifier = fullPathIdentifier.replace(/\\/g, '/');
        
        // Create output file path with the full path identifier
        const outputFilePath = path.join(outputDir, `${fullPathIdentifier}.json`);
        const outputFileDir = path.dirname(outputFilePath);
        
        // Create output directory if it doesn't exist
        if (!fs.existsSync(outputFileDir)) {
          fs.mkdirSync(outputFileDir, { recursive: true });
        }
        
        // Log paths for debugging
        console.log(`For ${filePath}:`);
        console.log(`  - Source path: ${sourceFilePath}`);
        console.log(`  - Full path identifier: ${fullPathIdentifier}`);
        console.log(`  - Output path: ${outputFilePath}`);
        
        // Try to read source file
        if (!fs.existsSync(sourceFilePath)) {
          console.error(`Source file not found: ${sourceFilePath}`);
          errorCount++;
          continue;
        }
        
        // If we get here, the file exists at the expected path
        const content = fs.readFileSync(sourceFilePath, 'utf8');
        
        // Create JSON file
        const jsonContent = JSON.stringify({ content });
        fs.writeFileSync(outputFilePath, jsonContent);
        
        console.log(`Processed: ${fullPathIdentifier}`);
        successCount++;
      } catch (error) {
        console.error(`Error processing ${filePath}:`, error);
        errorCount++;
      }
    }
    
    console.log(`Results for ${fileTreeRelativePath}: success=${successCount}, errors=${errorCount}`);
    totalFilesProcessed += successCount;
    totalErrors += errorCount;
    
  } catch (treeError) {
    console.error(`Error processing file tree ${fileTreeRelativePath}:`, treeError);
    totalErrors++;
  }
}

console.log(`\nOverall results: successfully processed ${totalFilesProcessed} files, errors: ${totalErrors}`);