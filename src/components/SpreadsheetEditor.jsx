import React, { useEffect, useRef } from 'react'
import Spreadsheet from 'x-data-spreadsheet'
// 导入编译后的CSS
import 'x-data-spreadsheet/dist/xspreadsheet.css'
import './SpreadsheetEditor.css'

function SpreadsheetEditor({ data }) {
  const containerRef = useRef(null)
  const spreadsheetRef = useRef(null)

  // 转换单个sheet的数据格式
  const convertSheetData = (sheet) => {
    const rows = {}
    
    if (sheet.celldata && Array.isArray(sheet.celldata)) {
      sheet.celldata.forEach(cell => {
        const row = cell.r
        const col = cell.c
        const value = cell.v?.v || cell.v?.m || ''
        
        if (!rows[row]) {
          rows[row] = { cells: {} }
        }
        
        rows[row].cells[col] = {
          text: String(value)
        }
      })
    }
    
    return { 
      name: sheet.name || 'Sheet1',
      rows 
    }
  }

  // 转换所有sheet数据为x-data-spreadsheet需要的格式
  const convertAllSheetsData = (sheets) => {
    return {
      sheets: sheets.map(sheet => convertSheetData(sheet))
    }
  }

  useEffect(() => {
    console.log('[SpreadsheetEditor] 收到数据:', data)
    
    if (!data || !data.sheets || data.sheets.length === 0) {
      console.log('[SpreadsheetEditor] 数据为空，跳过初始化')
      return
    }

    if (!containerRef.current) {
      console.error('[SpreadsheetEditor] 容器不存在')
      return
    }

    // 销毁旧的实例
    if (spreadsheetRef.current) {
      try {
        spreadsheetRef.current.destroy()
      } catch (e) {
        console.warn('[SpreadsheetEditor] 销毁旧实例失败:', e)
      }
      spreadsheetRef.current = null
    }

    // 清空容器
    containerRef.current.innerHTML = ''

    try {
      console.log('[SpreadsheetEditor] 开始创建x-data-spreadsheet实例...')
      console.log('[SpreadsheetEditor] sheets数量:', data.sheets.length)
      
      // 创建单个Spreadsheet实例
      const spreadsheet = new Spreadsheet(containerRef.current, {
        mode: 'edit',
        showToolbar: true,
        showGrid: true,
        showContextmenu: true,
        view: {
          height: () => {
            const container = containerRef.current
            if (!container) return 500
            return container.clientHeight
          },
          width: () => {
            const container = containerRef.current
            return container ? container.clientWidth : 800
          },
        },
      })

      spreadsheetRef.current = spreadsheet

      // 转换所有sheet数据
      const allSheetsData = convertAllSheetsData(data.sheets)
      console.log('[SpreadsheetEditor] 转换后的数据:', allSheetsData)
      console.log('[SpreadsheetEditor] sheet名称列表:', allSheetsData.sheets.map(s => s.name))
      
      // 一次性加载所有sheet，它们会自动显示在表格内部的tab栏
      spreadsheet.loadData(allSheetsData)
      console.log('[SpreadsheetEditor] ✓ 所有sheet加载成功！')
      console.log('[SpreadsheetEditor] sheet数量:', allSheetsData.sheets.length)

    } catch (error) {
      console.error('[SpreadsheetEditor] 初始化失败:', error)
      console.error('[SpreadsheetEditor] 错误详情:', error.stack)
    }

    return () => {
      if (spreadsheetRef.current) {
        try {
          spreadsheetRef.current.destroy()
          spreadsheetRef.current = null
        } catch (e) {
          console.warn('[SpreadsheetEditor] 清理失败:', e)
        }
      }
    }
  }, [data])

  if (!data || !data.sheets || data.sheets.length === 0) {
    return <div className="spreadsheet-container">暂无数据</div>
  }

  return (
    <div className="spreadsheet-container">
      <div ref={containerRef} className="x-spreadsheet-container"></div>
    </div>
  )
}

export default SpreadsheetEditor
