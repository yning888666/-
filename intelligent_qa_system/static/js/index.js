// 全局变量
let isLoading = false;
let lastMessageTime = null;

// DOM 元素
const $messagesContainer = $('#messagesContainer');
const $messageInput = $('#messageInput');
const $sendButton = $('#sendButton');
const $welcomeMessage = $('.welcome-message');

// 初始化
$(document).ready(function() {
    // 自动调整输入框高度
    $messageInput.on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // 发送按钮点击事件
    $sendButton.on('click', sendMessage);
    
    // 输入框回车发送（Shift+Enter换行）
    $messageInput.on('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 输入框聚焦
    $messageInput.on('focus', function() {
        $(this).closest('.input-wrapper').addClass('focused');
    });
    
    $messageInput.on('blur', function() {
        $(this).closest('.input-wrapper').removeClass('focused');
    });
});

// 发送消息
function sendMessage() {
    const message = $messageInput.val().trim();
    
    if (!message || isLoading) {
        return;
    }
    
    // 隐藏欢迎消息
    if (!$welcomeMessage.hasClass('hidden')) {
        $welcomeMessage.addClass('hidden');
    }
    
    // 添加用户消息
    addUserMessage(message);
    
    // 清空输入框
    $messageInput.val('');
    $messageInput.css('height', 'auto');
    
    // 显示加载动画
    showLoadingMessage();
    
    // 发送请求
    isLoading = true;
    $sendButton.prop('disabled', true);
    
    $.ajax({
        url: '/message',
        method: 'POST',
        data: { msg: message },
        timeout: 30000
    })
    .done(function(response) {
        removeLoadingMessage();
        addBotMessage(response.text || '抱歉，无法处理您的请求。', response.type);
    })
    .fail(function(xhr, status, error) {
        removeLoadingMessage();
        let errorMsg = '抱歉，处理请求时出现错误。';
        if (status === 'timeout') {
            errorMsg = '请求超时，请稍后重试。';
        } else if (xhr.responseJSON && xhr.responseJSON.error) {
            errorMsg = xhr.responseJSON.error;
        }
        addBotMessage(errorMsg, 'error');
    })
    .always(function() {
        isLoading = false;
        $sendButton.prop('disabled', false);
        $messageInput.focus();
    });
}

// 添加用户消息
function addUserMessage(text) {
    const timestamp = getCurrentTime();
    const messageHtml = `
        <div class="message message-user">
            <div class="message-content">
                ${escapeHtml(text)}
                <div class="timestamp">${timestamp}</div>
            </div>
        </div>
    `;
    
    $messagesContainer.append(messageHtml);
    scrollToBottom();
}

// 添加机器人消息
function addBotMessage(text, type = 'qa') {
    const timestamp = getCurrentTime();
    const formattedText = formatMessageText(text, type);
    
    const messageHtml = `
        <div class="message message-bot">
            <div class="message-avatar">
                <div class="avatar-icon-small">🤖</div>
            </div>
            <div class="message-content">
                ${formattedText}
                <div class="timestamp">${timestamp}</div>
            </div>
        </div>
    `;
    
    $messagesContainer.append(messageHtml);
    scrollToBottom();
}

// 格式化消息文本
function formatMessageText(text, type) {
    // 将换行符转换为 <br>
    let formatted = escapeHtml(text).replace(/\n/g, '<br>');
    
    // 根据类型添加样式
    if (type === 'translate') {
        formatted = formatted.replace(/🌐 翻译结果:/g, '<strong style="color: #4facfe;">🌐 翻译结果:</strong>');
    } else if (type === 'sentiment') {
        formatted = formatted.replace(/(😊|😞|😐) 情感分析结果:/g, '<strong style="color: #f5576c;">$1 情感分析结果:</strong>');
    } else if (type === 'classify') {
        formatted = formatted.replace(/📊 文本分类结果:/g, '<strong style="color: #667eea;">📊 文本分类结果:</strong>');
    }
    
    // 高亮置信度等关键信息
    formatted = formatted.replace(/(置信度|置信度:)\s*(\d+\.?\d*%)/g, '<span style="color: #22c55e;">$1 $2</span>');
    
    return formatted;
}

// 显示加载消息
function showLoadingMessage() {
    const loadingHtml = `
        <div class="message message-bot loading-message">
            <div class="message-avatar">
                <div class="avatar-icon-small">🤖</div>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    $messagesContainer.append(loadingHtml);
    scrollToBottom();
}

// 移除加载消息
function removeLoadingMessage() {
    $('.loading-message').remove();
}

// 滚动到底部
function scrollToBottom() {
    setTimeout(() => {
        $messagesContainer.scrollTop($messagesContainer[0].scrollHeight);
    }, 100);
}

// 获取当前时间
function getCurrentTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

// HTML 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}