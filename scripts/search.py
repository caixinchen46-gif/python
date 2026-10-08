#!/usr/bin/env python3
"""闭环检索：输入关键词 -> 多轮检索 -> 反馈扩展 -> 输出结果并记录日志。"""

import csv
import os
import re
import sys
from datetime import datetime

TUTORIAL_DIR = os.getenv(
    "PYTHON_TUTORIAL_DIR",
    "/vol1/1000/appRunData/PythonLearn/Python-100-Days",
)

DATA_DIR = os.getenv(
    "PYTHON_LEARN_DATA_DIR",
    "/vol1/1000/appRunData/PythonLearn",
)
SEARCH_LOG = os.path.join(DATA_DIR, "搜索日志.csv")

EXTS = (".md", ".txt", ".rst")
MIN_HITS = 1
MAX_RESULTS = 10
CONTEXT_LINES = 2


def normalize(text):
    return re.sub(r"\s+", "", text).lower()


def score_file(path, keyword):
    normalized_keyword = normalize(keyword)
    if not normalized_keyword:
        return 0, []

    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, OSError):
        return 0, []

    hits = []
    for i, line in enumerate(lines):
        if normalized_keyword in normalize(line):
            hits.append(i)
    return len(hits), hits


def search_once(keyword):
    results = []
    if not normalize(keyword):
        return results

    for root, dirs, files in os.walk(TUTORIAL_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files:
            if not name.lower().endswith(EXTS):
                continue
            path = os.path.join(root, name)
            count, hits = score_file(path, keyword)
            if count:
                results.append((count, path, hits))

    results.sort(key=lambda item: (-item[0], item[1]))
    return results


def expand_keywords(keyword):
    expanded = [keyword]

    stripped = re.sub(r"[\s，。！？、（）()\-_/]+", "", keyword)
    if stripped and stripped != keyword:
        expanded.append(stripped)

    parts = [p for p in re.split(r"[\s，。！？、（）()\-_/]+", keyword) if p]
    if len(parts) > 1:
        expanded.extend(parts)

    # 去重，保持顺序
    unique = []
    seen = set()
    for item in expanded:
        norm = normalize(item)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        unique.append(item)

    return unique


def merge_results(result_groups):
    """合并多轮检索结果，同一文件保留命中数更高的记录。"""
    merged = {}
    for results in result_groups:
        for count, path, hits in results:
            old = merged.get(path)
            if old is None or count > old[0]:
                merged[path] = (count, path, hits)

    merged_list = list(merged.values())
    merged_list.sort(key=lambda item: (-item[0], item[1]))
    return merged_list


def read_snippet(path, hit_line, context=CONTEXT_LINES):
    """安全读取命中行附近的摘要。"""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, OSError) as exc:
        return f"[无法读取文件：{exc}]"

    if not lines:
        return ""

    start = max(0, hit_line - context)
    end = min(len(lines), hit_line + context + 1)
    return "".join(lines[start:end]).strip()


def log_search(keyword, hit_count, status):
    """记录搜索日志。日志写入失败不应影响主流程。"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)

        # 文件不存在，或存在但为空，都需要写表头
        is_new = not os.path.exists(SEARCH_LOG) or os.path.getsize(SEARCH_LOG) == 0

        with open(SEARCH_LOG, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(["时间", "关键词", "命中数", "状态"])
            w.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                keyword,
                hit_count,
                status,
            ])
    except OSError as exc:
        print(f"警告：写入搜索日志失败：{exc}", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print("用法：python3 search.py 关键词")
        sys.exit(1)

    keyword = " ".join(sys.argv[1:]).strip()

    if not normalize(keyword):
        print("关键词不能为空（或只包含空白字符）。")
        log_search(keyword, 0, "无效关键词")
        sys.exit(1)

    if not os.path.isdir(TUTORIAL_DIR):
        print(f"教程目录不存在：{TUTORIAL_DIR}")
        print("请把 TUTORIAL_DIR 改成教程实际路径，或用 PYTHON_TUTORIAL_DIR 指定。")
        sys.exit(1)

    results = search_once(keyword)
    used_expansions = []

    # 直接检索命中不足时，进行多轮扩展检索，并合并结果
    if len(results) < MIN_HITS:
        result_groups = [results] if results else []

        for variant in expand_keywords(keyword):
            if normalize(variant) == normalize(keyword):
                continue

            extra = search_once(variant)
            if extra:
                used_expansions.append(variant)
                result_groups.append(extra)

        if result_groups:
            results = merge_results(result_groups)

    if not results:
        print(f"没有在教程中找到：{keyword}")
        log_search(keyword, 0, "未命中")
        return

    print(f"关键词：{keyword}")
    if used_expansions:
        print("直接检索命中不足，已扩展检索：" + "、".join(used_expansions))

    show_count = min(len(results), MAX_RESULTS)
    print(f"找到 {len(results)} 个相关文件，显示前 {show_count} 个：\n")

    for count, path, hits in results[:MAX_RESULTS]:
        rel = os.path.relpath(path, TUTORIAL_DIR)
        print(f"[{rel}] 命中 {count} 处")

        snippet = read_snippet(path, hits[0])
        if snippet:
            print(snippet)
        print()

    log_search(keyword, len(results), "命中")


if __name__ == "__main__":
    main()