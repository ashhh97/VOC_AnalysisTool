import React from 'react'
import { Workbook } from "@fortune-sheet/react"
import "@fortune-sheet/react/dist/index.css"
import './SpreadsheetEditor.css'

function SpreadsheetEditor({ data }) {
  console.log('[SpreadsheetEditor] 收到数据:', data)

  if (!data || !data.sheets || data.sheets.length === 0) {
    return <div className="spreadsheet-container">暂无数据</div>
  }

  return (
    <div className="spreadsheet-container">
      <Workbook
        key={data.fileId + '-' + data.sheets.length}
        data={data.sheets}
        onChange={(d) => console.log('Data changed:', d)}
      />
    </div>
  )
}

export default SpreadsheetEditor
