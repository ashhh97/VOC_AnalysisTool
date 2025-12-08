from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import openpyxl
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import json
from voc_analyzer import VOCAnalyzer

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

analyzer = VOCAnalyzer()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 保存文件
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f'{file_id}.xlsx')
    file.save(file_path)
    
    # 读取Excel文件并转换为Luckysheet格式
    try:
        wb = load_workbook(file_path)
        sheets_data = []
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            cells = []
            
            # 读取所有有数据的单元格
            for row_idx, row in enumerate(ws.iter_rows(values_only=False), start=1):
                for col_idx, cell in enumerate(row, start=1):
                    if cell.value is not None:
                        cells.append({
                            'r': row_idx - 1,
                            'c': col_idx - 1,
                            'v': {
                                'v': cell.value,
                                'm': str(cell.value),
                                'ct': {'fa': 'General', 't': 'g'}
                            }
                        })
            
            # 设置列宽
            column = []
            for col_idx in range(1, ws.max_column + 1):
                col_letter = get_column_letter(col_idx)
                width = ws.column_dimensions[col_letter].width if ws.column_dimensions[col_letter].width else 73
                column.append({ 'wch': width })
            
            sheet_data = {
                'name': sheet_name,
                'index': len(sheets_data),
                'order': len(sheets_data),
                'status': 1,
                'celldata': cells,
                'config': {
                    'columnlen': column,
                    'rowlen': {}
                },
                'scrollLeft': 0,
                'scrollTop': 0,
                'luckysheet_select_save': [],
                'calc chain': [],
                'isPivotTable': False,
                'pivotTable': {},
                'filter_select': None,
                'filter': None,
                'luckysheet_conditionformat_save': [],
                'frozen': {},
                'chart': [],
                'zoomRatio': 1,
                'image': [],
                'showGridLines': 1,
                'dataVerification': {}
            }
            sheets_data.append(sheet_data)
        
        return jsonify({
            'fileId': file_id,
            'sheets': sheets_data,
            'originalSheets': wb.sheetnames
        })
    except Exception as e:
        return jsonify({'error': f'处理文件失败: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_voc():
    data = request.json
    file_id = data.get('fileId')
    
    if not file_id:
        return jsonify({'error': '缺少fileId'}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, f'{file_id}.xlsx')
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    
    try:
        # 分析VOC数据
        analyzed_sheets = analyzer.analyze_and_categorize(file_path)
        
        return jsonify({
            'fileId': file_id,
            'sheets': analyzed_sheets
        })
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

