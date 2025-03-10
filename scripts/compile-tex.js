const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Find all .tex files
function findTexFiles(dir, filelist = []) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filepath = path.join(dir, file);
    if (fs.statSync(filepath).isDirectory()) {
      if (file !== 'website' && file !== 'node_modules' && !file.startsWith('.')) {
        filelist = findTexFiles(filepath, filelist);
      }
    } else if (path.extname(file) === '.tex') {
      filelist.push(filepath);
    }
  });
  return filelist;
}

// Create the static PDF directory
const pdfDir = path.join('website', 'static', 'pdfs');
if (!fs.existsSync(pdfDir)) {
  fs.mkdirSync(pdfDir, { recursive: true });
}

// Process each .tex file
const texFiles = findTexFiles('.');
texFiles.forEach(texFile => {
  try {
    // Get directory and filename
    const dirName = path.dirname(texFile);
    const baseName = path.basename(texFile, '.tex');
    
    // Compile the LaTeX file
    console.log(`Compiling ${texFile}...`);
    execSync(`cd "${dirName}" && pdflatex -interaction=nonstopmode "${baseName}.tex"`);
    
    // Create a meaningful path for the PDF
    const relativePath = path.relative('.', dirName);
    const destinationDir = path.join(pdfDir, relativePath);
    
    // Create destination directory if it doesn't exist
    if (!fs.existsSync(destinationDir)) {
      fs.mkdirSync(destinationDir, { recursive: true });
    }
    
    // Copy the PDF to the static directory
    const pdfFile = path.join(dirName, `${baseName}.pdf`);
    const destinationFile = path.join(destinationDir, `${baseName}.pdf`);
    fs.copyFileSync(pdfFile, destinationFile);
    
    console.log(`Copied ${pdfFile} to ${destinationFile}`);
  } catch (error) {
    console.error(`Error processing ${texFile}: ${error.message}`);
  }
});