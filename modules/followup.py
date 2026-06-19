import pandas as pd
import streamlit as st
from services.db_service import list_cases, list_audio_notes
from modules.common import require_login, hero_banner, metric_grid, render_review_plan


RISK_LABELS = {
    0: "待复拍",
    1: "低风险",
    2: "中风险",
    3: "高风险",
}


def _render_risk_trend(df: pd.DataFrame, name: str):
    """用 Streamlit/浏览器端图表替代 matplotlib，避免云端中文字体缺失导致乱码。"""
    chart_df = df.copy()
    chart_df["created_at"] = pd.to_datetime(chart_df["created_at"], errors="coerce")
    chart_df["risk_score"] = pd.to_numeric(chart_df["risk_score"], errors="coerce").fillna(0).clip(0, 3)
    chart_df = chart_df.dropna(subset=["created_at"])

    if chart_df.empty:
        st.info("暂无可绘制的风险曲线数据。")
        return

    st.markdown(f"#### {name} 风险曲线")
    plot_df = chart_df[["created_at", "risk_score"]].rename(
        columns={"created_at": "随访时间", "risk_score": "风险分值"}
    )
    st.line_chart(plot_df, x="随访时间", y="风险分值", height=260)
    st.caption("风险分值说明：0=待复拍，1=低风险，2=中风险，3=高风险。")


def render(user: dict):
    require_login()
    hero_banner('康复随访台', '查看连续记录、风险曲线与专家回写的治疗方案。')
    name = st.text_input('患者姓名', value=user['name'] if user['role'] == '村民' else '')
    if not name:
        st.info('请输入患者姓名。')
        return
    visits = list_cases(name)
    if not visits:
        st.warning('暂无记录。')
        return
    df = pd.DataFrame(visits)
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    latest = visits[-1]
    metric_grid([
        ('最新风险', latest.get('risk_level') or '未返回'),
        ('最新建议', latest.get('action_advice') or '未返回'),
        ('专家治疗方案', latest.get('expert_treatment_plan') or '暂未回写'),
        ('专家随访计划', latest.get('expert_followup_plan') or '暂未回写'),
    ])
    _render_risk_trend(df, name)

    table_cols = ['created_at', 'body_part', 'risk_level', 'action_advice', 'trend_summary']
    show_df = df[[c for c in table_cols if c in df.columns]].copy()
    if 'created_at' in show_df.columns:
        show_df['created_at'] = show_df['created_at'].dt.strftime('%Y-%m-%d %H:%M').fillna('')
    show_df = show_df.rename(columns={
        'created_at': '随访时间',
        'body_part': '部位',
        'risk_level': '风险分层',
        'action_advice': '行动建议',
        'trend_summary': '趋势摘要',
    })
    st.dataframe(show_df, use_container_width=True, hide_index=True)

    if latest.get('expert_treatment_plan'):
        st.markdown('#### 专家回写方案')
        render_review_plan(latest)
    notes = list_audio_notes(name)
    if notes:
        st.markdown('#### 对应门诊录音纪要')
        ndf = pd.DataFrame(notes)
        ncols = [c for c in ['created_at', 'status', 'summary_text'] if c in ndf.columns]
        ndf = ndf[ncols].copy()
        if 'created_at' in ndf.columns:
            ndf['created_at'] = pd.to_datetime(ndf['created_at'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M').fillna('')
        ndf = ndf.rename(columns={
            'created_at': '记录时间',
            'status': '状态',
            'summary_text': '纪要摘要',
        })
        st.dataframe(ndf, use_container_width=True, hide_index=True)
