import streamlit as st
import os
import random
import json
from openai import OpenAI
from datetime import datetime
import base64
import requests
import hashlib
import io
from PIL import Image
import zipfile

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

# 页面配置
st.set_page_config(
    page_title="AI旅行规划助手 - 现代化版",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 现代化Glassmorphism CSS样式 ====================
st.markdown("""
<style>
    /* 全局样式 - 现代毛玻璃风格 */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), 
                    url('https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* 主容器样式 */
    .main-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* 标题区域 */
    .header-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 30px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        background: linear-gradient(45deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 10px;
        text-shadow: 0 1px 5px rgba(0, 0, 0, 0.5);
    }
    
    /* 对话消息样式 */
    .chat-message {
        padding: 20px 25px;
        margin: 15px 0;
        border-radius: 18px;
        animation: fadeIn 0.3s ease-in;
        line-height: 1.7;
        position: relative;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: rgba(37, 99, 235, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(37, 99, 235, 0.4);
        margin-left: auto;
        max-width: 85%;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.2);
    }
    
    .assistant-message {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        max-width: 95%;
    }
    
    .message-role {
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .message-content {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1rem;
        white-space: pre-wrap;
    }
    
    /* 欢迎卡片 */
    .welcome-card {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 30px 40px;
        margin: 20px 0;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .welcome-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: white;
        margin-bottom: 15px;
    }
    
    .welcome-text {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        line-height: 1.6;
        margin: 10px 0;
    }
    
    /* 侧边栏样式 */
    section[data-testid="stSidebar"] {
        background: rgba(30, 30, 30, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* 按钮样式 */
    .stButton button {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 24px;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        width: 100%;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stButton button:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* 主要按钮样式 */
    .stButton button[kind="primary"] {
        background: linear-gradient(45deg, #2563EB, #3B82F6) !important;
        border: 1px solid rgba(59, 130, 246, 0.9) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(45deg, #1D4ED8, #2563EB) !important;
        box-shadow: 0 6px 25px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* 输入框样式 */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 15px 20px;
        font-size: 1rem;
        color: white;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput input:focus {
        border: 1px solid rgba(59, 130, 246, 0.8);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2), 0 4px 15px rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 0.2);
    }
    
    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.6);
    }
    
    /* 输入区域容器 */
    .input-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        margin-top: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* 卡片样式 */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
    }
    
    /* 状态指示器 */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 8px 0;
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
        width: 10px;
        height: 10px;
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
    
    /* 设置面板样式 */
    .settings-panel {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px;
        margin: 10px 0;
    }
    
    /* 导出功能样式 */
    .export-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    
    /* 历史管理样式 */
    .history-item {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 15px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
    }
    
    /* 徽章样式 */
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(37, 99, 235, 0.2);
        color: #3B82F6;
        border: 1px solid rgba(37, 99, 235, 0.4);
        margin-left: 8px;
    }
    
    /* 滚动条样式 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 修复文本颜色 */
    .stMarkdown, .stText {
        color: white;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .header-container {
            padding: 20px;
        }
        .welcome-card {
            padding: 20px;
        }
        .input-container {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== 工具函数 ====================

def get_weather_info(city="北京"):
    """获取天气信息"""
    try:
        # 使用Open-Meteo API获取天气
        url = f"https://api.open-meteo.com/v1/forecast?city={city}&current_weather=true&hourly=temperature_2m,weathercode,humidity&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data.get('current_weather', {})
            return {
                "city": city,
                "temperature": current.get('temperature', 'N/A'),
                "windspeed": current.get('windspeed', 'N/A'),
                "weathercode": current.get('weathercode', 0)
            }
    except Exception as e:
        st.error(f"获取天气信息失败: {e}")
    return None

def get_exchange_rate(from_currency="CNY", to_currency="USD"):
    """获取汇率信息"""
    try:
        url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('rates', {}).get(to_currency, None)
    except Exception as e:
        st.error(f"获取汇率失败: {e}")
    return None

def export_to_text():
    """导出对话记录为文本"""
    if not st.session_state.messages:
        return "暂无对话记录"
    
    content = "=== AI旅行代理对话记录 ===\n"
    content += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += "=" * 40 + "\n\n"
    
    for msg in st.session_state.messages:
        role = "用户" if msg["role"] == "user" else "AI助手"
        content += f"{role}: {msg['content']}\n\n"
    
    return content

def export_to_json():
    """导出对话记录为JSON"""
    if not st.session_state.messages:
        return {}
    
    export_data = {
        "export_time": datetime.now().isoformat(),
        "conversation_count": len(st.session_state.messages),
        "messages": st.session_state.messages,
        "settings": {
            "agent_initialized": st.session_state.agent.initialized,
            "conversation_count": st.session_state.conversation_count
        }
    }
    return export_data

def get_random_destinations():
    """获取随机目的地推荐"""
    destinations = [
        {
            "name": "京都, 日本",
            "description": "古典寺庙、樱花、传统文化体验",
            "best_time": "春季(3-5月)或秋季(9-11月)",
            "budget": "中等(¥8,000-15,000)"
        },
        {
            "name": "巴黎, 法国", 
            "description": "浪漫之都、艺术博物馆、美食体验",
            "best_time": "4-6月或9-10月",
            "budget": "中高等(¥12,000-25,000)"
        },
        {
            "name": "巴塞罗那, 西班牙",
            "description": "高迪建筑、海滩、弗拉门戈",
            "best_time": "5-9月",
            "budget": "中等(¥7,000-18,000)"
        },
        {
            "name": "新西兰南北岛",
            "description": "自然风光、极限运动、户外探险",
            "best_time": "12-2月(夏季)",
            "budget": "高(¥15,000-30,000)"
        },
        {
            "name": "土耳其伊斯坦布尔",
            "description": "欧亚文化交汇、历史遗迹、美食",
            "best_time": "4-6月或9-11月",
            "budget": "中低等(¥5,000-12,000)"
        }
    ]
    return random.choice(destinations)

# ==================== AI代理类 ====================

class ModernTravelAgent:
    def __init__(self):
        self.client = None
        self.initialized = False
        self.api_key = None
        self.base_url = None
        self.model = None
        
    def initialize(self, api_key, base_url, model):
        """初始化AI客户端"""
        try:
            if not api_key:
                return False, "❌ 未设置API密钥"
            
            if not base_url:
                base_url = "https://api.deepseek.com/v1"
            
            if not model:
                model = "deepseek-chat"
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            self.api_key = api_key
            self.base_url = base_url
            self.model = model
            self.initialized = True
            return True, f"✅ AI客户端初始化成功 ({model})"
            
        except Exception as e:
            return False, f"❌ 初始化失败: {str(e)}"
    
    def get_system_prompt(self):
        """获取系统提示词 - 可自定义"""
        return st.session_state.get("custom_system_prompt", """你是一个专业、友好、经验丰富的旅行规划专家。请用中文回复，遵循以下原则：

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

请为用户创造难忘的旅行体验！""")
    
    def process_request(self, user_input):
        """处理用户请求"""
        if not self.initialized:
            return "❌ 代理未初始化，请先在侧边栏配置API设置"
        
        try:
            # 智能工具调用检测
            tools_used = []
            enhanced_prompt = user_input
            
            # 天气查询
            if any(keyword in user_input for keyword in ["天气", "Weather", "温度", "下不下雨"]):
                # 简单提取城市名
                city = "北京"  # 默认城市
                for city_name in ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "南京", "武汉", "重庆"]:
                    if city_name in user_input:
                        city = city_name
                        break
                
                weather = get_weather_info(city)
                if weather:
                    tools_used.append(f"🌤️ 查询了{weather['city']}的天气: {weather['temperature']}°C")
                    enhanced_prompt = f"{user_input}\n\n参考天气信息: {city}当前温度{weather['temperature']}°C, 风速{weather['windspeed']}km/h"
            
            # 随机目的地推荐
            if any(keyword in user_input for keyword in ["随机", "推荐", "不知道去哪", "随便", "推荐个地方"]):
                destination = get_random_destinations()
                tools_used.append(f"🎲 推荐随机目的地: {destination['name']}")
                enhanced_prompt = f"{user_input}\n\n推荐目的地参考: {destination['name']} - {destination['description']}\n最佳旅行时间: {destination['best_time']}\n预算范围: {destination['budget']}"
            
            # 汇率查询
            if any(keyword in user_input for keyword in ["汇率", "换算", "钱", "价格", "费用"]):
                # 简单汇率查询
                if "美元" in user_input or "USD" in user_input or "$" in user_input:
                    rate = get_exchange_rate("CNY", "USD")
                    if rate:
                        tools_used.append("💱 提供了汇率换算信息")
                        enhanced_prompt = f"{user_input}\n\n汇率参考: 1 CNY ≈ {rate:.4f} USD"
            
            # 调用AI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
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
                return "❌ API调用额度已用完，请检查API账户余额"
            elif "auth" in error_msg.lower() or "key" in error_msg.lower():
                return "❌ API密钥无效，请检查API配置"
            else:
                return f"❌ 处理请求时出错: {error_msg}"

# ==================== 初始化session state ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = ModernTravelAgent()
if "agent_status" not in st.session_state:
    st.session_state.agent_status = "未初始化"
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0
if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = None
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "export_format" not in st.session_state:
    st.session_state.export_format = "text"
if "custom_system_prompt" not in st.session_state:
    st.session_state.custom_system_prompt = ""
if "current_view" not in st.session_state:
    st.session_state.current_view = "chat"
if "settings" not in st.session_state:
    st.session_state.settings = {
        "theme": "auto",
        "language": "zh",
        "font_size": "medium"
    }

# ==================== 主界面 ====================

# 顶部标题
st.markdown('''
<div class="header-container">
    <div class="main-title">✈️ AI旅行规划助手 <span class="badge">现代化版</span></div>
    <div class="subtitle">智能化、个性化的旅行规划体验</div>
</div>
''', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("🎛️ 控制面板")
    
    # 视图切换
    st.subheader("📱 视图模式")
    view_options = ["💬 智能对话", "📊 数据面板", "⚙️ 个性化设置", "📚 对话历史", "💾 导出功能"]
    for i, view in enumerate(view_options):
        if st.button(view, key=f"view_{i}", use_container_width=True):
            st.session_state.current_view = ["chat", "dashboard", "settings", "history", "export"][i]
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🤖 AI配置")
    
    # API配置
    api_key = st.text_input("API密钥:", type="password", 
                           value=os.environ.get("DEEPSEEK_API_KEY", ""))
    base_url = st.text_input("API基础URL:", 
                           value="https://api.deepseek.com/v1",
                           help="例如: https://api.deepseek.com/v1")
    model = st.text_input("模型名称:", 
                         value="deepseek-chat",
                         help="例如: deepseek-chat, gpt-3.5-turbo")
    
    if st.button("🚀 初始化AI代理", use_container_width=True, type="primary"):
        with st.spinner("初始化中..."):
            success, status = st.session_state.agent.initialize(api_key, base_url, model)
            st.session_state.agent_status = status
            if success:
                st.success("初始化成功！")
            else:
                st.error("初始化失败")
            st.rerun()
    
    # 代理状态
    st.subheader("📊 代理状态")
    status_class = "status-online" if st.session_state.agent.initialized else "status-offline"
    dot_class = "status-dot-online" if st.session_state.agent.initialized else "status-dot-offline"
    status_text = "已连接" if st.session_state.agent.initialized else "未连接"
    
    st.markdown(f'''
    <div class="status-badge {status_class}">
        <div class="status-dot {dot_class}"></div>
        {status_text}
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(f"状态: {st.session_state.agent_status}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("⚡ 快速操作")
    
    quick_actions = [
        ("🎲 随机目的地", "推荐一个随机旅行目的地并详细规划"),
        ("📅 三日游", "帮我规划一个精彩的三天旅行行程"),
        ("🌅 单日游", "规划一个充实的一日游行程"),
        ("💡 旅行贴士", "给我全面的旅行准备建议和贴士"),
        ("🏨 周末之旅", "规划一个放松的周末短途旅行"),
        ("💰 预算旅行", "推荐经济实惠的旅行方案"),
        ("🌍 文化体验", "推荐有文化深度的旅行体验"),
        ("🍽️ 美食之旅", "规划以美食为主题的旅行")
    ]
    
    for text, command in quick_actions:
        if st.button(text, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": command})
            st.rerun()
    
    if st.button("🔄 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📈 统计信息")
    st.info(f"对话轮次: {st.session_state.conversation_count}")
    st.info(f"消息数量: {len(st.session_state.messages)}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("💡 使用技巧")
    st.markdown("""
    - 🎯 描述具体需求获得更好结果
    - 🌍 可指定预算、兴趣、季节偏好
    - 💬 支持多轮对话完善计划
    - 🌤️ 支持天气查询和汇率换算
    - 🔧 可自定义System Prompt
    - 💾 支持多种格式导出
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== 主内容区域 ====================

if st.session_state.current_view == "chat":
    # 智能对话界面
    chat_container = st.container()
    
    with chat_container:
        # 显示欢迎信息
        if len(st.session_state.messages) == 0:
            st.markdown('''
            <div class="welcome-card">
                <div class="welcome-title">👋 欢迎使用现代化AI旅行规划助手！</div>
                <div class="welcome-text">我基于先进的AI技术，为您提供个性化、专业的旅行规划服务</div>
                <div class="welcome-text">✨ 支持天气查询、汇率换算、目的地推荐等智能功能</div>
                <div class="welcome-text">💬 请先在侧边栏配置API设置，然后开始您的旅行规划之旅</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # 显示对话历史
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'''
                <div class="chat-message user-message">
                    <div class="message-role">👤 您</div>
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
    
    # 输入区域
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.subheader("💬 与AI旅行专家对话")
    
    input_col1, input_col2 = st.columns([4, 1])
    
    with input_col1:
        user_input = st.text_input(
            "消息",
            placeholder="描述您的旅行需求，如：帮我规划一个巴黎三日游..." if st.session_state.agent.initialized else "请先在侧边栏初始化AI代理...",
            label_visibility="collapsed",
            disabled=not st.session_state.agent.initialized,
            key="user_input_chat"
        )
    
    with input_col2:
        send_button = st.button("发送", use_container_width=True, disabled=not st.session_state.agent.initialized, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 处理用户输入
    if send_button and user_input and st.session_state.agent.initialized:
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.conversation_count += 1
        
        # 获取AI响应
        with st.spinner("🤔 AI旅行专家正在思考..."):
            try:
                ai_response = st.session_state.agent.process_request(user_input)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
                
            except Exception as e:
                error_msg = f"抱歉，处理请求时出错: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()

elif st.session_state.current_view == "dashboard":
    # 数据面板
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("📊 数据面板")
    
    # 天气信息
    st.subheader("🌤️ 天气信息")
    col1, col2 = st.columns(2)
    
    with col1:
        city = st.selectbox("选择城市:", ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安"])
        if st.button("查询天气", use_container_width=True):
            weather = get_weather_info(city)
            if weather:
                st.session_state.weather_data = weather
    
    with col2:
        if st.session_state.weather_data:
            w = st.session_state.weather_data
            st.metric("温度", f"{w['temperature']}°C")
            st.metric("风速", f"{w['windspeed']} km/h")
        else:
            st.info("点击查询天气获取最新信息")
    
    # 汇率信息
    st.subheader("💱 汇率信息")
    col3, col4 = st.columns(2)
    
    with col3:
        from_cur = st.selectbox("从:", ["CNY", "USD", "EUR", "JPY", "GBP"])
        to_cur = st.selectbox("到:", ["USD", "CNY", "EUR", "JPY", "GBP"])
        if from_cur != to_cur:
            rate = get_exchange_rate(from_cur, to_cur)
            if rate:
                st.metric(f"{from_cur} → {to_cur}", f"{rate:.4f}")
    
    with col4:
        st.info("实时汇率信息，基于Frankfurter API")
    
    # 随机目的地
    st.subheader("🎲 随机目的地")
    if st.button("🎲 推荐随机目的地", use_container_width=True):
        destination = get_random_destinations()
        st.session_state.selected_destination = destination
    
    if st.session_state.selected_destination:
        d = st.session_state.selected_destination
        st.markdown(f'''
        <div class="glass-card">
            <h3>{d['name']}</h3>
            <p><strong>描述:</strong> {d['description']}</p>
            <p><strong>最佳时间:</strong> {d['best_time']}</p>
            <p><strong>预算范围:</strong> {d['budget']}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "settings":
    # 个性化设置
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("⚙️ 个性化设置")
    
    # System Prompt自定义
    st.subheader("🤖 System Prompt设置")
    custom_prompt = st.text_area(
        "自定义System Prompt:",
        value=st.session_state.custom_system_prompt,
        height=200,
        help="您可以自定义AI助手的角色和回复风格"
    )
    
    if st.button("💾 保存System Prompt", use_container_width=True):
        st.session_state.custom_system_prompt = custom_prompt
        st.success("System Prompt已保存！")
    
    st.markdown("---")
    
    # 其他设置
    st.subheader("🎨 界面设置")
    
    # 主题设置
    theme = st.selectbox("主题:", ["自动", "明亮", "深色"], 
                        index=0 if st.session_state.settings["theme"] == "auto" else 
                        1 if st.session_state.settings["theme"] == "light" else 2)
    
    # 语言设置
    language = st.selectbox("语言:", ["中文", "English"], 
                           index=0 if st.session_state.settings["language"] == "zh" else 1)
    
    # 字体大小
    font_size = st.selectbox("字体大小:", ["小", "中", "大"],
                            index=1 if st.session_state.settings["font_size"] == "medium" else
                            0 if st.session_state.settings["font_size"] == "small" else 2)
    
    if st.button("💾 保存设置", use_container_width=True):
        st.session_state.settings.update({
            "theme": "auto" if theme == "自动" else "light" if theme == "明亮" else "dark",
            "language": "zh" if language == "中文" else "en",
            "font_size": "small" if font_size == "小" else "medium" if font_size == "中" else "large"
        })
        st.success("设置已保存！")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "history":
    # 对话历史
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("📚 对话历史")
    
    if st.session_state.messages:
        # 搜索功能
        search_term = st.text_input("🔍 搜索对话内容:")
        
        # 筛选对话
        filtered_messages = []
        for i in range(0, len(st.session_state.messages), 2):
            if i + 1 < len(st.session_state.messages):
                user_msg = st.session_state.messages[i]
                ai_msg = st.session_state.messages[i + 1]
                if (not search_term or 
                    search_term.lower() in user_msg["content"].lower() or 
                    search_term.lower() in ai_msg["content"].lower()):
                    filtered_messages.append((user_msg, ai_msg))
        
        # 显示对话历史
        for idx, (user_msg, ai_msg) in enumerate(filtered_messages):
            st.markdown(f'''
            <div class="history-item">
                <h4>对话 {idx + 1}</h4>
                <p><strong>用户:</strong> {user_msg['content'][:100]}{'...' if len(user_msg['content']) > 100 else ''}</p>
                <p><strong>AI:</strong> {ai_msg['content'][:100]}{'...' if len(ai_msg['content']) > 100 else ''}</p>
                <small>时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            ''', unsafe_allow_html=True)
        
        st.info(f"共找到 {len(filtered_messages)} 条对话记录")
    else:
        st.info("暂无对话历史记录")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "export":
    # 导出功能
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("💾 导出功能")
    
    if st.session_state.messages:
        st.subheader("📄 选择导出格式")
        
        export_format = st.radio("导出格式:", ["文本格式", "JSON格式"], horizontal=True)
        
        if export_format == "文本格式":
            st.subheader("📝 文本导出预览")
            export_content = export_to_text()
            st.text_area("导出内容:", value=export_content, height=300)
            
            if st.button("📥 下载文本文件", use_container_width=True):
                st.download_button(
                    label="💾 下载 .txt 文件",
                    data=export_content,
                    file_name=f"旅行代理对话记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        else:
            st.subheader("🔧 JSON导出预览")
            export_data = export_to_json()
            export_json = json.dumps(export_data, ensure_ascii=False, indent=2)
            st.text_area("导出内容:", value=export_json, height=300)
            
            if st.button("📥 下载JSON文件", use_container_width=True):
                st.download_button(
                    label="💾 下载 .json 文件",
                    data=export_json,
                    file_name=f"旅行代理对话记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        st.markdown("---")
        st.subheader("📊 导出统计")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("对话轮次", st.session_state.conversation_count)
        with col2:
            st.metric("消息数量", len(st.session_state.messages))
        with col3:
            st.metric("字符数", sum(len(msg["content"]) for msg in st.session_state.messages))
    else:
        st.info("暂无对话记录可导出")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== 页脚 ====================
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 20px; font-size: 0.9em;">'
    '🤖 基于现代化AI技术构建 | ✈️ AI旅行规划助手 | 🌐 部署于 Streamlit Cloud | '
    '💡 支持自定义API接口和System Prompt'
    "</div>",
    unsafe_allow_html=True
)