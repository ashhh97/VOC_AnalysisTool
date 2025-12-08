import React, { useState } from 'react'
import FileUpload from './components/FileUpload'
import SpreadsheetEditor from './components/SpreadsheetEditor'
import './App.css'

function App() {
  const [fileData, setFileData] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleFileUpload = async (file) => {
    setIsAnalyzing(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('上传失败')
      }

      const data = await response.json()
      setFileData(data)
    } catch (error) {
      console.error('上传错误:', error)
      alert('上传失败，请重试')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleAnalyze = async () => {
    if (!fileData) return

    setIsAnalyzing(true)
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ fileId: fileData.fileId })
      })

      if (!response.ok) {
        throw new Error('分析失败')
      }

      const analyzedData = await response.json()
      setFileData(analyzedData)
    } catch (error) {
      console.error('分析错误:', error)
      alert('分析失败，请重试')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>VOC分析工具 - AI用户研究分析</h1>
        <p>上传Excel表格，AI将自动分类用户反馈</p>
      </header>

      <main className="app-main">
        {!fileData ? (
          <FileUpload onUpload={handleFileUpload} isAnalyzing={isAnalyzing} />
        ) : (
          <div className="editor-container">
            <div className="editor-header">
              <button onClick={() => setFileData(null)} className="btn-secondary">
                上传新文件
              </button>
              <button 
                onClick={handleAnalyze} 
                className="btn-primary"
                disabled={isAnalyzing}
              >
                {isAnalyzing ? '分析中...' : '开始AI分析'}
              </button>
            </div>
            <SpreadsheetEditor data={fileData} />
          </div>
        )}
      </main>
    </div>
  )
}

export default App

