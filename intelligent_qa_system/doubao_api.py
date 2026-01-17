"""
豆包API调用模块
"""
import http.client
import json


class DoubaoAPI:
    """豆包API调用类"""
    
    def __init__(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name
        self.host = "ark.cn-beijing.volces.com"
        self.endpoint = "/api/v3/chat/completions"
    
    def chat(self, user_message, system_message="你是一个智能助手，可以帮助用户回答问题、分析文本、进行翻译等任务。"):
        """调用豆包API进行对话"""
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.host)
            payload = json.dumps({
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            })
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            conn.request("POST", self.endpoint, payload, headers)
            res = conn.getresponse()
            data = res.read()
            response_data = json.loads(data.decode("utf-8"))
            
            # 提取回复内容
            if 'choices' in response_data and len(response_data['choices']) > 0:
                reply = response_data['choices'][0]['message']['content']
                return {
                    'success': True,
                    'reply': reply,
                    'raw_response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': '未获取到有效回复',
                    'raw_response': response_data
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_response': None
            }
        finally:
            if conn:
                conn.close()
    
    def translate(self, text, target_lang='en'):
        """使用豆包API进行翻译"""
        if target_lang == 'en':
            prompt = f"请将以下中文翻译成英文：{text}"
        else:
            prompt = f"Please translate the following English to Chinese: {text}"
        
        result = self.chat(prompt, "你是一个专业的翻译助手。")
        if result['success']:
            return {
                'original': text,
                'translated': result['reply'],
                'target_lang': target_lang
            }
        else:
            return {
                'original': text,
                'translated': f'翻译失败：{result.get("error", "未知错误")}',
                'target_lang': target_lang
            }
