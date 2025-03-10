import React from 'react';
import styles from './PdfViewer.module.css';

export default function PdfViewer({pdfPath, title}) {
  return (
    <div className={styles.pdfContainer}>
      <h2>{title || 'Document Viewer'}</h2>
      <div className={styles.pdfWrapper}>
        <object
          data={pdfPath}
          type="application/pdf"
          className={styles.pdfObject}
        >
          <div className={styles.fallback}>
            <p>It appears your browser doesn't support embedded PDFs.</p>
            <a 
              href={pdfPath}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.downloadLink}
            >
              Download the PDF
            </a>
          </div>
        </object>
      </div>
    </div>
  );
}