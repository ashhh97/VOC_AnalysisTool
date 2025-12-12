import React, { useState, useEffect, useRef } from 'react'
import FileUpload from './components/FileUpload'
import SpreadsheetEditor from './components/SpreadsheetEditor'
import './App.css'

function App() {
  const [fileData, setFileData] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)
  const [countdown, setCountdown] = useState(null)
  const [progress, setProgress] = useState(null) // 进度信息 {current, total, progress, message}
  const [timeoutSeconds] = useState(120) // 超时时间：120秒
  const countdownTimerRef = useRef(null)
  const abortControllerRef = useRef(null)
  const eventSourceRef = useRef(null)

  // 清理定时器和请求
  useEffect(() => {
    // 使用 unload 事件代替 beforeunload，确保不会阻止页面刷新
    const handleUnload = () => {
      // 只清理资源，不阻止页面刷新
      if (countdownTimerRef.current) {
        clearInterval(countdownTimerRef.current)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }

    // 监听页面卸载事件（不会阻止刷新）
    window.addEventListener('unload', handleUnload)
    
    // 组件卸载时清理
    return () => {
      window.removeEventListener('unload', handleUnload)
      if (countdownTimerRef.current) {
        clearInterval(countdownTimerRef.current)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  const handleFileUpload = async (file) => {
    setIsAnalyzing(true)
    setErrorMessage(null)
    setCountdown(null)
    
    // 创建AbortController用于取消请求
    abortControllerRef.current = new AbortController()
    
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: '上传失败' }))
        throw new Error(errorData.error || `上传失败: ${response.status}`)
      }

      const data = await response.json()
      console.log('[上传] 收到上传响应:', data)
      console.log('[上传] fileId:', data.fileId)
      console.log('[上传] sheets数量:', data.sheets?.length)
      if (data.sheets && data.sheets.length > 0) {
        console.log('[上传] 第一个sheet:', {
          name: data.sheets[0].name,
          index: data.sheets[0].index,
          celldata数量: data.sheets[0].celldata?.length || 0
        })
        if (data.sheets[0].celldata && data.sheets[0].celldata.length > 0) {
          console.log('[上传] 第一个sheet的前3个单元格:', data.sheets[0].celldata.slice(0, 3))
        }
      }
      setFileData(data)
      console.log('[上传] 已设置fileData')
      
      // 上传成功后自动开始AI分析
      setTimeout(() => {
        console.log('[上传] 开始自动分析...')
        handleAnalyze(data)
      }, 1000) // 等待1秒让表格先显示
    } catch (error) {
      if (error.name === 'AbortError') {
        setErrorMessage('请求已取消')
      } else {
        console.error('上传错误:', error)
        setErrorMessage(error.message || '上传失败，请重试')
      }
      setIsAnalyzing(false)
      setCountdown(null)
      if (countdownTimerRef.current) {
        clearInterval(countdownTimerRef.current)
      }
    }
  }

  const handleAnalyze = async (dataToAnalyze = null) => {
    const targetData = dataToAnalyze || fileData
    if (!targetData || !targetData.fileId) return

    setIsAnalyzing(true)
    setErrorMessage(null)
    setProgress(null)
    setCountdown(timeoutSeconds)
    
    // 关闭之前的EventSource
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    
    // 启动倒计时
    countdownTimerRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev === null || prev <= 1) {
          clearInterval(countdownTimerRef.current)
          // 超时，关闭EventSource
          if (eventSourceRef.current) {
            eventSourceRef.current.close()
            eventSourceRef.current = null
          }
          return null
        }
        return prev - 1
      })
    }, 1000)

    // 设置超时
    const timeoutId = setTimeout(() => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
      setIsAnalyzing(false)
      setCountdown(null)
      setProgress(null)
      setErrorMessage(`分析超时（${timeoutSeconds}秒），请重试`)
      if (countdownTimerRef.current) {
        clearInterval(countdownTimerRef.current)
      }
    }, timeoutSeconds * 1000)

    return new Promise((resolve, reject) => {
      // 使用fetch的stream模式接收SSE
      fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ fileId: targetData.fileId })
      }).then(response => {
        if (!response.ok) {
          throw new Error(`分析失败: ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let completed = false // 跟踪是否已收到complete消息

        const readStream = () => {
          reader.read().then(({ done, value }) => {
            if (done) {
              clearTimeout(timeoutId)
              if (countdownTimerRef.current) {
                clearInterval(countdownTimerRef.current)
                countdownTimerRef.current = null
              }
              // 流结束，如果没有收到complete消息，可能是错误
              if (!completed) {
                setIsAnalyzing(false)
                setProgress(null)
                setCountdown(null)
                setErrorMessage('分析连接中断，请重试')
                reject(new Error('分析连接中断'))
              } else {
                resolve()
              }
              return
            }

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() || '' // 保留最后一个不完整的行

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))
                  console.log('[前端] 收到SSE数据:', data.type, data)
                  
                  if (data.type === 'progress') {
                    setProgress({
                      current: data.current,
                      total: data.total,
                      progress: data.progress,
                      message: data.message
                    })
                  } else if (data.type === 'complete') {
                    completed = true
                    clearTimeout(timeoutId)
                    if (countdownTimerRef.current) {
                      clearInterval(countdownTimerRef.current)
                      countdownTimerRef.current = null
                    }
                    console.log('[前端] 收到完成数据:', data.data)
                    console.log('[前端] sheets数量:', data.data?.sheets?.length)
                    console.log('[前端] fileId:', data.data?.fileId)
                    if (data.data?.sheets) {
                      console.log('[前端] 第一个sheet:', JSON.stringify(data.data.sheets[0], null, 2).substring(0, 500))
                    }
                    setFileData(data.data)
                    setProgress(null)
                    setCountdown(null)
                    setIsAnalyzing(false)
                    resolve(data.data)
                    return
                  } else if (data.type === 'error') {
                    completed = true
                    clearTimeout(timeoutId)
                    if (countdownTimerRef.current) {
                      clearInterval(countdownTimerRef.current)
                      countdownTimerRef.current = null
                    }
                    setIsAnalyzing(false)
                    setProgress(null)
                    setCountdown(null)
                    setErrorMessage(data.message || '分析失败')
                    reject(new Error(data.message || '分析失败'))
                    return
                  }
                } catch (e) {
                  console.error('解析SSE数据失败:', e, line)
                }
              }
            }

            readStream()
          }).catch(err => {
            clearTimeout(timeoutId)
            if (countdownTimerRef.current) {
              clearInterval(countdownTimerRef.current)
              countdownTimerRef.current = null
            }
            setIsAnalyzing(false)
            setProgress(null)
            setCountdown(null)
            setErrorMessage(err.message || '分析失败，请重试')
            reject(err)
          })
        }

        readStream()
      }).catch(err => {
        clearTimeout(timeoutId)
        if (countdownTimerRef.current) {
          clearInterval(countdownTimerRef.current)
          countdownTimerRef.current = null
        }
        setIsAnalyzing(false)
        setProgress(null)
        setCountdown(null)
        setErrorMessage(err.message || '分析失败，请重试')
        reject(err)
      })
    })
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
              <button onClick={() => {
                setFileData(null)
                setErrorMessage(null)
                setCountdown(null)
                setProgress(null)
                if (eventSourceRef.current) {
                  eventSourceRef.current.close()
                  eventSourceRef.current = null
                }
                if (abortControllerRef.current) {
                  abortControllerRef.current.abort()
                }
                if (countdownTimerRef.current) {
                  clearInterval(countdownTimerRef.current)
                }
              }} className="btn-secondary">
                上传新文件
              </button>
              {isAnalyzing && (
                <>
                  <div className="analyzing-indicator">
                    <span className="spinner-small"></span>
                    <span>
                      {progress ? (
                        <>
                          {progress.message}
                          {progress.total > 0 && (
                            <span className="countdown">
                              （{progress.current}/{progress.total}，{progress.progress}%）
                            </span>
                          )}
                        </>
                      ) : (
                        <>
                          AI分析中，请稍候...
                          {countdown !== null && (
                            <span className="countdown">（剩余 {countdown} 秒）</span>
                          )}
                        </>
                      )}
                    </span>
                  </div>
                  <button 
                    onClick={async () => {
                      if (fileData && fileData.fileId) {
                        try {
                          // 关闭EventSource
                          if (eventSourceRef.current) {
                            eventSourceRef.current.close()
                            eventSourceRef.current = null
                          }
                          
                          // 取消前端请求
                          if (abortControllerRef.current) {
                            abortControllerRef.current.abort()
                          }
                          
                          // 通知后端停止分析
                          await fetch('/api/analyze/stop', {
                            method: 'POST',
                            headers: {
                              'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ fileId: fileData.fileId })
                          })
                          
                          setIsAnalyzing(false)
                          setCountdown(null)
                          setProgress(null)
                          setErrorMessage('分析已终止')
                          if (countdownTimerRef.current) {
                            clearInterval(countdownTimerRef.current)
                            countdownTimerRef.current = null
                          }
                        } catch (error) {
                          console.error('终止分析失败:', error)
                          setErrorMessage('终止分析失败，请重试')
                        }
                      }
                    }}
                    className="btn-danger"
                  >
                    终止分析
                  </button>
                </>
              )}
              {!isAnalyzing && fileData && fileData.sheets && fileData.sheets.length > 0 && (
                <button 
                  onClick={() => handleAnalyze()} 
                  className="btn-primary"
                >
                  重新分析
                </button>
              )}
            </div>
            {errorMessage && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                <span>{errorMessage}</span>
                <button 
                  className="error-close"
                  onClick={() => setErrorMessage(null)}
                >
                  ×
                </button>
              </div>
            )}
            <SpreadsheetEditor data={fileData} />
          </div>
        )}
      </main>
    </div>
  )
}

export default App

