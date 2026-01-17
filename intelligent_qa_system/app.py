"""
多功能智能问答系统
整合豆包API、文本分类、情感分析、机器翻译
"""
from flask import Flask, render_template, request, jsonify
from doubao_api import DoubaoAPI
from nlp_models import NLPModels
import re


# 初始化Flask应用
app = Flask(__name__, static_url_path='/static')

# 初始化豆包API
DOUBAO_API_KEY = '5fe8c115-d78c-4fae-90be-6a2075f29f7e'
DOUBAO_MODEL = 'doubao-seed-1-6-lite-251015'
doubao = DoubaoAPI(DOUBAO_API_KEY, DOUBAO_MODEL)

# 初始化NLP模型
nlp_models = NLPModels()

# 加载模型（如果可用）
print("=" * 60)
print("正在初始化多功能智能问答系统...")
print("=" * 60)
print("\n正在加载NLP模型...")
try:
    if nlp_models.load_text_classifier():
        print("  ✓ 文本分类模型已加载")
    else:
        print("  ✗ 文本分类模型不可用（将跳过分类功能）")
except Exception as e:
    print(f"  ✗ 文本分类模型加载失败: {str(e)}")

try:
    if nlp_models.load_sentiment_analyzer():
        print("  ✓ 情感分析词典已构建")
    else:
        print("  ✗ 情感分析词典不可用（将使用简化版本）")
except Exception as e:
    print(f"  ✗ 情感分析词典加载失败: {str(e)}")

print("\n✓ 系统初始化完成！")
print("=" * 60)
print("功能包括：")
print("  1. 🤖 豆包API智能问答")
print("  2. 📊 文本分类（10个类别）")
print("  3. 😊 情感分析（正面/负面/中性）")
print("  4. 🌐 机器翻译（使用豆包API）")
print("  5. 🎯 智能意图识别")
print("=" * 60)
print("\n系统将在 http://127.0.0.1:8808 启动\n")


def detect_function(user_input):
    """智能检测用户意图，判断应该使用哪个功能"""
    user_input_lower = user_input.lower()
    
    # 翻译意图关键词
    translate_keywords = ['翻译', 'translate', '译成', '转换成', '翻译成']
    if any(keyword in user_input or keyword.lower() in user_input_lower for keyword in translate_keywords):
        return 'translate'
    
    # 情感分析意图关键词
    sentiment_keywords = ['情感', '情绪', '感觉', 'sentiment', '心情', '态度', '评价']
    if any(keyword in user_input or keyword.lower() in user_input_lower for keyword in sentiment_keywords):
        return 'sentiment'
    
    # 文本分类意图关键词
    classify_keywords = ['分类', '类别', '属于', '是什么类型', 'category', 'classify']
    if any(keyword in user_input or keyword.lower() in user_input_lower for keyword in classify_keywords):
        return 'classify'
    
    # 如果包含中英文混合，可能是翻译需求
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_input)
    has_english = bool(re.search(r'[a-zA-Z]', user_input))
    if has_chinese and has_english and len(user_input) < 50:
        return 'translate'
    
    # 默认使用问答
    return 'qa'


