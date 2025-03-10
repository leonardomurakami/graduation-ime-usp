import React, { useState, useEffect } from 'react';
import { useColorMode } from '@docusaurus/theme-common';
import CodeBlock from '@theme/CodeBlock';
import styles from './CodeBrowser.module.css';
import { ChevronDown, ChevronRight, Folder, File, Code } from 'lucide-react';

// Main component
const CodeBrowser = ({ rootDir = 'static/code-samples', defaultOpenFile = null}) => {
  const [fileTree, setFileTree] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState({});
  const [selectedFile, setSelectedFile] = useState(defaultOpenFile);
  const [fileContent, setFileContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { colorMode } = useColorMode();
  
  // Build file tree from the static directory structure
  useEffect(() => {
    const buildFileTree = async () => {
      try {
        setLoading(true);
        
        // For Docusaurus static files, we need to define the structure manually
        // or load a pre-generated JSON file that describes the file structure
        const response = await fetch(`/${rootDir}/file-tree.json`);
        
        if (!response.ok) {
          throw new Error('Failed to load file structure. Make sure file-tree.json exists in your static directory.');
        }
        
        const data = await response.json();
        setFileTree(data);
        
        // Automatically expand the first level of folders
        const initialExpanded = {};
        if (data && data.children) {
          data.children.forEach(item => {
            if (item.type === 'directory') {
              initialExpanded[item.path] = true;
            }
          });
        }
        setExpandedFolders(initialExpanded);
        
        // If a default file is specified, load it
        if (defaultOpenFile) {
          setSelectedFile(defaultOpenFile);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error loading file structure:', err);
        setError(err.message);
        setLoading(false);
      }
    };
    
    buildFileTree();
  }, [rootDir, defaultOpenFile]);
  
  // Fetch file content when a file is selected
  useEffect(() => {
    const fetchFileContent = async () => {
      if (!selectedFile) return;
      
      try {
        setLoading(true);
        
        // Try to fetch from the plugin-generated JSON
        try {
          const timestamp = new Date().getTime(); // Add cache-busting
          const removeLastSlice = (path) => path.split('/').slice(0, -1).join('/');

          const jsonResponse = await fetch(`/code-json/${removeLastSlice(rootDir)}/${selectedFile}.json?t=${timestamp}`, {
            headers: {
              'Accept': 'application/json',
              'Cache-Control': 'no-cache'
            }
          });
          
          // Check if we got JSON or HTML by looking at the content-type
          const contentType = jsonResponse.headers.get('content-type');
          
          if (jsonResponse.ok && contentType && contentType.includes('application/json')) {
            // If JSON version exists and is actually JSON, use it
            const text = await jsonResponse.text();
            try {
              const data = JSON.parse(text);
              setFileContent(data.content);
              setLoading(false);
              return; // Exit early if successful
            } catch (jsonError) {
              console.error('Failed to parse JSON response:', jsonError);
              // Continue to fallback methods
            }
          }
        } catch (jsonError) {
          console.warn('Error fetching from plugin JSON:', jsonError);
          // Continue to fallback methods
        }
        
        // Try fallback to static JSON if available
        try {
          const staticJsonResponse = await fetch(`/${rootDir}-json/${selectedFile}.json`, {
            headers: {
              'Accept': 'application/json',
              'Cache-Control': 'no-cache'
            }
          });
          
          if (staticJsonResponse.ok) {
            const text = await staticJsonResponse.text();
            try {
              const data = JSON.parse(text);
              setFileContent(data.content);
              setLoading(false);
              return; // Exit early if successful
            } catch (jsonError) {
              console.error('Failed to parse static JSON response:', jsonError);
              // Continue to direct file access
            }
          }
        } catch (staticJsonError) {
          console.warn('Error fetching from static JSON:', staticJsonError);
          // Continue to direct file access
        }
            
        // Last resort - direct file access (less reliable)
        console.warn(`JSON versions not found, trying direct file access...`);
        
        const timestamp = new Date().getTime();
        const directResponse = await fetch(`/${rootDir}/${selectedFile}?raw=true&t=${timestamp}`, {
          headers: {
            'Accept': 'text/plain, application/octet-stream',
            'Cache-Control': 'no-cache'
          }
        });
        
        if (!directResponse.ok) {
          throw new Error(`Failed to load file content: ${directResponse.status}`);
        }
        
        const content = await directResponse.text();
        
        // Check if the content seems to be HTML
        if (content.toLowerCase().includes('<!doctype html>') || content.toLowerCase().includes('<html')) {
          setFileContent(
            `// Error: Received HTML instead of the actual file content.\n` +
            `// Please use the custom plugin or run the code conversion script.\n` +
            `// See README for instructions.`
          );
        } else {
          setFileContent(content);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error loading file content:', err);
        setError(err.message);
        setLoading(false);
      }
    };
    
    fetchFileContent();
  }, [selectedFile, rootDir]);
  
  // Toggle folder expansion
  const toggleFolder = (path) => {
    setExpandedFolders(prev => ({
      ...prev,
      [path]: !prev[path]
    }));
  };
  
  // Handle file selection
  const handleFileSelect = (path) => {
    setSelectedFile(path);
  };
  
  // Determine language based on file extension
  const getLanguage = (filename) => {
    if (!filename) return 'text';
    
    const extension = filename.split('.').pop().toLowerCase();
    
    switch (extension) {
      case 'js':
        return 'javascript';
      case 'jsx':
        return 'jsx';
      case 'ts':
        return 'typescript';
      case 'tsx':
        return 'tsx';
      case 'html':
        return 'html';
      case 'css':
        return 'css';
      case 'json':
        return 'json';
      case 'md':
      case 'mdx':
        return 'markdown';
      case 'py':
        return 'python';
      case 'java':
        return 'java';
      case 'c':
        return 'c';
      case 'cpp':
      case 'cc':
        return 'cpp';
      case 'go':
        return 'go';
      case 'rb':
        return 'ruby';
      case 'php':
        return 'php';
      case 'sh':
      case 'bash':
        return 'bash';
      case 'yml':
      case 'yaml':
        return 'yaml';
      case 'sql':
        return 'sql';
      default:
        return 'text';
    }
  };
  
  // Recursive function to render the file tree
  const renderFileTree = (node, level = 0) => {
    if (!node) return null;
    
    if (node.type === 'file') {
      return (
        <div 
          key={node.path}
          className={`${styles.fileItem} ${selectedFile === node.path ? styles.selectedFile : ''}`}
          style={{ paddingLeft: `${level * 16}px` }}
          onClick={() => handleFileSelect(node.path)}
        >
          <File size={16} className={styles.fileIcon} />
          <span className={styles.itemName}>{node.name}</span>
        </div>
      );
    }
    
    if (node.type === 'directory') {
      const isExpanded = expandedFolders[node.path];
      
      return (
        <div key={node.path}>
          <div 
            className={styles.folderItem}
            style={{ paddingLeft: `${level * 16}px` }}
            onClick={() => toggleFolder(node.path)}
          >
            {isExpanded ? 
              <ChevronDown size={16} className={styles.folderIcon} /> : 
              <ChevronRight size={16} className={styles.folderIcon} />
            }
            <Folder size={16} className={styles.folderIcon} />
            <span className={styles.itemName}>{node.name}</span>
          </div>
          
          {isExpanded && node.children && (
            <div className={styles.folderChildren}>
              {node.children.map(child => renderFileTree(child, level + 1))}
            </div>
          )}
        </div>
      );
    }
    
    return null;
  };
  
  // Render file content with proper syntax highlighting using Docusaurus CodeBlock
  const renderFileContent = () => {
    if (!selectedFile) {
      return (
        <div className={styles.noFileSelected}>
          <Code size={48} className={styles.codeIcon} />
          <p>Select a file to view its content</p>
        </div>
      );
    }
    
    if (loading) {
      return <div className={styles.loading}>Loading...</div>;
    }
    
    if (error) {
      return <div className={styles.error}>{error}</div>;
    }
    
    const language = getLanguage(selectedFile);
    
    return (
      <div className={styles.codeContainer}>
        <div className={styles.fileHeader}>
          <span className={styles.fileName}>{selectedFile}</span>
        </div>
        <div className={styles.codeBlockWrapper}>
          <CodeBlock 
            language={language}
            showLineNumbers={true}
          >
            {fileContent}
          </CodeBlock>
        </div>
      </div>
    );
  };
  
  if (loading && !fileTree) {
    return <div className={styles.loading}>Loading file explorer...</div>;
  }
  
  if (error && !fileTree) {
    return <div className={styles.error}>{error}</div>;
  }
  
  return (
    <div className={`${styles.codeBrowser} ${colorMode === 'dark' ? styles.darkTheme : styles.lightTheme}`}>
      <div className={styles.fileExplorer}>
        <div className={styles.explorerHeader}>
          <span>EXPLORER</span>
        </div>
        <div className={styles.fileTree}>
          {fileTree && renderFileTree(fileTree)}
        </div>
      </div>
      <div className={styles.contentArea}>
        {renderFileContent()}
      </div>
    </div>
  );
};

export default CodeBrowser;