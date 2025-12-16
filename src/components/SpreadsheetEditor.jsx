import React from 'react'
import { Workbook } from "@fortune-sheet/react"
import "@fortune-sheet/react/dist/index.css"
import './SpreadsheetEditor.css'

// 简单的防抖控制
// (Moving ref inside component)

function SpreadsheetEditor({ data, onRecalculate }) {
  // console.log('[SpreadsheetEditor] 收到数据:', data)

  if (!data || !data.sheets || data.sheets.length === 0) {
    return <div className="spreadsheet-container">暂无数据</div>
  }

  // 简单的防抖控制
  const lastLogRef = React.useRef({ time: 0, r: -1 })

  const handleRecalculateClick = () => {
    if (!onRecalculate) return

    // 提取当前表格数据
    // 假设分析结果在第二个sheet
    const analysisSheet = data.sheets.find(s => s.name === '分析结果')
    if (!analysisSheet) {
      console.error('[Recalculate] Analysis sheet not found')
      return
    }

    console.log('[Recalculate] Extracting data from sheet:', analysisSheet.name)
    onRecalculate(analysisSheet.celldata)
  }

  const handleOp = (op) => {
    // console.log('[SpreadsheetEditor] Operation:', op)

    // 监听行移动操作 (Move Rows)
    // FortuneSheet/Luckysheet 'mv' operation: { "op": "mv", "r": [start, end], "t": target_index }

    // 简化逻辑：我们只关心 'mv' (move) 操作
    if (op.op === 'mv') {
      const targetIndex = op.v.t
      const sourceIndices = op.v.r // [startRow, endRow]

      console.log(`[Implicit Feedback] Row moved to index ${targetIndex}`)

      // 延迟一点执行，确保数据已更新
      setTimeout(() => {
        const sheet = data.sheets[0]
        const prevRowIndex = targetIndex - 1
        if (prevRowIndex < 0) return

        const getCellValue = (rowIndex, colIndex) => {
          const cell = sheet.celldata.find(c => c.r === rowIndex && c.c === colIndex)
          return cell ? cell.v.v : null
        }

        const prevCategory = getCellValue(prevRowIndex, 0)
        const targetCategory = getCellValue(targetIndex, 0)

        // 如果上一行有分类，且当前行分类为空或不同
        if (prevCategory && prevCategory !== targetCategory) {
          console.log(`[Implicit Feedback] Inference: Row ${targetIndex} should be ${prevCategory} (Neighbor: Row ${prevRowIndex})`)
          console.log(`[自动归类] 已根据上下文将第 ${targetIndex + 1} 行归类为: ${prevCategory}`)

          const vocText = getCellValue(targetIndex, 6)

          const payload = {
            event_type: "drag_inference",
            voc_text: vocText || "Unknown",
            inferred_label: prevCategory,
            original_label: targetCategory || "None",
            confidence_weight: 0.8,
            timestamp: new Date().toISOString()
          }

          // 防抖
          const now = Date.now()
          if (now - lastLogRef.current.time < 2000 && lastLogRef.current.r === targetIndex) {
            return
          }
          lastLogRef.current = { time: now, r: targetIndex }

          // 发送请求
          fetch('/api/log_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          }).then(res => {
            console.log('[Implicit Feedback] Logged to backend')
          }).catch(err => {
            console.error('[Implicit Feedback] Log failed', err)
          })
        }
      }, 500)
    }
  }

  return (
    <div className="spreadsheet-container">
      {onRecalculate && (
        <div style={{ padding: '10px', background: '#f5f5f5', borderBottom: '1px solid #ddd' }}>
          <button
            onClick={handleRecalculateClick}
            style={{
              padding: '8px 16px',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            📊 重新计算统计
          </button>
          <span style={{ marginLeft: '10px', color: '#666', fontSize: '12px' }}>
            手动调整分类后，点击此按钮重新计算用户数量和占比
          </span>
        </div>
      )}
      <Workbook
        key={data.fileId + '-' + data.sheets.length}
        data={data.sheets}
        onChange={(d) => console.log('Data changed:', d)}
        onOp={handleOp}
      />
    </div>
  )
}

export default SpreadsheetEditor
