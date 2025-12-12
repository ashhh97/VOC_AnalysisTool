import openpyxl
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import requests
import json
import re
import os

# 尝试导入配置文件
try:
    from config import HF_API_TOKEN, TONGYI_API_KEY, API_PRIORITY
except ImportError:
    # 如果配置文件不存在，使用默认值
    HF_API_TOKEN = None
    TONGYI_API_KEY = None
    API_PRIORITY = ["hf_token", "tongyi", "hf_free", "local"]

class VOCAnalyzer:
    def __init__(self):
        # 加载API配置
        self.hf_token = HF_API_TOKEN or os.getenv('HF_API_TOKEN')
        self.tongyi_key = TONGYI_API_KEY or os.getenv('TONGYI_API_KEY')
        self.api_priority = API_PRIORITY
        
        # Hugging Face API端点（使用Token）
        self.hf_api_urls = [
            "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct",
            "https://api-inference.huggingface.co/models/Qwen/Qwen2-7B-Instruct",
            "https://api-inference.huggingface.co/models/Qwen/Qwen2-1.5B-Instruct",
            "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-14B-Instruct",
        ]
        
        # Hugging Face免费API端点（无需Token，但可能不可用）
        self.hf_free_api_urls = [
            "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct",
            "https://api-inference.huggingface.co/models/Qwen/Qwen2-7B-Instruct",
            "https://api-inference.huggingface.co/models/Qwen/Qwen2-1.5B-Instruct",
        ]
        
        # 通义千问API端点
        self.tongyi_api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        self.current_api_index = 0
        self.use_local_analysis = False
        self.stop_flag = None
        
        # 打印配置信息
        print(f"[VOC Analyzer] 初始化完成")
        if self.hf_token:
            print(f"[VOC Analyzer] Hugging Face Token已配置")
        if self.tongyi_key:
            print(f"[VOC Analyzer] 通义千问API Key已配置")
        print(f"[VOC Analyzer] API优先级: {', '.join(self.api_priority)}")
    
    def set_stop_flag(self, stop_flag):
        """设置停止标志"""
        self.stop_flag = stop_flag
    
    def analyze_with_ai(self, text):
        """使用Qwen AI分析文本情感和分类，按优先级尝试不同的API"""
        if self.use_local_analysis:
            return self.local_analyze(text)
        
        # 构造prompt
        prompt = f"""请分析以下用户反馈，返回JSON格式结果：
{{
    "sentiment": "正面/负面/中性",
    "category": "功能问题/性能问题/界面问题/体验问题/服务问题/价格问题/其他问题"
}}

用户反馈：{text}

请只返回JSON，不要其他内容："""
        
        # 按优先级尝试不同的API
        for api_type in self.api_priority:
            if api_type == "hf_token" and self.hf_token:
                result = self._try_huggingface_token(prompt, text)
                if result:
                    return result
            elif api_type == "tongyi" and self.tongyi_key:
                result = self._try_tongyi_api(prompt, text)
                if result:
                    return result
            elif api_type == "hf_free":
                result = self._try_huggingface_free(prompt, text)
                if result:
                    return result
            elif api_type == "local":
                print("[Qwen API] 使用本地分析")
                return self.local_analyze(text)
        
        # 所有API都失败，使用本地分析
        print("[Qwen API] 所有API都不可用，使用本地分析")
        return self.local_analyze(text)
    
    def _try_huggingface_token(self, prompt, text):
        """尝试使用Hugging Face API Token"""
        for api_url in self.hf_api_urls:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.hf_token}"
                }
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 150,
                        "temperature": 0.3,
                        "return_full_text": False
                    }
                }
                
                print(f"[HF Token API] 尝试调用: {api_url}")
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[HF Token API] 调用成功")
                    return self.parse_ai_result(result, text)
                elif response.status_code == 503:
                    error_info = response.json() if response.content else {}
                    estimated_time = error_info.get('estimated_time', 0)
                    print(f"[HF Token API] 模型正在加载，预计等待时间: {estimated_time}秒")
                    if estimated_time and estimated_time < 30:
                        import time
                        time.sleep(min(estimated_time + 2, 30))
                        retry_response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                        if retry_response.status_code == 200:
                            return self.parse_ai_result(retry_response.json(), text)
                    continue
                else:
                    print(f"[HF Token API] 错误 {response.status_code}: {response.text[:200]}")
                    continue
            except Exception as e:
                print(f"[HF Token API] 调用失败: {e}")
                continue
        return None
    
    def _try_tongyi_api(self, prompt, text):
        """尝试使用通义千问API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.tongyi_key}"
            }
            payload = {
                "model": "qwen-turbo",  # 或 "qwen-plus", "qwen-max"
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "max_tokens": 150,
                    "temperature": 0.3
                }
            }
            
            print(f"[通义千问API] 尝试调用...")
            response = requests.post(self.tongyi_api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('output') and result['output'].get('choices'):
                    generated_text = result['output']['choices'][0]['message']['content']
                    print(f"[通义千问API] 调用成功")
                    # 解析结果
                    return self.parse_ai_result({'generated_text': generated_text}, text)
                else:
                    print(f"[通义千问API] 响应格式异常: {result}")
                    return None
            else:
                print(f"[通义千问API] 错误 {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"[通义千问API] 调用失败: {e}")
            return None
    
    def _try_huggingface_free(self, prompt, text):
        """尝试使用Hugging Face免费API（无需Token）"""
        for api_url in self.hf_free_api_urls:
            try:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 150,
                        "temperature": 0.3,
                        "return_full_text": False
                    }
                }
                
                print(f"[HF Free API] 尝试调用: {api_url}")
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[HF Free API] 调用成功")
                    return self.parse_ai_result(result, text)
                elif response.status_code == 503:
                    error_info = response.json() if response.content else {}
                    estimated_time = error_info.get('estimated_time', 0)
                    print(f"[HF Free API] 模型正在加载，预计等待时间: {estimated_time}秒")
                    if estimated_time and estimated_time < 30:
                        import time
                        time.sleep(min(estimated_time + 2, 30))
                        retry_response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                        if retry_response.status_code == 200:
                            return self.parse_ai_result(retry_response.json(), text)
                    continue
                elif response.status_code == 410:
                    print(f"[HF Free API] 模型不可用(410 - Gone)")
                    continue
                elif response.status_code == 429:
                    print(f"[HF Free API] 请求过多(429)")
                    import time
                    time.sleep(2)
                    continue
                else:
                    print(f"[HF Free API] 错误 {response.status_code}: {response.text[:200]}")
                    continue
            except Exception as e:
                print(f"[HF Free API] 调用失败: {e}")
                continue
        return None
    
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
        """解析Qwen返回的结果"""
        try:
            # Qwen2.5 API返回格式可能是列表或字典
            generated_text = ""
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    generated_text = result[0].get('generated_text', '')
                else:
                    generated_text = str(result[0])
            elif isinstance(result, dict):
                generated_text = result.get('generated_text', '')
            else:
                generated_text = str(result)
            
            # 尝试从返回文本中提取JSON
            # 查找JSON对象
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', generated_text)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                sentiment = parsed.get('sentiment', '中性')
                category = parsed.get('category', '其他问题')
                
                # 标准化情感值
                if '正面' in sentiment or 'positive' in sentiment.lower() or '积极' in sentiment:
                    sentiment = '正面'
                elif '负面' in sentiment or 'negative' in sentiment.lower() or '消极' in sentiment:
                    sentiment = '负面'
                else:
                    sentiment = '中性'
                
                # 验证分类是否有效
                valid_categories = ['功能问题', '性能问题', '界面问题', '体验问题', '服务问题', '价格问题', '其他问题']
                if category not in valid_categories:
                    # 尝试从文本中匹配分类
                    category = self.categorize_text(text)
                
                return {
                    'sentiment': sentiment,
                    'category': category,
                    'confidence': 0.85
                }
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}, 返回文本: {generated_text[:100]}")
        except Exception as e:
            print(f"解析Qwen结果失败: {e}, 使用本地分析")
        
        # 如果解析失败，使用本地分析
        return self.local_analyze(text)
    
    def analyze_and_categorize(self, file_path, progress_callback=None):
        """分析VOC文件并分类
        
        Args:
            file_path: Excel文件路径
            progress_callback: 进度回调函数，接收 (current, total, message) 参数
        """
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
            if progress_callback:
                progress_callback(0, 100, f'正在读取工作表 "{sheet_name}"...')
            
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
            
            total_rows = len(rows_data)
            if progress_callback:
                progress_callback(0, total_rows, f'开始分析工作表 "{sheet_name}"，共 {total_rows} 条反馈...')
            
            # 对反馈进行分类
            categorized_data = {}
            for idx, row_info in enumerate(rows_data, 1):
                # 检查是否应该停止
                if self.stop_flag and self.stop_flag.is_set():
                    print(f"[停止分析] 检测到停止标志，终止分析")
                    raise KeyboardInterrupt("分析被用户终止")
                
                # 更新进度
                if progress_callback:
                    progress_callback(idx, total_rows, f'正在分析第 {idx}/{total_rows} 条反馈...')
                
                analysis = self.analyze_with_ai(row_info['feedback'])
                
                # 再次检查停止标志
                if self.stop_flag and self.stop_flag.is_set():
                    print(f"[停止分析] 检测到停止标志，终止分析")
                    raise KeyboardInterrupt("分析被用户终止")
                
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
    

