---
name: python-learn
description: Python学习助手。记录和查询学习进度。触发词：Python进度/学Python/记录学习/考核/掌握
---

# Python 学习助手

> 技能目录：`/vol1/@apphome/trim.openclaw/data/workspace/skills/python-learn/`
> 数据目录：`/vol1/1000/appRunData/PythonLearn/`
> 进度数据：`学习进度.csv`

## 一、核心命令

用户说"Python进度"时，执行：
`python3 /vol1/@apphome/trim.openclaw/data/workspace/skills/python-learn/scripts/query.py stats`

用户说"开始学 PY-003"时，执行：
`python3 /vol1/@apphome/trim.openclaw/data/workspace/skills/python-learn/scripts/query.py learn PY-003`

用户说"考核 PY-002"或"测测我掌握了 PY-002"时，执行：
`python3 /vol1/@apphome/trim.openclaw/data/workspace/skills/python-learn/scripts/query.py assess PY-002`

非交互模式（AI 代驱动）：
1. 提交答案：`python3 query.py assess PY-002 --submit answers.txt`
   - 若无待答题目，脚本自动生成题目并打印，写入 pending.json
   - AI 向用户展示题目、收集答案，写入文件（答案间用空行分隔）
2. 再次提交：`python3 query.py assess PY-002 --submit answers.txt`
   - 脚本读取答案、判分、更新状态

答案文件格式：各题答案之间用空行分隔，按顺序对应。支持多行代码答案。

注意：`assess`（不带 --submit）检测到非交互 stdin 时会拒绝运行，避免空输入触发学习模式污染数据。

禁止手动标记“已掌握”；“已掌握”只能由 `assess` 考核判定。

## 新增命令

用户说"查一下 Python 的 XXX"或"Python 教程里有没有 XXX"时，执行：
`python3 /vol1/@apphome/trim.openclaw/data/workspace/skills/python-learn/scripts/search.py XXX`

## 二、严格掌握判定（参考钱学森《工程控制论》）

“掌握”定义为：一个闭环控制系统在输入、输出、反馈、扰动和时间稳定性考验下，仍能保持正确输出。

每个知识点必须依次通过三关，全部通过才允许标记“已掌握”：

1. 第1关 概念与输出：不看资料，用自己的话讲清概念、用途和边界条件并举例，再独立完成一道基础编码题，代码可运行、结果正确。
2. 第2关 反馈与扰动：找出示例代码中的典型错误并改正、说清原因，再换参数、换场景、加限制连续完成 2 道变式题，仍保持正确。
3. 第3关 时间稳定：前两关通过后间隔 3 天复测，仍能独立做对。

判定规则：

- 当前关未通过 → 状态“学习中”，记录卡在第几关
- 第1关通过 → 进入第2关
- 第2关通过 → 状态“待复测”，3 天后才能复测
- 复测通过 → “已掌握”，写入掌握日期
- 复测失败 → 退回第2关重新考核

AI 考官规则：

- 每次只出一题，不提前泄露答案
- 判定必须严格：无提示、独立完成、代码能运行、不认可含糊答案
- 只输出 `PASS` 或 `FAIL`，附不超过两行的理由
- 不允许用户说“我掌握了”就标记已掌握，不允许任何手动改状态
- 每次考核后更新 CSV 的“当前关卡、考核次数、上次考核日期、待复测日期、考核记录”字段
- 【固定】双考官制：用户答完题，必须先贴给 Clawver 预审，由 Clawver 独立判断答案是否达标；Clawver 预审通过，才允许提交给脚本考官（`query.py assess`，DeepSeek 判分）。预审不通过直接 FAIL，不调用脚本、不推进关卡。
- 【固定】若 Clawver 预审通过、但脚本考官判 FAIL，取脚本考官给的理由原文，由 Clawver 独立复核、重新判断实际是否通过；Clawver 不得直接改 CSV 状态。
- 【固定】冲突处置优先级：Clawver 判断优先；双方复核后仍不一致，走人工复核兜底（沿用 `query.py` CSV 考核记录中“人工复核”先例）。

## 学习模式

- 当用户提交“不会”“不会做”“不知道”时，进入分步学习模式：
  - 教学输出前必须自检：只给思路，不贴完整代码。
  - 不判分、不记录失败、不推进关卡。
  - 把当前题目拆成 3 个小台阶，逐级引导。
  - 每个台阶只提示思路，不直接给完整答案。
  - 学完 3 个台阶后，询问是否重新考核。
  - 用户输入 `r` 重新考核，输入 `q` 退出；退出不改变当前关卡。

## 三、技能脚本

脚本路径：`scripts/query.py`、`scripts/search.py`

- `stats`：查询进度
- `learn`：标记开始学习
- `assess`：AI 三关严格考核
- `search`：查询教程内容

