"use client";
import { useState, useRef } from 'react';
import api from '@/lib/api';
import { Upload, X, FileText, Image, File as FileIcon, Loader2 } from 'lucide-react';

const ICON_MAP = {
  'image/': Image,
  'application/pdf': FileText,
};

function getIcon(contentType) {
  for (const [prefix, Icon] of Object.entries(ICON_MAP)) {
    if (contentType?.startsWith(prefix)) return Icon;
  }
  return FileIcon;
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FileUpload({ inquiryId, files = [], onFilesChange, maxFiles = 5, readOnly = false }) {
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleUpload = async (fileList) => {
    if (!inquiryId || files.length >= maxFiles) return;
    setUploading(true);
    const newFiles = [...files];
    for (const file of Array.from(fileList).slice(0, maxFiles - files.length)) {
      if (file.size > 10 * 1024 * 1024) continue;
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await api.post(`/inquiries/${inquiryId}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        newFiles.push(res.data);
      } catch {}
    }
    onFilesChange?.(newFiles);
    setUploading(false);
  };

  const handleDelete = async (fileId) => {
    try {
      await api.delete(`/files/${fileId}`);
      onFilesChange?.(files.filter(f => f.id !== fileId));
    } catch {}
  };

  const handleDownload = (file) => {
    const url = `${process.env.REACT_APP_BACKEND_URL}/api/files/${file.id}/download`;
    window.open(url, '_blank');
  };

  if (readOnly) {
    if (files.length === 0) return null;
    return (
      <div className="sf-file-list" data-testid="file-list-readonly">
        {files.map(f => {
          const Icon = getIcon(f.content_type);
          return (
            <div key={f.id} className="sf-file-item" onClick={() => handleDownload(f)} style={{ cursor: 'pointer' }} data-testid={`file-${f.id}`}>
              <Icon size={16} style={{ flexShrink: 0, color: 'var(--sf-gold, #5ba4b5)' }} />
              <span className="sf-file-name">{f.original_filename}</span>
              <span className="sf-file-size">{formatSize(f.size)}</span>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div data-testid="file-upload-section">
      {/* Dropzone */}
      <div
        className={`sf-dropzone ${dragOver ? 'active' : ''}`}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files); }}
        onClick={() => inputRef.current?.click()}
        data-testid="file-dropzone"
      >
        {uploading ? (
          <Loader2 size={24} className="sf-spin" />
        ) : (
          <>
            <Upload size={24} style={{ opacity: 0.5 }} />
            <span>Dateien hierher ziehen oder klicken</span>
            <span style={{ fontSize: '0.72rem', opacity: 0.5 }}>Max. {maxFiles} Dateien, je 10 MB</span>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          multiple
          style={{ display: 'none' }}
          onChange={e => handleUpload(e.target.files)}
          data-testid="file-input"
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="sf-file-list" data-testid="file-list">
          {files.map(f => {
            const Icon = getIcon(f.content_type);
            return (
              <div key={f.id} className="sf-file-item" data-testid={`file-${f.id}`}>
                <Icon size={16} style={{ flexShrink: 0, color: 'var(--sf-gold, #5ba4b5)' }} />
                <span className="sf-file-name" onClick={() => handleDownload(f)} style={{ cursor: 'pointer' }}>{f.original_filename}</span>
                <span className="sf-file-size">{formatSize(f.size)}</span>
                <button onClick={() => handleDelete(f.id)} className="sf-file-remove" data-testid={`file-remove-${f.id}`}>
                  <X size={14} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
