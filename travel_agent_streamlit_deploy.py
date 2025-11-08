import streamlit as st
import os
import random
import json
from openai import OpenAI
from datetime import datetime

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

# 页面配置
st.set_page_config(
    page_title="AI旅行规划助手",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 现代GPT风格的CSS样式
st.markdown("""
<style>
    /* 全局样式 - 添加背景图片 */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.4)), 
                    url('https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* 主容器 - GPT对话式风格 */
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* 顶部标题区域 */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
        text-align: center;
    }
    
    .subtitle {
        font-size: 0.95rem;
        color: #666;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* 对话消息样式 - GPT风格 */
    .chat-message {
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
        border-radius: 18px;
        animation: fadeIn 0.3s ease-in;
        line-height: 1.6;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: rgba(52, 53, 65, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-left: auto;
        max-width: 85%;
    }
    
    .assistant-message {
        background: rgba(68, 70, 84, 0.85);
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
        max-width: 95%;
    }
    
    .message-role {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .user-role {
        color: #10a37f;
    }
    
    .assistant-role {
        color: #1a1a1a;
    }
    
    .message-content {
        color: #1a1a1a;
        font-size: 0.95rem;
    }
    
    /* 欢迎卡片 */
    .welcome-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 1rem;
    }
    
    .welcome-text {
        color: #666;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0.75rem 0;
    }
    
    /* 快速操作卡片 */
    .quick-action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .quick-action-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid rgba(0, 0, 0, 0.08);
        text-align: center;
    }
    
    .quick-action-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        background: rgba(255, 255, 255, 0.95);
    }
    
    .quick-action-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .quick-action-text {
        color: #1a1a1a;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* 侧边栏样式 */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0, 0, 0, 0.08);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #1a1a1a;
        font-weight: 600;
    }
    
    section[data-testid="stSidebar"] .element-container {
        color: #1a1a1a;
    }
    
    /* 按钮样式 - GPT风格 */
    .stButton button {
        background: linear-gradient(135deg, #10a37f 0%, #0d8a6a 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 500;
        padding: 0.65rem 1.25rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(16, 163, 127, 0.2);
        width: 100%;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #0d8a6a 0%, #0a7558 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* 二级按钮样式 */
    .stButton button[kind="secondary"] {
        background: rgba(0, 0, 0, 0.05);
        color: #1a1a1a;
        box-shadow: none;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .stButton button[kind="secondary"]:hover {
        background: rgba(0, 0, 0, 0.08);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* 输入框样式 */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(0, 0, 0, 0.15);
        border-radius: 14px;
        padding: 0.85rem 1.25rem;
        font-size: 0.95rem;
        color: #1a1a1a;
        transition: all 0.2s ease;
    }
    
    .stTextInput input:focus {
        border: 1px solid #10a37f;
        box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
        outline: none;
    }
    
    .stTextInput input::placeholder {
        color: #999;
    }
    
    /* 输入区域容器 */
    .input-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* 状态指示器 */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    .status-online {
        background: rgba(16, 163, 127, 0.1);
        color: #10a37f;
        border: 1px solid rgba(16, 163, 127, 0.2);
    }
    
    .status-offline {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .status-dot-online {
        background: #10a37f;
    }
    
    .status-dot-offline {
        background: #ef4444;
    }
    
    /* 信息卡片 */
    .info-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 14px;
        padding: 1.25rem;
        margin: 1rem 0;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }
    
    .info-card-title {
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
    }
    
    .info-card-content {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* 统计数字 */
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #10a37f;
        margin: 0.5rem 0;
    }
    
    /* 徽章 */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(16, 163, 127, 0.1);
        color: #10a37f;
        border: 1px solid rgba(16, 163, 127, 0.2);
    }
    
    /* 加载动画 */
    .loading-dots {
        display: inline-flex;
        gap: 0.25rem;
    }
    
    .loading-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #10a37f;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* 滚动条 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 0, 0, 0.3);
    }
    
    /* 分隔线 */
    hr {
        border: none;
        height: 1px;
        background: rgba(0, 0, 0, 0.08);
        margin: 1.5rem 0;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

class DeepSeekTravelAgent:
    def __init__(self):
        self.client = None
        self.initialized = False
        
    def initialize(self):
        """初始化DeepSeek客户端"""
        try:
            # 从环境变量或secrets获取配置
            api_key = os.environ.get("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY")
            
            if not api_key:
                return False, "未设置DeepSeek API密钥"
            
            # 配置DeepSeek客户端
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"  # DeepSeek API端点
            )
            self.initialized = True
            return True, "DeepSeek客户端初始化成功"
            
        except Exception as e:
            return False, f"初始化失败: {str(e)}"
    
    def get_random_destination(self):
        """获取随机目的地"""
        destinations = [
            "巴塞罗那, 西班牙", "巴黎, 法国", "东京, 日本", 
            "纽约, 美国", "伦敦, 英国", "悉尼, 澳大利亚",
            "罗马, 意大利", "京都, 日本", "新加坡",
            "开普敦, 南非", "里约热内卢, 巴西", "迪拜, 阿联酋",
            "北京, 中国", "上海, 中国", "香港, 中国", "台北, 台湾",
            "清迈, 泰国", "巴厘岛, 印度尼西亚", "布拉格, 捷克"
        ]
        return random.choice(destinations)
    
    def get_travel_tips(self):
        """获取旅行贴士"""
        tips = [
            "📋 提前办理签证和购买旅行保险",
            "💵 准备一些当地货币现金，方便小额支付", 
            "🗺️ 下载离线地图和翻译应用",
            "🚨 了解当地的紧急联系电话",
            "💊 准备常用药品和防晒用品",
            "🔌 带上合适的电源转换插头",
            "📞 保存大使馆联系方式",
            "🎒 复印重要证件并分开存放",
            "🌡️ 了解目的地气候和季节特点",
            "🍽️ 研究当地饮食文化和特色美食"
        ]
        return "\n".join(tips)
    
    def process_request(self, user_input):
        """处理用户请求"""
        if not self.initialized:
            return "代理未初始化，请先在侧边栏点击初始化按钮"
        
        try:
            # 智能工具调用检测
            tools_used = []
            enhanced_prompt = user_input
            
            if any(keyword in user_input for keyword in ["随机", "推荐", "不知道去哪", "随便"]):
                destination = self.get_random_destination()
                tools_used.append(f"🎲 随机选择了: {destination}")
                enhanced_prompt = f"{user_input}\n\n随机选择的目的地: {destination}"
            
            if any(keyword in user_input for keyword in ["贴士", "建议", "提示", "注意", "准备"]):
                tips = self.get_travel_tips()
                tools_used.append("💡 提供了基础旅行贴士")
                enhanced_prompt = f"{user_input}\n\n参考旅行贴士: {tips}"
            
            # 完整的系统提示词
            system_message = """你是一个专业、友好、经验丰富的旅行规划专家。请用中文回复，遵循以下原则：

# 角色设定
你是资深的旅行规划师，拥有10年以上全球旅行规划经验，熟悉各国文化、景点、美食和交通。

# 回复要求
1. **个性化服务**：根据用户具体需求提供定制化建议
2. **详细具体**：提供具体的景点名称、餐厅推荐、交通方式、时间安排
3. **实用建议**：包括预算估算、最佳季节、注意事项、省钱技巧
4. **格式清晰**：使用适当的标题、列表、分段，让内容易于阅读
5. **热情友好**：保持积极、鼓励的语气，让用户感受到专业和温暖
6. **文化敏感**：尊重各地文化差异，提供文化体验建议

# 内容结构
- 行程概览
- 每日详细安排
- 餐饮推荐
- 交通指南
- 预算分析
- 实用贴士
- 文化体验

请为用户创造难忘的旅行体验！"""
            
            # 调用DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",  # DeepSeek的主要模型
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            
            # 如果使用了工具，在回复开头说明
            if tools_used:
                tools_info = " | ".join(tools_used)
                ai_response = f"🔧 {tools_info}\n\n{ai_response}"
            
            return ai_response
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "API调用额度已用完，请检查DeepSeek账户余额或等待额度重置"
            elif "auth" in error_msg.lower() or "key" in error_msg.lower():
                return "API密钥无效，请检查DeepSeek API密钥配置"
            else:
                return f"处理请求时出错: {error_msg}"

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = DeepSeekTravelAgent()
if "agent_status" not in st.session_state:
    st.session_state.agent_status = "未初始化"
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

# 侧边栏
with st.sidebar:
    # 标题
    st.markdown("### ⚙️ 控制中心")
    
    # 系统状态
    status_class = "status-online" if st.session_state.agent.initialized else "status-offline"
    dot_class = "status-dot-online" if st.session_state.agent.initialized else "status-dot-offline"
    status_text = "已连接" if st.session_state.agent.initialized else "未连接"
    
    st.markdown(f'''
    <div class="status-badge {status_class}">
        <div class="status-dot {dot_class}"></div>
        {status_text}
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 初始化按钮
    if st.button("🚀 初始化AI助手", use_container_width=True, type="primary"):
        with st.spinner("正在连接..."):
            success, status = st.session_state.agent.initialize()
            st.session_state.agent_status = status
            if success:
                st.success("✓ 连接成功")
            else:
                st.error("✗ 连接失败")
            st.rerun()
    
    st.markdown("---")
    
    # 快速操作
    st.markdown("### ⚡ 快速开始")
    
    quick_actions = [
        ("🎲", "随机目的地", "推荐一个随机旅行目的地并详细规划"),
        ("📅", "三日游", "帮我规划一个精彩的三天旅行行程"),
        ("🌅", "单日游", "规划一个充实的一日游行程"),
        ("💡", "旅行贴士", "给我全面的旅行准备建议和贴士"),
        ("🏨", "周末之旅", "规划一个放松的周末短途旅行"),
        ("💰", "预算旅行", "推荐经济实惠的旅行方案"),
    ]
    
    for icon, text, command in quick_actions:
        if st.button(f"{icon} {text}", use_container_width=True, key=f"quick_{text}"):
            st.session_state.messages.append({"role": "user", "content": command})
            st.rerun()
    
    st.markdown("---")
    
    # 统计信息
    st.markdown("### 📊 会话统计")
    st.markdown(f'<div class="stat-number">{st.session_state.conversation_count}</div>', unsafe_allow_html=True)
    st.markdown("对话轮次")
    
    st.markdown("---")
    
    # 清空按钮
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()
    
    st.markdown("---")
    
    # 使用提示
    st.markdown("""
    <div class="info-card">
        <div class="info-card-title">💡 使用技巧</div>
        <div class="info-card-content">
        • 描述详细需求获得更好结果<br>
        • 可指定预算、兴趣、季节<br>
        • 支持多轮对话完善计划<br>
        • 基于 DeepSeek 智能模型
        </div>
    </div>
    """, unsafe_allow_html=True)

# 主内容区域
# 顶部标题
st.markdown('''
<div class="header-container">
    <div class="main-title">✈️ AI 旅行规划助手 <span class="badge">DeepSeek</span></div>
    <div class="subtitle">让每一次旅行都成为难忘的回忆</div>
</div>
''', unsafe_allow_html=True)

# 对话区域
chat_container = st.container()

with chat_container:
    # 显示欢迎信息
    if len(st.session_state.messages) == 0:
        st.markdown('''
        <div class="welcome-card">
            <div class="welcome-title">👋 你好！我是你的AI旅行规划助手</div>
            <div class="welcome-text">我可以帮你规划完美的旅行行程、推荐目的地，并提供专业的旅行建议</div>
            <div class="welcome-text">💬 请先在左侧点击"初始化AI助手"，然后告诉我你的旅行想法</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # 显示对话历史
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'''
            <div class="chat-message user-message">
                <div class="message-role user-role">👤 你</div>
                <div class="message-content">{message["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="chat-message assistant-message">
                <div class="message-role assistant-role">🤖 AI助手</div>
                <div class="message-content">{message["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)

# 输入区域
st.markdown('<div class="input-container">', unsafe_allow_html=True)

input_col1, input_col2 = st.columns([5, 1])

with input_col1:
    user_input = st.text_input(
        "消息",
        placeholder="例如：帮我规划一个巴黎三日游，预算中等，喜欢文化和美食..." if st.session_state.agent.initialized else "请先初始化AI助手...",
        label_visibility="collapsed",
        disabled=not st.session_state.agent.initialized,
        key="user_input"
    )

with input_col2:
    send_button = st.button("发送", use_container_width=True, disabled=not st.session_state.agent.initialized, type="primary")

st.markdown('</div>', unsafe_allow_html=True)

# 处理用户输入
if send_button and user_input and st.session_state.agent.initialized:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.conversation_count += 1
    
    # 显示AI响应
    with st.spinner(""):
        st.markdown('''
        <div class="chat-message assistant-message">
            <div class="message-role assistant-role">🤖 AI助手</div>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        try:
            ai_response = st.session_state.agent.process_request(user_input)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
            
        except Exception as e:
            error_msg = f"抱歉，处理请求时出错: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.rerun()