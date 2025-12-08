import openpyxl
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import requests
import json
import re

class VOCAnalyzer:
    def __init__(self):
        # 使用Hugging Face的免费API（无需API key，但有限制）
        # 或者可以使用Ollama本地模型
        self.api_url = "https://api-inference.huggingface.co/models/uer/roberta-base-finetuned-chinanews-chinese"
        # 备用：使用简单的规则+关键词匹配（如果API不可用）
        self.use_local_analysis = False
    
    def analyze_with_ai(self, text):
        """使用AI分析文本情感和分类"""
        if self.use_local_analysis:
            return self.local_analyze(text)
        
        try:
            # 尝试使用Hugging Face API
            headers = {"Content-Type": "application/json"}
            payload = {"inputs": text}
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                # 解析结果
                return self.parse_ai_result(result, text)
            else:
                # API不可用时使用本地分析
                return self.local_analyze(text)
        except Exception as e:
            print(f"AI分析失败，使用本地分析: {e}")
            return self.local_analyze(text)
    
    def local_analyze(self, text):
        """本地规则分析（备用方案）"""
        text_lower = text.lower()
        
        # 情感分析关键词（更全面的中文关键词）
        positive_keywords = ['好', '满意', '喜欢', '推荐', '优秀', '棒', '赞', '不错', '很好', '完美', 
                            '赞', '给力', '好用', '方便', '快捷', '流畅', '清晰', '美观', '实用', 
                            '贴心', '专业', '高效', '稳定', '可靠', '值得', '超值', '惊喜']
        negative_keywords = ['差', '不好', '失望', '问题', '错误', '慢', '卡', '崩溃', 'bug', '故障',
                            '糟糕', '垃圾', '难用', '复杂', '麻烦', '延迟', '卡顿', '闪退', '死机',
                            '不兼容', '缺失', '不足', '缺陷', '漏洞', '不安全', '贵', '不值']
        
        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)
        
        # 判断情感
        if positive_count > negative_count and positive_count > 0:
            sentiment = '正面'
        elif negative_count > 0:
            sentiment = '负面'
        else:
            sentiment = '中性'
        
        # 简单分类
        category = self.categorize_text(text)
        
        return {
            'sentiment': sentiment,
            'category': category,
            'confidence': 0.7
        }
    
    def categorize_text(self, text):
        """简单的文本分类"""
        text_lower = text.lower()
        
        categories = {
            '功能问题': ['功能', '不能', '无法', '不支持', '缺少', '没有', '缺失', '不完善', '不完整', '缺少功能'],
            '性能问题': ['慢', '卡', '延迟', '加载', '响应', '卡顿', '卡死', '运行慢', '速度', '性能', '优化'],
            '界面问题': ['界面', 'UI', '设计', '布局', '显示', '美观', '样式', '颜色', '字体', '图标', '按钮'],
            '体验问题': ['体验', '使用', '操作', '流程', '方便', '易用', '简单', '复杂', '麻烦', '顺手', '习惯'],
            '服务问题': ['服务', '客服', '支持', '帮助', '响应', '态度', '处理', '售后', '咨询', '反馈'],
            '价格问题': ['价格', '费用', '收费', '贵', '便宜', '性价比', '价值', '划算', '不值', '定价'],
            '其他问题': []
        }
        
        # 计算每个类别的匹配分数
        category_scores = {}
        for category, keywords in categories.items():
            if category == '其他问题':
                continue
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                category_scores[category] = score
        
        # 返回得分最高的类别
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return '其他问题'
    
    def parse_ai_result(self, result, text):
        """解析AI返回结果"""
        # 这里需要根据实际API返回格式调整
        # 简化处理，使用本地分析
        return self.local_analyze(text)
    
    def analyze_and_categorize(self, file_path):
        """分析VOC文件并分类"""
        wb = load_workbook(file_path)
        sheets_data = []
        
        # 处理每个sheet
        for sheet_idx, sheet_name in enumerate(wb.sheetnames):
            ws = wb[sheet_name]
            
            # 读取原始数据
            rows_data = []
            headers = []
            
            # 读取第一行作为表头
            first_row = next(ws.iter_rows(values_only=True), None)
            if first_row:
                headers = [str(cell) if cell else f'列{i+1}' for i, cell in enumerate(first_row)]
            
            # 读取数据行（假设用户反馈在第二列，可以根据实际情况调整）
            feedback_column_idx = 1  # 默认第二列（索引从0开始）
            if len(headers) > 1:
                # 尝试找到包含"反馈"、"意见"、"评论"等关键词的列
                for idx, header in enumerate(headers):
                    if any(keyword in str(header).lower() for keyword in ['反馈', '意见', '评论', '评价', '内容']):
                        feedback_column_idx = idx
                        break
            
            # 读取所有数据行
            for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
                if row_idx == 1:
                    continue  # 跳过表头
                
                if len(row) > feedback_column_idx and row[feedback_column_idx]:
                    feedback_text = str(row[feedback_column_idx]).strip()
                    if feedback_text:
                        rows_data.append({
                            'row_data': list(row),
                            'feedback': feedback_text,
                            'original_row': row_idx
                        })
            
            # 对反馈进行分类
            categorized_data = {}
            for row_info in rows_data:
                analysis = self.analyze_with_ai(row_info['feedback'])
                category = analysis['category']
                sentiment = analysis['sentiment']
                
                key = f"{category}_{sentiment}"
                if key not in categorized_data:
                    categorized_data[key] = {
                        'category': category,
                        'sentiment': sentiment,
                        'rows': []
                    }
                categorized_data[key]['rows'].append(row_info)
            
            # 创建新的sheet数据
            new_sheet_name = f"{sheet_name}_分析结果"
            
            # 先添加原始sheet
            original_sheet_data = self.create_sheet_data(ws, sheet_name, sheet_idx)
            sheets_data.append(original_sheet_data)
            
            # 创建分析结果sheet
            analyzed_sheet_data = self.create_analyzed_sheet(
                headers, categorized_data, new_sheet_name, len(sheets_data)
            )
            sheets_data.append(analyzed_sheet_data)
        
        return sheets_data
    
    def create_sheet_data(self, ws, sheet_name, index):
        """创建原始sheet的Luckysheet数据"""
        cells = []
        
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
        
        column = []
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            width = ws.column_dimensions[col_letter].width if ws.column_dimensions[col_letter].width else 73
            column.append({ 'wch': width })
        
        return {
            'name': sheet_name,
            'index': index,
            'order': index,
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
    
    def create_analyzed_sheet(self, headers, categorized_data, sheet_name, index):
        """创建分析结果sheet"""
        cells = []
        merge_cells = []
        current_row = 0
        
        # 添加表头
        for col_idx, header in enumerate(headers):
            cells.append({
                'r': current_row,
                'c': col_idx,
                'v': {
                    'v': header,
                    'm': str(header),
                    'ct': {'fa': 'General', 't': 'g'}
                }
            })
        current_row += 1
        
        # 按分类添加数据
        for key in sorted(categorized_data.keys()):
            category_info = categorized_data[key]
            category = category_info['category']
            sentiment = category_info['sentiment']
            num_rows = len(category_info['rows'])
            
            if num_rows > 0:
                # 添加分类标题行（第一个单元格：分类名称）
                cells.append({
                    'r': current_row,
                    'c': 0,
                    'v': {
                        'v': category,
                        'm': category,
                        'ct': {'fa': 'General', 't': 'g'}
                    }
                })
                
                # 第二个单元格：情感
                cells.append({
                    'r': current_row,
                    'c': 1,
                    'v': {
                        'v': sentiment,
                        'm': sentiment,
                        'ct': {'fa': 'General', 't': 'g'}
                    }
                })
                
                # 记录合并单元格信息
                # 合并第一列（分类名称）
                merge_cells.append({
                    'r': current_row,
                    'c': 0,
                    'rs': num_rows,
                    'cs': 1
                })
                
                # 合并第二列（情感）
                merge_cells.append({
                    'r': current_row,
                    'c': 1,
                    'rs': num_rows,
                    'cs': 1
                })
                
                # 添加该分类下的所有行
                for row_info in category_info['rows']:
                    for col_idx, cell_value in enumerate(row_info['row_data']):
                        if cell_value is not None:
                            cells.append({
                                'r': current_row,
                                'c': col_idx,
                                'v': {
                                    'v': cell_value,
                                    'm': str(cell_value),
                                    'ct': {'fa': 'General', 't': 'g'}
                                }
                            })
                    current_row += 1
        
        # 设置列宽
        column = []
        for col_idx in range(len(headers)):
            column.append({ 'wch': 100 })
        
        return {
            'name': sheet_name,
            'index': index,
            'order': index,
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
            'dataVerification': {},
            'merge': merge_cells if merge_cells else {}
        }
    

