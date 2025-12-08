import React, { useEffect, useRef } from 'react'
import './SpreadsheetEditor.css'

function SpreadsheetEditor({ data }) {
  const containerRef = useRef(null)
  const luckysheetRef = useRef(null)

  useEffect(() => {
    if (!data || !containerRef.current) return

    // 初始化Luckysheet
    if (window.luckysheet) {
      // 如果已经初始化过，先销毁
      if (luckysheetRef.current) {
        window.luckysheet.destroy()
      }

      const options = {
        container: 'luckysheet-container',
        lang: 'zh',
        allowCopy: true,
        allowEdit: true,
        allowDelete: true,
        showtoolbar: true,
        showinfobar: false,
        showsheetbar: true,
        showstatisticBar: false,
        enableAddRow: true,
        enableAddCol: true,
        allowEdit: true,
        data: data.sheets || []
      }

      window.luckysheet.create(options)
      luckysheetRef.current = true
    }

    return () => {
      if (window.luckysheet && luckysheetRef.current) {
        try {
          window.luckysheet.destroy()
        } catch (e) {
          console.error('销毁Luckysheet失败:', e)
        }
      }
    }
  }, [data])

  return (
    <div className="spreadsheet-container">
      <div id="luckysheet-container" ref={containerRef}></div>
    </div>
  )
}

export default SpreadsheetEditor

