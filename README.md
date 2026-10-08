# python-learn

一个基于「严格掌握判定」的 Python 学习助手技能。核心理念参考钱学森《工程控制论》：一个知识点只有在输入、输出、反馈、扰动和时间稳定性考验下仍能保持正确输出，才算真正掌握。

## 三关考核

每个知识点必须依次通过三关，全部通过才标记「已掌握」：

1. **第 1 关 · 概念与输出**：不看资料讲清概念、用途、边界条件并举例，再独立完成一道基础编码题。
2. **第 2 关 · 反馈与扰动**：找出示例代码的典型错误并改正、说清原因，再完成 2 道变式题。
3. **第 3 关 · 时间稳定**：前两关通过后间隔 3 天复测，仍能独立做对。

判定由 DeepSeek 驱动的脚本考官（`query.py`）完成，只输出 `PASS` / `FAIL`，禁止任何手动改状态。

## 命令

```bash
# 查询学习进度
python3 scripts/query.py stats

# 标记开始学习某知识点
python3 scripts/query.py learn PY-001

# 交互式考核（需终端）
python3 scripts/query.py assess PY-001

# 非交互考核（AI 代驱动）：首次调用自动生成题目并写入 pending.json
python3 scripts/query.py assess PY-001 --submit answers.txt
# 收集用户答案写入 answers.txt 后，再次调用即判分
python3 scripts/query.py assess PY-001 --submit answers.txt

# 清除某知识点残留的待答题目，重新出题
python3 scripts/query.py clear PY-001

# 查询教程内容
python3 scripts/search.py <关键词>
```

## 答案文件格式（重要）

`--submit` 模式按**空行**切分答案，每个空行分隔的文本块按顺序对应一道题：

- 各题答案之间用**恰好一个空行**分隔。
- **不要**用 `---`、`===` 等分隔符。
- 单个答案内部**不要**留空行（会被误当成题目边界）。
- 支持多行代码答案，只要块内不含空行。

脚本用 `re.split(r"\n\s*\n", content)` 切分。注意：一次 FAIL 会清空 `pending.json` 并重新出题，失败的答案无法再次提交，因此提交前务必确认格式正确。

## 配置

在数据目录放置 `.env` 提供 DeepSeek 密钥（不随仓库提交）：

```
DEEPSEEK_API_KEY=sk-你的密钥
```

## 文件结构

```
SKILL.md            技能说明与双考官审核规则
scripts/query.py    进度记录 + 三关考核 + 判分主程序
scripts/search.py   教程内容检索
```
