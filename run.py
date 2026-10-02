from pathlib import Path
from datetime import datetime
from rich import print

from resume_agent.agent import analyze_resume
from resume_agent.file_loader import load_resume, find_resume


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def save_markdown(result: dict, jd_name: str) -> Path:
    Path("output").mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path("output") / f"report_{jd_name}_{timestamp}.md"

    lines = [
        "# 简历分析报告",
        "",
        f"- 生成时间：{timestamp}",
        f"- 目标岗位：{jd_name}",
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
        "",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main():
    data_dir = Path("data")

    profile = load_text("data/profile.txt")
    jd = load_text("data/jd.txt")

    resume_path = find_resume(data_dir)
    print(f"[bold green]找到简历文件：{resume_path}[/bold green]")
    resume = load_resume(resume_path)

    print("[bold green]正在分析简历...[/bold green]")
    result = analyze_resume(profile, resume, jd)

    print("\n[bold cyan]===== 岗位级别 =====[/bold cyan]")
    print(f"JD 级别：{result['jd_level']}")
    print(f"你的阶段：{result['candidate_level']}")
    if result["level_mismatch"]:
        print("[bold red]⚠️ 岗位级别与你的阶段不匹配[/bold red]")
    else:
        print("[bold green]✅ 岗位级别与你的阶段匹配[/bold green]")

    print("\n[bold cyan]===== 匹配分数 =====[/bold cyan]")
    print(result["match_score"])
    print(result["match_level"])

    print("\n[bold cyan]===== 匹配关键词 =====[/bold cyan]")
    for kw in result["matched_keywords"]:
        print(f"  ✅ {kw}")

    print("\n[bold cyan]===== 硬性缺失 =====[/bold cyan]")
    for kw in result["missing_hard_keywords"]:
        print(f"  ❌ {kw}")

    print("\n[bold cyan]===== 加分项缺失 =====[/bold cyan]")
    for kw in result["missing_nice_to_have"]:
        print(f"  ⚠️ {kw}")

    print("\n[bold cyan]===== 正在学习 =====[/bold cyan]")
    for kw in result["learning_keywords"]:
        print(f"  📘 {kw}")

    print("\n[bold cyan]===== 简历问题 =====[/bold cyan]")
    for issue in result["resume_issues"]:
        print(f"  - {issue}")

    print("\n[bold cyan]===== 改写建议 =====[/bold cyan]")
    for s in result["rewrite_suggestions"]:
        print(f"  - {s}")

    print("\n[bold cyan]===== 定制摘要 =====[/bold cyan]")
    print(result["custom_summary"])

    print("\n[bold cyan]===== 求职信 =====[/bold cyan]")
    print(result["cover_letter"])

    jd_name = input("\n给这次分析起个名字：").strip()
    if not jd_name:
        jd_name = "default"

    out_path = save_markdown(result, jd_name)
    print(f"\n[bold green]报告已保存：{out_path}[/bold green]")


if __name__ == "__main__":
    main()