# B · style_strip 代码内容保护设计方案（v2，返修稿）

- **文档类型**：设计方案（不施工，待复审）
- **任务**：B（style_strip 代码内容保护）独立立项设计
- **版本**：方案 v2（按复审意见返修；v1 暂不通过）
- **日期**：2026-11-22
- **更新时间**：2026-11-22 12:50（Asia/Shanghai）
- **当前状态**：**设计返修完成，待复审；未改代码/配置/线上**
- **对应 commit**：无（未施工）

## 〇、v1 阻断项与返修

v1 用“连续两行缩进”识别无围栏代码，**无法覆盖真实 69 字符样本的首行和末行**：

```
def add(a, b):          ← 首行无缩进，v1 不纳入
    result = a + b
    return result

print(add(2, 3))        ← 末行无缩进，v1 不纳入
```

真实变形正是首行 `,` → `，`、末行 `,` → `，` 加上缩进/空行丢失。v2 改为“代码起始行 + 块扩展”，首末行都纳入；并把完整真实样本列为**逐字节保真必测项**。

## 一、目标

让 `style_strip` 在保持“短消息口语化”行为的同时，识别并**逐字节保护**代码内容；不改变 `max_len` 旧行为；不扩展到 `multi_bubble` / `rule_guard`。

## 二、现状

线上 `astrbot_plugin_style_strip/main.py`（SHA `bb2e9984…`）：

- `restyle()`：逐行 `fix_punctuation`、`[ \t]{2,}→1`、行首 `^[，\s]+` 清空、`strip()`；
- `squash_blank()`：删空行；
- `fix_quotes()`：引号替换；
- 无代码检测；配置 `enable=true`、`max_len=400`。

## 三、识别设计（v2）

### 3.1 围栏代码

````
``` / ~~~（长度 ≥3，同字符关闭；关闭行只允许空白；支持 CRLF `\r?$`；
未闭合 → 保护到末尾；四反引号开、三反引号关不算关闭。
````

### 3.2 无围栏代码（重点返修）

**候选起始行条件**（同时满足）：

1. 行首匹配代码关键字：`async def|def|class|import|from|for|if|elif|else|while|try|except|finally|with|return|yield|raise|assert|print|lambda|@[\w.]+`（只匹配 ASCII 小写/关键字，中文“如果/当”不匹配）；
2. 行内含有代码符号之一：`:`、`=`、`(`、`[`、`{`、`->`，或下一行以 2+ 空格/Tab 缩进；
3. 不是列表（`^\s*[-*+]\s`）、不是引用（`^\s*>`）、不是表格（`^\s*\|`）。

**块扩展**（从起始行 i 开始）：

- 包含起始行；
- 后续行按顺序：
  - 缩进行（`^(?: {2,}|\t)`）→ 包含；
  - 空行 → 暂存；若下一行仍是缩进行/代码行/闭合行，则保留空行并继续，否则结束于空行前；
  - 非缩进但匹配代码关键字、或闭合行（`^\s*[)\]}]+;?$`）、或 `^\s*(else|elif|except|finally)\b` → 包含；
  - 其它行 → 结束。

真实样本走这条规则：`def add(a, b):`（含 `:`+`(`）起始 → 缩进行 → 空行（下一行 `print` 是代码行，保留）→ `print(add(2, 3))`（含 `(`，包含）→ 结束。整段 69 字符逐字节保护。

**误判反例（必须不纳入）**：

- 中文段落：“如果明天有空，我们就去…”（不匹配 ASCII 关键字）；
- 英文句子：“If you want, we can talk.”（`If` 匹配但行内无 `:`/`=`/`(`/`[`/`{`/`->`，且下一行不缩进 → 排除）；
- 列表：“- 第一项”“1. 第一项”；
- 引用：“> 引用文字”；
- 表格：“| a | b |”。

### 3.3 行内代码

- 单反引号：`` `code` ``（前后不能是反引号）；
- 双反引号：`` ``code`` ``；
- 未闭合单/双反引号：保护到**行尾**（不跨行）；
- 围栏内不再识别行内代码，避免嵌套误判。

### 3.4 扫描异常

`_code_regions()` 抛异常时：

```python
try:
    regions = _code_regions(text)
except Exception as e:
    logger.warning(f"[style_strip] 代码识别失败，按原文返回（{type(e).__name__}）")
    return text   # 整条原文，不执行 restyle
```

即：**扫描异常返回整条原文，不继续执行 restyle**（不是“跳过保护继续处理”）。

### 3.5 max_len 兼容

保持旧行为：先判断

```python
if len(text) > max_len:
    return text   # 与旧版一致：超长不处理
```

只有 `≤ max_len` 才进入保护 + restyle。这样不改变长消息行为。

## 四、分段处理

```python
def protected_restyle(text, max_len):
    if len(text) > max_len:
        return text
    try:
        regions = _code_regions(text)
    except Exception as e:
        logger.warning(...)
        return text
    out, last = [], 0
    for s, e in regions:
        out.append(restyle_noncode(text[last:s]))
        out.append(text[s:e])       # 逐字节
        last = e
    out.append(restyle_noncode(text[last:]))
    return "".join(out)
```

`restyle_noncode` 内部仍走原有 `fix_punctuation` / 空格压缩 / 行首清理 / `strip` / `squash_blank` / `fix_quotes`；保护区内不执行这些。

## 五、验收矩阵（必须覆盖）

| # | 场景 | 期望 |
|---|---|---|
| 1 | **完整真实 69 字符样本**（首行 `def`、末行 `print`、缩进、空行、逗号） | 逐字节不变 |
| 2 | ``` 围栏（含 CRLF、未闭合、四反引号） | 围栏内不变；围栏外正常 |
| 3 | ~~~ 围栏 | 同上 |
| 4 | 无围栏缩进块（仅缩进，无起始关键字） | 按块保护 |
| 5 | 中文段落 / 列表 / 引用 / 英文句子 | **不**被误保护，正常 restyle |
| 6 | 单反引号、双反引号 | 不变 |
| 7 | 未闭合单/双反引号 | 保护到行尾 |
| 8 | 代码内 `, ; 、 。 「」`、URL/数字逗号 | 不变 |
| 9 | 扫描异常（强制 raise） | 整条原文返回，不 restyle |
| 10 | `len > max_len` | 原样返回（旧行为） |
| 11 | 二次处理 | 幂等 |

## 六、范围与不做

- 只改 `astrbot_plugin_style_strip/main.py` 与对应测试；
- 不扩展到 `multi_bubble._tidy`、`rule_guard`（相邻通道独立立项）；
- 不改 AstrBot 核心、配置默认值；
- 本轮不施工、不部署、不重启。

## 七、待复审

1. 无围栏识别规则是否接受“起始关键字 + 代码符号/下一行缩进”的条件；
2. 未闭合行内代码保护到行尾是否符合预期；
3. 扫描异常“整条原文返回”是否符合 fail-open 预期；
4. 是否把 `max_len` 截断改为“代码段不计入”，还是保持整条超长不处理（v2 选择保持旧行为）。
