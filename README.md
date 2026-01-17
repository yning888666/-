# 多功能智能问答系统

一个集成了豆包API、Seq2Seq模型、文本分类、情感分析和机器翻译的智能问答系统。

## 功能特点

1. **🤖 智能问答** - 使用豆包API进行智能对话
2. **🧠 Seq2Seq模型** - 基于注意力机制的Seq2Seq对话生成模型
3. **📊 文本分类** - 自动分类文本到10个类别（体育、财经、房产、家居、教育、科技、时尚、时政、游戏、娱乐）
4. **😊 情感分析** - 分析文本的情感倾向（正面/负面/中性）
5. **🌐 机器翻译** - 支持中英文互译（使用豆包API）
6. **🎯 智能意图识别** - 自动识别用户意图并选择合适的处理方式

## 系统架构

```
intelligent_qa_system/
├── app.py              # 主Flask应用
├── doubao_api.py       # 豆包API调用模块
├── nlp_models.py       # NLP模型加载和调用模块
├── Seq2Seq.py          # Seq2Seq模型定义（Encoder/Decoder/Attention）
├── data_utils.py       # 数据处理工具（语料读取、分词、词典构建）
├── execute.py          # Seq2Seq模型训练脚本
├── data/               # 数据集目录
│   ├── dialog/         # 对话数据（one.txt, two.txt, three.txt, four.txt, five.txt）
│   └── ids/            # 词典数据（all_dict.txt, mydict.txt, source.txt, target.txt）
├── tmp/                # 临时文件目录（处理后数据和模型）
│   └── model/          # 训练好的模型检查点
├── templates/          # HTML模板
│   └── index.html
├── static/             # 静态资源
│   ├── css/
│   ├── js/
│   └── res/
├── requirements.txt    # 依赖列表
└── README.md          # 说明文档
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

确保以下路径存在（相对于项目目录）：
- `../nlp_deeplearn/data/` - 包含NLP模型的数据文件
- `../nlp_deeplearn/tmp/my_model.h5` - 文本分类模型（如果可用）

### 3. 数据处理（可选）

如果需要重新处理数据集并训练Seq2Seq模型：

```bash
# 处理数据集（读取对话语料、分词、构建词典、生成source.txt和target.txt）
python data_utils.py

# 训练Seq2Seq模型（需要较长时间）
python execute.py
```

数据集说明：
- `data/dialog/` - 包含5个对话文件（one.txt, two.txt, three.txt, four.txt, five.txt）
- `data/ids/` - 包含词典文件（all_dict.txt, mydict.txt）和预处理后的问答对（source.txt, target.txt）

### 4. 运行系统

```bash
python app.py
```

系统将在 `http://127.0.0.1:8808` 启动。

## 使用方法

### 智能识别模式（默认）
系统会自动识别用户意图：
- 输入包含"翻译"、"translate"等关键词 → 自动使用翻译功能
- 输入包含"情感"、"情绪"等关键词 → 自动使用情感分析
- 输入包含"分类"、"类别"等关键词 → 自动使用文本分类
- 其他情况 → 使用智能问答，并自动进行文本分类和情感分析

### 示例

1. **智能问答**：
   - 输入："什么是人工智能？"
   - 系统会自动回答，并显示分类和情感分析结果

2. **文本分类**：
   - 输入："分类：这是一篇关于科技的新闻"
   - 系统会返回分类结果

3. **情感分析**：
   - 输入："情感：今天天气真好，我很开心"
   - 系统会返回情感分析结果

4. **机器翻译**：
   - 输入："翻译成英文：你好世界"
   - 系统会返回翻译结果

## API接口

### POST /message
主要消息处理接口
- 参数：`msg` - 用户输入的消息
- 返回：包含回答和分析结果的JSON

### POST /analyze
文本分析接口
- 参数：`text` - 要分析的文本，`type` - 分析类型（all/classify/sentiment）
- 返回：分析结果的JSON

### POST /translate
翻译接口
- 参数：`text` - 要翻译的文本，`target_lang` - 目标语言（en/zh）
- 返回：翻译结果的JSON

## 数据集

本项目包含完整的中文对话数据集：
- **对话文件**：`data/dialog/` 目录下的5个txt文件，包含问答对数据
- **词典文件**：`data/ids/all_dict.txt` - 完整词典列表
- **自定义词典**：`data/ids/mydict.txt` - jieba分词自定义词典
- **预处理数据**：`data/ids/source.txt` 和 `target.txt` - 分词后的问答对

数据集格式：
- 每个对话文件包含多行，奇数行为问题，偶数行为答案
- 数据已使用jieba进行分词处理

## Seq2Seq模型

本项目实现了基于注意力机制的Seq2Seq模型：
- **Encoder**：GRU编码器，将输入序列编码为隐层状态
- **Decoder**：GRU解码器，使用注意力机制生成回复
- **Attention**：Bahdanau注意力机制，提高生成质量

模型参数：
- 词嵌入维度：256
- 隐层神经元数：512
- 最大序列长度：50
- 批次大小：15

## 技术栈

- **后端**：Flask
- **深度学习**：TensorFlow/Keras
- **Seq2Seq模型**：基于GRU和注意力机制的对话生成模型
- **NLP工具**：jieba分词
- **前端**：HTML, CSS, JavaScript, jQuery
- **API**：豆包API

## 注意事项

1. 文本分类模型需要相应的模型文件（`../nlp_deeplearn/tmp/my_model.h5`），如果模型文件不存在，相关功能可能无法使用
2. 机器翻译使用豆包API实现，确保API密钥有效
3. 情感分析使用基于词典的方法，即使模型文件不存在也能工作
4. 系统会自动处理中文和英文输入

## 豆包API配置

API密钥和模型参数已在 `app.py` 中配置：
- API Key: `5fe8c115-d78c-4fae-90be-6a2075f29f7e`
- Model: `doubao-seed-1-6-lite-251015`

如需修改，请编辑 `app.py` 中的相应配置。
