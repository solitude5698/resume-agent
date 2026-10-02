import tempfile
from pathlib import Path

import streamlit as st

from resume_agent.agent import analyze_resume
from resume_agent.file_loader import load_resume


st.set_page_config(
    page_title="简历分析 Agent",
    page_icon="📄",
    layout="wide",
)

st.title("📄 简历分析 Agent")
st.caption("上传简历 + 粘贴岗位 JD，自动分析匹配度、缺失关键词、改写建议")

with st.sidebar:
    st.header("🔑 DeepSeek API Key")
    st.caption(
        "本项目不存储你的 Key。"
        "Key 仅用于本次请求，不会上传到服务器。"
    )
    user_api_key = st.text_input(
        "填入你自己的 DeepSeek API Key",
        type="password",
        placeholder="sk-...",
    )
    st.markdown("获取方式：https://platform.deepseek.com")

    st.divider()

    st.header("📖 使用说明")
    st.markdown(
        """
        1. 填入 DeepSeek API Key
        2. 上传简历（PDF / DOCX / TXT）
        3. 粘贴目标岗位 JD
        4. 填写你的求职背景
        5. 点击「开始分析」
        """
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("① 上传简历")
    resume_file = st.file_uploader(
        "支持 PDF / DOCX / TXT",
        type=["pdf", "docx", "txt"],
    )

with col2:
    st.subheader("② 岗位 JD")
    jd_text = st.text_area(
        "粘贴岗位描述",
        height=260,
        placeholder="把 BOSS / 实习僧 / 公司官网的 JD 复制到这里",
    )

st.subheader("③ 你的求职背景")
profile_text = st.text_area(
    "让 AI 知道你是谁",
    height=160,
    placeholder=(
        "例如：\n"
        "身份：在校本科生\n"
        "毕业时间：2028 年\n"
        "求职类型：实习 / 校招\n"
        "目标方向：AI Agent 后端\n"
        "当前水平：Python、Java、MySQL\n"
        "正在学习：Docker、K8s、LangChain"
    ),
)

if st.button("🚀 开始分析", type="primary"):
    if not user_api_key.strip():
        st.warning("请先在左侧填入你的 DeepSeek API Key")
        st.stop()

    if resume_file is None:
        st.warning("请先上传简历")
        st.stop()

    if not jd_text.strip():
        st.warning("请粘贴岗位 JD")
        st.stop()

    if not profile_text.strip():
        st.warning("请填写求职背景")
        st.stop()

    suffix = Path(resume_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(resume_file.read())
        tmp_path = Path(tmp.name)

    try:
        resume_text = load_resume(tmp_path)
    except Exception as e:
        st.error(f"读取简历失败：{e}")
        st.stop()
    finally:
        tmp_path.unlink(missing_ok=True)

    with st.spinner("正在分析简历..."):
        try:
            result = analyze_resume(
                profile_text,
                resume_text,
                jd_text,
                api_key=user_api_key,
            )
        except Exception as e:
            st.error(f"分析失败：{e}")
            st.stop()

    st.success("分析完成！")

    st.markdown("### 岗位级别")
    c1, c2, c3 = st.columns(3)
    c1.metric("JD 级别", result["jd_level"])
    c2.metric("你的阶段", result["candidate_level"])
    c3.metric("是否错配", "是" if result["level_mismatch"] else "否")

    st.markdown("### 匹配分数")
    st.progress(result["match_score"] / 100)
    st.write(f"**{result['match_score']} 分** —— {result['match_level']}")

    st.markdown("### 匹配关键词")
    st.write("　".join(f"✅ {k}" for k in result["matched_keywords"]))

    st.markdown("### 硬性缺失")
    if result["missing_hard_keywords"]:
        st.write("　".join(f"❌ {k}" for k in result["missing_hard_keywords"]))
    else:
        st.write("无")

    st.markdown("### 加分项缺失")
    if result["missing_nice_to_have"]:
        st.write("　".join(f"⚠️ {k}" for k in result["missing_nice_to_have"]))
    else:
        st.write("无")

    st.markdown("### 正在学习")
    if result["learning_keywords"]:
        st.write("　".join(f"📘 {k}" for k in result["learning_keywords"]))
    else:
        st.write("无")

    st.markdown("### 简历问题")
    for issue in result["resume_issues"]:
        st.write(f"- {issue}")

    st.markdown("### 改写建议")
    for s in result["rewrite_suggestions"]:
        st.write(f"- {s}")

    st.markdown("### 定制摘要")
    st.info(result["custom_summary"])

    st.markdown("### 求职信")
    st.text_area("复制这段", result["cover_letter"], height=220)

    report_lines = [
        "# 简历分析报告",
        "",
        "## 岗位级别",
        f"- JD 级别：{result['jd_level']}",
        f"- 你的阶段：{result['candidate_level']}",
        f"- 是否错配：{result['level_mismatch']}",
        "",
        "## 匹配分数",
        f"**{result['match_score']}** —— {result['match_level']}",
        "",
        "## 匹配关键词",
        *[f"- ✅ {k}" for k in result["matched_keywords"]],
        "",
        "## 硬性缺失",
        *[f"- ❌ {k}" for k in result["missing_hard_keywords"]],
        "",
        "## 加分项缺失",
        *[f"- ⚠️ {k}" for k in result["missing_nice_to_have"]],
        "",
        "## 正在学习",
        *[f"- 📘 {k}" for k in result["learning_keywords"]],
        "",
        "## 简历问题",
        *[f"- {i}" for i in result["resume_issues"]],
        "",
        "## 改写建议",
        *[f"- {s}" for s in result["rewrite_suggestions"]],
        "",
        "## 定制摘要",
        result["custom_summary"],
        "",
        "## 求职信",
        result["cover_letter"],
    ]
    report_md = "\n".join(report_lines)

    st.download_button(
        "⬇️ 下载 Markdown 报告",
        data=report_md,
        file_name="resume_report.md",
        mime="text/markdown",
    )