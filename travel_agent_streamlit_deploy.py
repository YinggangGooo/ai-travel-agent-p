import streamlit as st
import asyncio
import os
import random
import sys
from datetime import datetime

# 尝试导入依赖包，提供友好的错误提示
try:
    from agent_framework import ChatAgent
    from agent_framework.openai import OpenAIChatClient
    DEPENDENCIES_LOADED = True
except ImportError as e:
    DEPENDENCIES_LOADED = False
    st.error(f"❌ 依赖包加载失败: {e}")

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

# 页面配置
st.set_page_config(
    page_title="AI旅行规划代理 - 云端版",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #2196f3;
    }
    .assistant-message {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4dabf7;
    }
    .system-message {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 3px solid #6c757d;
        font-size: 0.9em;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_agent():
    """初始化AI代理"""
    if not DEPENDENCIES_LOADED:
        return None, "依赖包未加载"
    
    # 工具函数
    def get_random_destination() -> str:
        destinations = [
            "巴塞罗那, 西班牙", "巴黎, 法国", "东京, 日本", 
            "纽约, 美国", "伦敦, 英国", "悉尼, 澳大利亚",
            "罗马, 意大利", "京都, 日本", "新加坡",
            "开普敦, 南非", "里约热内卢, 巴西", "迪拜, 阿联酋"
        ]
        selected = random.choice(destinations)
        return selected
    
    def get_travel_tips() -> str:
        tips = [
            "📋 提前办理签证和购买旅行保险",
            "💵 准备一些当地货币现金，方便小额支付", 
            "🗺️ 下载离线地图和翻译应用",
            "🚨 了解当地的紧急联系电话",
            "💊 准备常用药品和防晒用品",
            "🔌 带上合适的电源转换插头"
        ]
        return "\n".join(tips)
    
    try:
        # 获取环境变量 - 在Streamlit Cloud中通过secrets管理
        github_endpoint = os.environ.get("GITHUB_ENDPOINT") or st.secrets.get("GITHUB_ENDPOINT", "https://models.inference.ai.azure.com")
        github_token = os.environ.get("GITHUB_TOKEN") or st.secrets.get("GITHUB_TOKEN", "")
        github_model = os.environ.get("GITHUB_MODEL_ID") or st.secrets.get("GITHUB_MODEL_ID", "gpt-4o-mini")
        
        if not github_token:
            return None, "未设置GITHUB_TOKEN"
        
        client = OpenAIChatClient(
            base_url=github_endpoint,
            api_key=github_token,
            model_id=github_model
        )
        
        agent = ChatAgent(
            chat_client=client,
            instructions="""你是一个专业、友好的旅行规划专家。你可以帮助用户：

1. 规划各种旅行行程（单日游、多日游、周末 getaway 等）
2. 推荐随机目的地
3. 提供旅行贴士和建议
4. 根据用户偏好定制个性化行程

请用中文回复，保持专业且友好的语气。根据用户需求自动选择合适的工具来帮助他们。""",
            tools=[get_random_destination, get_travel_tips]
        )
        
        return agent, "✅ AI代理初始化成功"
        
    except Exception as e:
        return None, f"❌ 代理初始化失败: {str(e)}"

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "agent_status" not in st.session_state:
    st.session_state.agent_status = "未初始化"
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

# 标题和介绍
st.markdown('<h1 class="main-header">🏖️ AI 智能旅行规划代理 - 云端版</h1>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("🚀 控制面板")
    
    # 系统状态
    st.subheader("📊 系统状态")
    if not DEPENDENCIES_LOADED:
        st.error("依赖包未加载")
    elif not ENV_LOADED:
        st.warning("环境变量未加载")
    else:
        st.success("环境正常")
    
    # 初始化代理按钮
    if st.button("🔄 初始化AI代理", use_container_width=True):
        with st.spinner("初始化中..."):
            agent, status = initialize_agent()
            st.session_state.agent = agent
            st.session_state.agent_status = status
            st.rerun()
    
    # 显示代理状态
    status_color = "🔴" if "失败" in st.session_state.agent_status else "🟢" if "成功" in st.session_state.agent_status else "🟡"
    st.write(f"{status_color} {st.session_state.agent_status}")
    
    st.markdown("---")
    st.subheader("⚡ 快速操作")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 随机目的地", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "推荐一个随机旅行目的地"})
        if st.button("📅 三日游", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "帮我规划一个三天的旅行行程"})
    with col2:
        if st.button("💡 小贴士", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "给我一些旅行小贴士"})
        if st.button("🔄 清空", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    st.subheader("📈 会话统计")
    st.info(f"对话轮次: {st.session_state.conversation_count}")
    
    st.markdown("---")
    st.subheader("💡 使用提示")
    st.markdown("""
    - 🎯 **具体需求**获得更好结果
    - 🌍 **指定偏好**如预算、兴趣
    - 💬 **多轮对话**完善计划
    - ⚡ **先初始化**代理再使用
    """)

# 主对话区域
chat_container = st.container()

with chat_container:
    # 显示欢迎信息
    if len(st.session_state.messages) == 0:
        st.markdown('<div class="system-message">🚀 欢迎使用 AI 旅行规划代理！</div>', unsafe_allow_html=True)
        st.markdown('<div class="system-message">💡 我可以帮您规划旅行、推荐目的地、提供旅行建议</div>', unsafe_allow_html=True)
        st.markdown('<div class="system-message">👇 请在侧边栏点击"初始化AI代理"，然后开始使用</div>', unsafe_allow_html=True)
    
    # 显示对话历史
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">👤 您: {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🤖 AI: {message["content"]}</div>', unsafe_allow_html=True)

# 用户输入区域（仅在代理初始化后可用）
st.markdown("---")
input_col1, input_col2 = st.columns([4, 1])

with input_col1:
    user_input = st.text_input(
        "💬 输入您的旅行需求:",
        placeholder="例如：帮我规划一个巴黎三日游..." if st.session_state.agent else "请先初始化AI代理...",
        label_visibility="collapsed",
        disabled=not st.session_state.agent
    )

with input_col2:
    send_button = st.button("发送", use_container_width=True, disabled=not st.session_state.agent)

# 处理用户输入
if send_button and user_input and st.session_state.agent:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.conversation_count += 1
    
    # 显示AI响应
    with st.spinner("🤔 AI思考中..."):
        try:
            async def get_response():
                return await st.session_state.agent.run(user_input)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(get_response())
            loop.close()
            
            # 提取回复文本
            last_message = response.messages[-1]
            if hasattr(last_message.contents[0], 'text'):
                ai_response = last_message.contents[0].text
            else:
                ai_response = str(last_message.contents[0])
            
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
            
        except Exception as e:
            error_msg = f"抱歉，处理请求时出错: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.rerun()

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6c757d;'>"
    "🤖 基于 Microsoft Agent Framework 构建 | "
    "🏖️ AI 旅行规划代理 云端版 v1.0 | "
    "🌐 部署于 Streamlit Cloud"
    "</div>",
    unsafe_allow_html=True
)