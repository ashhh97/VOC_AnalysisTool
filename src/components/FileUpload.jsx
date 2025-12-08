import React, { useRef, useState } from 'react'
import './FileUpload.css'

function FileUpload({ onUpload, isAnalyzing }) {
  const fileInputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileSelect = (file) => {
    if (file && (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                 file.type === 'application/vnd.ms-excel' ||
                 file.name.endsWith('.xlsx') || 
                 file.name.endsWith('.xls'))) {
      onUpload(file)
    } else {
      alert('请上传Excel文件（.xlsx 或 .xls）')
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  return (
    <div className="upload-container">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''} ${isAnalyzing ? 'analyzing' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </div>
        <h2>上传VOC Excel表格</h2>
        <p>点击或拖拽文件到此处</p>
        <p className="file-types">支持 .xlsx 和 .xls 格式</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls"
          style={{ display: 'none' }}
          onChange={(e) => {
            const file = e.target.files[0]
            if (file) {
              handleFileSelect(file)
            }
          }}
        />
        {isAnalyzing && (
          <div className="analyzing-overlay">
            <div className="spinner"></div>
            <p>正在处理文件...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default FileUpload

