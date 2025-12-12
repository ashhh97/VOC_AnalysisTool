import React, { useEffect, useRef } from 'react'
import Spreadsheet from 'x-data-spreadsheet'
// 导入编译后的CSS
import 'x-data-spreadsheet/dist/xspreadsheet.css'
import './SpreadsheetEditor.css'

function SpreadsheetEditor({ data }) {
  const containerRef = useRef(null)
  const spreadsheetRef = useRef(null)

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
      
      // 创建Spreadsheet实例
      const spreadsheet = new Spreadsheet(containerRef.current, {
        mode: 'edit', // 编辑模式
        showToolbar: true,
        showGrid: true,
        showContextmenu: true,
        view: {
          height: () => containerRef.current.clientHeight,
          width: () => containerRef.current.clientWidth,
        },
      })

      spreadsheetRef.current = spreadsheet

      // 转换数据格式
      // x-data-spreadsheet需要的数据格式：{ rows: { 0: { cells: { 0: { text: 'value' } } } } }
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
        
        return { rows }
      }

      // 加载第一个sheet的数据
      if (data.sheets.length > 0) {
        const firstSheet = data.sheets[0]
        console.log('[SpreadsheetEditor] 加载第一个sheet:', firstSheet.name)
        console.log('[SpreadsheetEditor] celldata数量:', firstSheet.celldata?.length || 0)
        
        const convertedData = convertSheetData(firstSheet)
        console.log('[SpreadsheetEditor] 转换后的数据行数:', Object.keys(convertedData.rows).length)
        
        spreadsheet.loadData(convertedData)
        console.log('[SpreadsheetEditor] ✓ 数据加载成功！')
      }

      // 如果有多个sheet，可以添加sheet切换功能
      if (data.sheets.length > 1) {
        console.log('[SpreadsheetEditor] 检测到多个sheet，当前只显示第一个')
        // x-data-spreadsheet本身不支持多sheet，但可以后续扩展
      }

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

  return (
    <div className="spreadsheet-container">
      <div ref={containerRef} className="x-spreadsheet-container"></div>
    </div>
  )
}

export default SpreadsheetEditor
