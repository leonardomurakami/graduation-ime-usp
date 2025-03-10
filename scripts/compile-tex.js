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
const pdfDir = path.join('static', 'pdfs');
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
    try {
      execSync(`cd "${dirName}" && pdflatex -interaction=nonstopmode "${baseName}.tex"`, { stdio: 'pipe' });
    } catch (compileError) {
      console.warn(`Warning: LaTeX compilation had issues for ${texFile}, but continuing: ${compileError.message}`);
      // Continue execution - PDF might still have been generated
    }
    
    // Create a meaningful path for the PDF
    const relativePath = path.relative('.', dirName);
    const destinationDir = path.join(pdfDir, relativePath);
    
    // Create destination directory if it doesn't exist
    if (!fs.existsSync(destinationDir)) {
      fs.mkdirSync(destinationDir, { recursive: true });
    }
    
    // Check if PDF was created
    const pdfFile = path.join(dirName, `${baseName}.pdf`);
    const destinationFile = path.join(destinationDir, `${baseName}.pdf`);
    
    if (!fs.existsSync(pdfFile)) {
      console.error(`Error: PDF file ${pdfFile} was not created`);
    } else {
      try {
        // Copy instead of rename
        if (fs.existsSync(destinationFile)) {
          fs.unlinkSync(destinationFile); // Remove existing file if it exists
        }
        
        // Use copyFile with a small delay to avoid potential file lock issues
        fs.copyFileSync(pdfFile, destinationFile);
        console.log(`Copied ${pdfFile} to ${destinationFile}`);
        
        // Only delete the original after successful copy
        fs.unlinkSync(pdfFile);
      } catch (moveError) {
        console.error(`Warning: Could not move PDF file ${pdfFile}: ${moveError.message}`);
        // Continue with execution - don't throw
      }
    }
    
    // Clean up auxiliary files
    const auxExtensions = ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk', '.synctex.gz', '.blg', '.bbl'];
    auxExtensions.forEach(ext => {
      const auxFile = path.join(dirName, `${baseName}${ext}`);
      try {
        if (fs.existsSync(auxFile)) {
          fs.unlinkSync(auxFile);
          console.log(`Cleaned up ${auxFile}`);
        }
      } catch (cleanupError) {
        console.error(`Warning: Could not clean up ${auxFile}: ${cleanupError.message}`);
        // Continue with execution - don't throw
      }
    });
  } catch (error) {
    console.error(`Error processing ${texFile}: ${error.message}`);
    // Continue with next file
  }
});

console.log('LaTeX compilation and PDF moving completed.');