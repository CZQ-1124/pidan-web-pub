import streamlit as st

from config.settings import APP_NAME
from services.db_service import init_db, import_seed_cases
from services.runtime_config import config_status
from modules.common import init_theme, hero_banner, render_status_pills
from modules import dashboard, upload_visit, family_trend, followup, teaching_library, settings_page
from modules import clinical_portal, training_portal, expert_portal

st.set_page_config(page_title=APP_NAME, layout='wide')
init_theme()
init_db()
import_seed_cases()

PAGE_MAP = {
    '皮蛋工作台': dashboard.render,
    '村民随手拍': upload_visit.render,
    '亲情云守护': family_trend.render,
    '康复随访台': followup.render,
    '村医临床工作区': clinical_portal.render,
    '培训学习区': training_portal.render,
    '教学病例库': teaching_library.render,
    '专家终审台': expert_portal.render,
    '系统设置': settings_page.render,
}

ROLE_NAV = {
    '村民': ['皮蛋工作台', '村民随手拍', '康复随访台'],
    '家属': ['皮蛋工作台', '亲情云守护', '康复随访台'],
    '村医': ['皮蛋工作台', '村医临床工作区', '培训学习区', '教学病例库'],
    '专家': ['皮蛋工作台', '专家终审台', '教学病例库'],
}

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

status = config_status()
with st.sidebar:
    st.markdown(f'## {APP_NAME}')
    render_status_pills(status)
    if st.session_state.get('logged_in'):
        user = st.session_state['user']
        st.write(f"当前用户：{user['name']}｜{user['role']}")
        nav_items = list(ROLE_NAV[user['role']])
        if user['role'] == '专家' and status.get('runtime_settings_enabled'):
            nav_items.append('系统设置')
        page = st.radio('导航', nav_items)
        if st.button('退出登录', use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else:
        st.caption('请选择身份进入演示系统。')

if not st.session_state['logged_in']:
    hero_banner(
        '皮蛋乡村系统',
        '面向基层皮肤健康管理的多角色协同演示系统：早筛、辅助判断、上转复核、随访与培训。'
    )
    tabs = st.tabs(['登录入口', '项目说明', '部署状态'])
    with tabs[0]:
        st.subheader('进入系统')
        c1, c2 = st.columns([1.2, 1])
        with c1:
            name = st.text_input('登录名 / 姓名')
            role = st.selectbox('身份', ['村民', '家属', '村医', '专家'])
            bind_name = st.text_input('家属绑定村民姓名（家属端可填）')
            if st.button('进入皮蛋系统', type='primary'):
                st.session_state['logged_in'] = True
                st.session_state['user'] = {'name': name or role, 'role': role, 'bind_name': bind_name}
                st.rerun()
        with c2:
            st.markdown('### 身份说明')
            st.markdown('- **村民**：上传皮损、看趋势、收随访建议')
            st.markdown('- **家属**：绑定村民、看曲线、看纪要摘要')
            st.markdown('- **村医**：初筛、会诊、随访、提交复核、培训')
            st.markdown('- **专家**：待复核终审、教学病例库维护')
    with tabs[1]:
        st.subheader('当前版本：皮蛋乡村系统 · 公开展示版')
        st.markdown('1. 村民上传后进入图像质控与 AI 分层。')
        st.markdown('2. 家属与村医可查看连续风险曲线。')
        st.markdown('3. 村医可上传音频形成门诊纪要。')
        st.markdown('4. 专家终审可写治疗方案与随访计划，村医继续跟进。')
        st.markdown('5. 培训区支持识图闯关、病例推演与模拟门诊。')
    with tabs[2]:
        settings_page.render(None, embedded=True)
    st.stop()

user = st.session_state['user']
PAGE_MAP[page](user)