## 四、双考官审核流程（固定规则 · 每次考核必读）

### 4.0 角色
| 角色 | 载体 | 职责 |
|---|---|---|
| 第一考官 Clawver | 本助手（OpenClaw） | 答案达标性预审、冲突复核 |
| 第二考官 脚本考官 | `query.py assess`（DeepSeek 判分） | 最终判分、状态推进、写 CSV |
| 人工复核 | 兜底 | 双方复核后仍不一致时启用 |

### 4.1 强制顺序
用户提交答案 → Clawver 预审 → 预审通过才执行 `query.py assess --submit` → 脚本考官 PASS/FAIL → 按结果推进关卡。

- 未经 Clawver 预审通过，禁止调用 `query.py assess`。
- Clawver 预审不通过：只回 FAIL + ≤2 行理由，不调用脚本，不推进关卡，默认不累加考核次数。
- Clawver 预审通过：才执行
  `python3 /vol1/@apphome/trim.openclaw/data/workspace/skills/python-learn/scripts/query.py assess <ID> --submit <answers_file>`。

### 4.1.1 非交互考核流程（AI 代驱动）

由于脚本考官是纯交互式 stdin 判分，AI 无法直接在终端中作答。改用以下流程：

1. **首次提交（自动生成题目）**：AI 调用 `assess <ID> --submit <answers_file>`，若 `pending.json` 中没有对应关卡的题目，脚本自动调用 DeepSeek 生成题目、写入 `pending.json`、打印题目后退出（不判分）。
2. **收集答案**：AI 向用户逐题展示题目，收集用户答案，写入临时文件（各题答案之间用空行分隔，支持多行代码）。
3. **再次提交（判分）**：AI 调用 `assess <ID> --submit <answers_file>`，脚本读取 pending.json 中的题目和文件中的答案，判分并更新状态。

关键约束：
- `assess`（不带 `--submit`）检测到 stdin 不是终端时，会拒绝运行并报错，防止空输入触发学习模式。
- `--submit` 模式不需要交互终端，完全非交互。
- 题目生成和答案提交可以分开进行，中间可以有任意延迟。
- 答案文件格式：各题答案之间用空行分隔（不是每行一题），支持多行代码答案。
- 如果 `pending.json` 中有残留题目导致每次 assess 加载同一道题，用 `clear <ID>` 清除后重新出题。

### 4.2 Clawver 预审标准
1. 无提示、无抄资料：答案只能来自用户自己。
2. 独立完成：代码可运行，且用户给出实际运行输出/结果。
3. 不含糊：概念有用途、边界条件、反例；编码题有明确输入输出。
4. 输出格式：只输出 `PASS` 或 `FAIL`，附不超过两行理由。
5. 禁止：不给提示、不泄露答案、不代改代码、不代跑结果。

### 4.3 冲突处理
- Clawver PASS + 脚本 FAIL：取脚本考官理由原文，由 Clawver 独立复核。
- 复核认为确不达标：以 FAIL 为准，考核记录写 `C复核改判:FAIL`。
- 复核坚持通过：不覆盖脚本状态，转 4.4 人工复核。
- Clawver FAIL + 用户申诉：允许一次复核，仍 FAIL 则维持。
- 任何环节，Clawver 不得把状态改成“已掌握”。

### 4.4 人工复核兜底
- 触发：Clawver 与脚本考官结论不一致，且 Clawver 复核后仍不一致。
- 写法：沿用历史先例，写入 CSV `考核记录` 字段：
  `人工复核:<日期> <分歧点> <结论>`
- 默认只走 1 轮。

### 4.5 记录规范
- Clawver 预审结论追加到 `考核记录`：`C:PASS` / `C:FAIL`。
- 链路示例：
  - 双通过：`C:PASS|S:PASS`
  - 冲突：`C:PASS|S:FAIL|C复核:PASS|人工复核:<日期> 分歧点 结论`
- `当前关卡`、`考核次数`、`上次考核日期`、`待复测日期`，一律由脚本考官结果写入，Clawver 不直接改。
- 仅预审不通过时，默认不累加“考核次数”。

### 4.6 与学习模式边界
- 用户回”不会 / 不会做 / 不知道” → 进入学习模式：不判分、不预审、不调 `assess`、不推进关卡。
- 3 个台阶只给思路，不贴完整代码。
- `r` 重考，`q` 退出；退出不改变当前关卡。
- `assess`（不带 `--submit`）在非交互 stdin 下会拒绝运行，不会触发学习模式，避免污染考核记录。
- 如果 `pending.json` 中有残留题目导致每次 assess 加载同一道题，用 `clear <ID>` 清除后重新出题。

### 4.7 每次会话必读
凡涉及 Python 学习/记录的会话，先读：第二节（严格掌握判定 + AI 考官规则）、第三节、本节，再执行任何命令。