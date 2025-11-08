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

# 现代深色风格的CSS样式 - 优化版
st.markdown("""
<style>
    /* 全局样式 - 添加背景图片 */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), 
                    url('https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* 主容器 */
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* 顶部标题区域 - 透明简洁 */
    .header-container {
        background: transparent;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .main-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: white;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    }
    
    .subtitle {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 0.5rem;
        text-shadow: 0 1px 5px rgba(0, 0, 0, 0.5);
    }
    
    /* 对话消息样式 - 增强对比度 */
    .chat-message {
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
        border-radius: 16px;
        animation: fadeIn 0.3s ease-in;
        line-height: 1.6;
        position: relative;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: rgba(45, 45, 45, 0.95) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        margin-left: auto;
        max-width: 85%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .assistant-message {
        background: rgba(60, 60, 60, 0.95) !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.12);
        max-width: 95%;
    }
    
    .message-role {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: rgba(255, 255, 255, 0.95);
    }
    
    .message-content {
        color: rgba(255, 255, 255, 0.98);
        font-size: 0.95rem;
        white-space: pre-wrap;
        line-height: 1.7;
    }
    
    /* 欢迎卡片 - 紧凑清晰设计 */
    .welcome-card {
        background: rgba(45, 45, 45, 0.92) !important;
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
        text-align: center;
    }
    
    .welcome-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.75rem;
    }
    
    .welcome-text {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0.5rem 0;
    }
    
    /* 侧边栏样式 */
    section[data-testid="stSidebar"] {
        background: rgba(30, 30, 30, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white;
        font-weight: 600;
    }
    
    section[data-testid="stSidebar"] .element-container {
        color: white;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* 按钮样式 - 增强可见性 */
    .stButton button {
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.5rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* 主要按钮样式 */
    .stButton button[kind="primary"] {
        background: rgba(59, 130, 246, 0.8) !important;
        border: 1px solid rgba(59, 130, 246, 0.9) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: rgba(59, 130, 246, 0.9) !important;
        border: 1px solid rgba(59, 130, 246, 1) !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* 输入框样式 - 增强对比度 */
    .stTextInput input {
        background: rgba(40, 40, 40, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.25rem !important;
        font-size: 0.95rem !important;
        color: white !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stTextInput input:focus {
        border: 1px solid rgba(59, 130, 246, 0.8) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2), 0 2px 8px rgba(0, 0, 0, 0.3) !important;
        outline: none !important;
        background: rgba(40, 40, 40, 1) !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* 输入区域容器 - 清晰背景 */
    .input-container {
        background: rgba(35, 35, 35, 0.95) !important;
        backdrop-filter: blur(20px);
        border-radius: 18px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 6px 28px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    /* 发送按钮特殊样式 */
    .send-button {
        background: rgba(59, 130, 246, 0.9) !important;
        border: 1px solid rgba(59, 130, 246, 1) !important;
        color: white !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.8rem !important;
        width: 100% !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
    }
    
    .send-button:hover {
        background: rgba(59, 130, 246, 1) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4) !important;
    }
    
    .send-button:disabled {
        background: rgba(100, 100, 100, 0.5) !important;
        border: 1px solid rgba(100, 100, 100, 0.7) !important;
        color: rgba(255, 255, 255, 0.5) !important;
        cursor: not-allowed !important;
    }
    
    /* 状态徽章 */
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
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.4);
    }
    
    .status-offline {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
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
        background: #22c55e;
    }
    
    .status-dot-offline {
        background: #ef4444;
    }
    
    /* 信息卡片 */
    .info-card {
        background: rgba(45, 45, 45, 0.8);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    .info-card-title {
        font-weight: 600;
        color: white;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
    }
    
    .info-card-content {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* 统计数字 */
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #22c55e;
        margin: 0.5rem 0;
    }
    
    /* 徽章 */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    
    /* 滚动条 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* 分隔线 */
    hr {
        border: none;
        height: 1px;
        background: rgba(255, 255, 255, 0.1);
        margin: 1.5rem 0;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 修复Streamlit默认文字颜色 */
    .stMarkdown, .stText {
        color: white;
    }
    
    /* 优化空白区域 */
    .stEmpty {
        background: transparent !important;
    }
    
    /* 聊天容器间距优化 */
    .chat-container {
        margin-bottom: 1rem;
    }
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
                base_url="https://api.deepseek.com/v1"
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
            "北京, 中国", "上海, 中国", "中国香港, 中国", "台北, 中国台湾",
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
            
            # 系统提示词
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

请为用户创造难忘的旅行体验！"""
            
            # 调用DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
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
    <div class="subtitle">探索世界，规划完美旅程</div>
</div>
''', unsafe_allow_html=True)

# 对话区域
chat_container = st.container()
chat_container.markdown('<div class="chat-container">', unsafe_allow_html=True)

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
                <div class="message-role">👤 你</div>
                <div class="message-content">{message["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="chat-message assistant-message">
                <div class="message-role">🤖 AI助手</div>
                <div class="message-content">{message["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)

chat_container.markdown('</div>', unsafe_allow_html=True)

# 输入区域
st.markdown('<div class="input-container">', unsafe_allow_html=True)

input_col1, input_col2 = st.columns([5, 1])

with input_col1:
    user_input = st.text_input(
        "消息",
        placeholder="描述你的旅行想法..." if st.session_state.agent.initialized else "请先初始化AI助手...",
        label_visibility="collapsed",
        disabled=not st.session_state.agent.initialized,
        key="user_input"
    )

with input_col2:
    # 使用自定义样式的发送按钮
    send_button = st.button("➤", use_container_width=True, disabled=not st.session_state.agent.initialized, type="primary")

st.markdown('</div>', unsafe_allow_html=True)

# 处理用户输入
if send_button and user_input and st.session_state.agent.initialized:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.conversation_count += 1
    
    # 获取AI响应
    with st.spinner("思考中..."):
        try:
            ai_response = st.session_state.agent.process_request(user_input)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
            
        except Exception as e:
            error_msg = f"抱歉，处理请求时出错: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.rerun()