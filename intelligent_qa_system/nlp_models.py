"""
NLP模型加载和调用工具类
整合文本分类、情感分析、机器翻译模型
"""
import os
import sys
import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import sequence
import jieba
from collections import Counter


class NLPModels:
    """NLP模型管理类"""
    
    def __init__(self):
        self.text_classifier = None
        self.sentiment_analyzer_dicts = None
        self.text_classifier_vocab = None
        self.text_classifier_categories = None
        # 获取nlp_deeplearn路径（假设在上级目录的兄弟目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        self.nlp_deeplearn_path = os.path.join(parent_dir, 'nlp_deeplearn')
        
    def load_text_classifier(self):
        """加载文本分类模型"""
        try:
            # 路径配置
            base_dir = os.path.join(self.nlp_deeplearn_path, 'data')
            vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')
            model_dir = os.path.join(self.nlp_deeplearn_path, 'tmp', 'my_model.h5')
            
            if not os.path.exists(vocab_dir) or not os.path.exists(model_dir):
                print(f"文本分类模型文件不存在: vocab={vocab_dir}, model={model_dir}")
                return False
            
            # 读取词汇表
            with open(vocab_dir, 'r', encoding='utf-8', errors='ignore') as f:
                words = [i.strip() for i in f.readlines()]
            self.text_classifier_vocab = dict(zip(words, range(len(words))))
            
            # 读取分类目录
            self.text_classifier_categories = ['体育', '财经', '房产', '家居', '教育', '科技', '时尚', '时政', '游戏', '娱乐']
            
            # 加载模型
            self.text_classifier = load_model(model_dir)
            print("✓ 文本分类模型加载成功")
            return True
        except Exception as e:
            print(f"✗ 加载文本分类模型失败: {str(e)}")
            return False
    
    def load_sentiment_analyzer(self):
        """加载情感分析词典"""
        try:
            # 路径配置
            data_dir = os.path.join(self.nlp_deeplearn_path, 'data')
            neg_file = os.path.join(data_dir, 'neg.xls')
            pos_file = os.path.join(data_dir, 'pos.xls')
            sum_file = os.path.join(data_dir, 'sum.xls')
            
            if not os.path.exists(neg_file) or not os.path.exists(pos_file):
                print("情感分析数据文件不存在，将使用简化词典")
                return False
            
            # 读取并构建词典
            neg = pd.read_excel(neg_file, header=None, index_col=None)
            pos = pd.read_excel(pos_file, header=None, index_col=None)
            
            pos['mark'] = 1
            neg['mark'] = 0
            pn_all = pd.concat([pos, neg], ignore_index=True)
            pn_all[0] = pn_all[0].astype(str)
            
            # 分词
            cut_word = lambda x: list(jieba.cut(x))
            pn_all['words'] = pn_all[0].apply(cut_word)
            
            # 如果有sum.xls，也加入
            if os.path.exists(sum_file):
                comment = pd.read_excel(sum_file)
                if 'rateContent' in comment.columns:
                    comment = comment[comment['rateContent'].notnull()]
                    comment['words'] = comment['rateContent'].apply(cut_word)
                    pn_comment = pd.concat([pn_all['words'], comment['words']], ignore_index=True)
                else:
                    pn_comment = pn_all['words']
            else:
                pn_comment = pn_all['words']
            
            # 构建词典
            w = []
            for i in pn_comment:
                w.extend(i)
            dicts = pd.DataFrame(pd.Series(w).value_counts())
            dicts['id'] = list(range(1, len(dicts)+1))
            self.sentiment_analyzer_dicts = dicts
            
            print("✓ 情感分析词典构建成功")
            return True
        except Exception as e:
            print(f"✗ 加载情感分析词典失败: {str(e)}")
            return False
    
    def classify_text(self, text):
        """文本分类"""
        if not self.text_classifier or not self.text_classifier_vocab:
            return None
        
        try:
            # 预处理
            contents = list(text)
            data_id = [[self.text_classifier_vocab.get(x, 0) for x in contents if x in self.text_classifier_vocab]]
            x_pad = sequence.pad_sequences(data_id, maxlen=600)
            
            # 预测
            y_pred = self.text_classifier.predict(x_pad, verbose=0)
            predicted_category = self.text_classifier_categories[np.argmax(y_pred[0])]
            confidence = float(np.max(y_pred[0]))
            
            return {
                'category': predicted_category,
                'confidence': confidence,
                'all_probabilities': {cat: float(prob) for cat, prob in zip(self.text_classifier_categories, y_pred[0])}
            }
        except Exception as e:
            print(f"文本分类失败: {str(e)}")
            return None
    
    def analyze_sentiment(self, text):
        """情感分析（基于词典的方法）"""
        try:
            # 分词
            words = list(jieba.cut(text))
            
            # 扩展的正面词汇表（使用set去重）
            pos_words = {'好', '棒', '喜欢', '满意', '赞', '优秀', '完美', '太好了', '不错', '高兴', 
                        '开心', '快乐', '愉快', '兴奋', '惊喜', '爱', '美好', 
                        '精彩', '出色', '杰出', '很棒', '非常好', '太棒了', '好评',
                        '棒极了'}
            
            # 扩展的负面词汇表（使用set去重）
            neg_words = {'差', '坏', '讨厌', '不满', '糟糕', '失望', '难过', '伤心', '生气', '愤怒', 
                        '不好', '沮丧', '痛苦', '难受', '厌恶',
                        '很差', '非常差', '太差了', '差评',
                        '糟糕透顶', '让人失望'}
            
            # 统计正面和负面词汇
            pos_count = sum(1 for word in words if word in pos_words)
            neg_count = sum(1 for word in words if word in neg_words)
            
            # 计算情感倾向和置信度
            total_emotion_words = pos_count + neg_count
            if total_emotion_words == 0:
                sentiment = '中性'
                confidence = 0.5
            elif pos_count > neg_count:
                sentiment = '正面'
                confidence = 0.6 + min(0.35, pos_count / 15)
            elif neg_count > pos_count:
                sentiment = '负面'
                confidence = 0.6 + min(0.35, neg_count / 15)
            else:
                sentiment = '中性'
                confidence = 0.5
            
            # 确保置信度在合理范围内
            confidence = min(0.95, max(0.5, confidence))
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'positive_words': pos_count,
                'negative_words': neg_count
            }
        except Exception as e:
            print(f"情感分析失败: {str(e)}")
            return {
                'sentiment': '中性',
                'confidence': 0.5,
                'positive_words': 0,
                'negative_words': 0
            }
