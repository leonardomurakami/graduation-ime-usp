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