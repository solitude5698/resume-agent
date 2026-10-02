# 📄 简历分析 Agent

基于 DeepSeek 大模型的智能简历分析 Agent。上传简历 + 粘贴岗位 JD，自动分析匹配度，生成改写建议、定制摘要和求职信。

## ✨ 功能

- 📄 支持 PDF / DOCX / TXT 三种简历格式
- 🎯 岗位级别识别：自动判断 JD 属于实习 / 校招 / 中级 / 资深
- 📊 匹配分数：0-100 分，区分硬性缺失、加分项、正在学习
- ✍️ 智能改写建议：针对目标岗位给出具体可执行的修改方案
- 📝 自动生成定制摘要和求职信
- ⬇️ 一键下载 Markdown 报告
- 🖥️ Streamlit 网页界面，无需命令行

## 🛠️ 技术栈

- Python 3.13
- DeepSeek API（兼容 OpenAI SDK）
- Streamlit（网页界面）
- pypdf / python-docx（文件解析）
- rich（终端美化）

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/solitude5698/resume-agent.git
cd resume-agent