def format_response_with_analysis(user_input, reply, classification=None, sentiment=None):
    """格式化回复，包含分析结果"""
    response_parts = []
    
    # 添加主要回复
    response_parts.append(reply)
    
    # 添加分类结果
    if classification:
        category = classification.get('category', '未知')
        confidence = classification.get('confidence', 0)
        response_parts.append(f"\n📊 文本分类: {category} (置信度: {confidence:.2%})")
    
    # 添加情感分析结果
    if sentiment:
        sentiment_type = sentiment.get('sentiment', '未知')
        sentiment_conf = sentiment.get('confidence', 0)
        response_parts.append(f"😊 情感分析: {sentiment_type} (置信度: {sentiment_conf:.2%})")
    
    return "\n".join(response_parts)


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/message', methods=['POST'])
def reply():
    """智能问答接口"""
    try:
        # 获取用户输入
        user_msg = request.form.get('msg', '').strip()
        
        if not user_msg:
            return jsonify({'text': '请输入您的问题或需要处理的内容。', 'type': 'error'})
        
        # 检测用户意图
        function_type = detect_function(user_msg)
        
        result = {
            'text': '',
            'type': function_type,
            'analysis': {}
        }
        
        # 根据意图执行相应功能
        if function_type == 'translate':
            # 翻译功能
            translate_text = user_msg
            for keyword in ['翻译', 'translate', '译成', '转换成', '翻译成']:
                if keyword in translate_text:
                    translate_text = translate_text.split(keyword)[-1].strip()
                    break
            
            # 判断目标语言
            target_lang = 'en'
            if '英文' in user_msg or 'english' in user_msg.lower() or '英语' in user_msg:
                target_lang = 'en'
            elif '中文' in user_msg or 'chinese' in user_msg.lower() or '汉语' in user_msg:
                target_lang = 'zh'
            
            # 使用豆包API进行翻译
            translation = doubao.translate(translate_text, target_lang)
            result['text'] = f"🌐 翻译结果:\n原文: {translation['original']}\n译文: {translation['translated']}"
            result['analysis']['translation'] = translation
        
        elif function_type == 'sentiment':
            # 情感分析
            analyze_text = user_msg
            for keyword in ['情感', '情绪', '感觉', 'sentiment', '心情', '态度', '评价']:
                if keyword in analyze_text:
                    analyze_text = analyze_text.split(keyword)[-1].strip()
                    break
            
            sentiment_result = nlp_models.analyze_sentiment(analyze_text)
            if sentiment_result:
                sentiment_type = sentiment_result.get('sentiment', '未知')
                sentiment_conf = sentiment_result.get('confidence', 0)
                pos_words = sentiment_result.get('positive_words', 0)
                neg_words = sentiment_result.get('negative_words', 0)
                
                emoji = '😊' if sentiment_type == '正面' else '😞' if sentiment_type == '负面' else '😐'
                result['text'] = f"{emoji} 情感分析结果:\n情感倾向: {sentiment_type}\n置信度: {sentiment_conf:.2%}\n正面词汇数: {pos_words}\n负面词汇数: {neg_words}"
                result['analysis']['sentiment'] = sentiment_result
            else:
                result['text'] = "情感分析功能暂时不可用，请稍后再试。"
        
        elif function_type == 'classify':
            # 文本分类
            classify_text = user_msg
            for keyword in ['分类', '类别', '属于', '是什么类型', 'category', 'classify']:
                if keyword in classify_text:
                    classify_text = classify_text.split(keyword)[-1].strip()
                    break
            
            classification_result = nlp_models.classify_text(classify_text)
            if classification_result:
                category = classification_result.get('category', '未知')
                confidence = classification_result.get('confidence', 0)
                result['text'] = f"📊 文本分类结果:\n类别: {category}\n置信度: {confidence:.2%}"
                result['analysis']['classification'] = classification_result
            else:
                result['text'] = "文本分类功能暂时不可用，请稍后再试。"
        
        else:
            # 默认：智能问答 + 自动分析
            qa_result = doubao.chat(user_msg)
            
            if qa_result['success']:
                reply_text = qa_result['reply']
                
                # 自动执行文本分类和情感分析
                classification = nlp_models.classify_text(user_msg)
                sentiment = nlp_models.analyze_sentiment(user_msg)
                
                # 组合回复
                result['text'] = format_response_with_analysis(user_msg, reply_text, classification, sentiment)
                result['analysis']['classification'] = classification
                result['analysis']['sentiment'] = sentiment
            else:
                result['text'] = f"抱歉，我无法回答这个问题。错误信息: {qa_result.get('error', '未知错误')}"
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'text': f'处理请求时出错: {str(e)}',
            'type': 'error'
        })


@app.route('/analyze', methods=['POST'])
def analyze():
    """专门的文本分析接口"""
    try:
        text = request.form.get('text', '').strip()
        analysis_type = request.form.get('type', 'all')
        
        if not text:
            return jsonify({'error': '请提供要分析的文本'})
        
        result = {}
        
        if analysis_type in ['all', 'classify']:
            classification = nlp_models.classify_text(text)
            result['classification'] = classification
        
        if analysis_type in ['all', 'sentiment']:
            sentiment = nlp_models.analyze_sentiment(text)
            result['sentiment'] = sentiment
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/translate', methods=['POST'])
def translate():
    """专门的翻译接口"""
    try:
        text = request.form.get('text', '').strip()
        target_lang = request.form.get('target_lang', 'en')
        
        if not text:
            return jsonify({'error': '请提供要翻译的文本'})
        
        translation = doubao.translate(text, target_lang)
        return jsonify(translation)
    
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8808, debug=True)
