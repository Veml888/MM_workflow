#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""audit_paper_tables.py — 论文表格/表题专项机检（硬门禁，exit 0 才算 PASS）。

检查项：
  T-0 中文字体系统：正文宋体、标题黑体；主字体 SimSun、无衬线字体 SimHei；标题层级、图表题、
      表内文字和源码字号采用固定字体实现。
  T-1 表题/图题标签格式：应为 GB/T 7713 的 "表1 标题"（表号与"表"间无空格、用空格或
      无分隔，禁止冒号）；要求重定义了 \\fnum@table / \\fnum@figure 且 labelsep 用空格。
  T-2 表格列对齐：禁止左对齐 l 或右对齐 r 列，必须居中（c / C{...}）——表头、文字、数字居中。
  T-3 符号说明：只允许一个 longtable（符号|含义|单位），不得"两栏并排/双列分组"，不得包进
      table/floating 浮动环境；longtable 必须具备 \\endfirsthead/\\endhead 续表头。
  T-4 表格字体：表内须为五号宋体（\\songti\\zihao{5}），禁止相对字号或其它中文字体替代。
  T-5 三线表：使用 booktabs 的 \\toprule/\\midrule/\\bottomrule。
  T-5b longtable 跨页续表完整性：必须具备 \\endfirsthead/\\endhead/\\endfoot/\\endlastfoot
      四件套；续页标题必带原表号（\\thetable）；末页底线 \\bottomrule 只允许一条且须在
      \\endlastfoot 内（表末数据行后不得再写第二个 \\bottomrule）。
  T-6 结构：\\end{document} 恰出现一次（防重复）。

用法：python audit_paper_tables.py <论文.tex>
"""

from __future__ import annotations

import re
import sys

# --- UTF-8 输出保护（防乱码）---
if hasattr(sys, "stdout") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys, "stderr") and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# --- /UTF-8 输出保护 ---


def load(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def check(tex, path):
    ok = True
    errs = []

    # ---- T-0 中文字体系统与标题层级 ----
    font_checks = [
        (
            re.search(r'\\setCJKmainfont(?:\[[^\]]*\])?\{\s*SimSun\s*\}', tex, re.I),
            'T-0 缺少 \\setCJKmainfont{SimSun}，正文中文字体必须显式设为宋体',
        ),
        (
            re.search(r'\\setCJKsansfont(?:\[[^\]]*\])?\{\s*SimHei\s*\}', tex, re.I),
            'T-0 缺少 \\setCJKsansfont{SimHei}，中文标题字体必须显式设为黑体',
        ),
        (
            re.search(r'\\songti\s*\\zihao\{-4\}|\\zihao\{-4\}\s*\\songti', tex),
            'T-0 未设置小四号宋体正文（应出现 \\songti\\zihao{-4}）',
        ),
        (
            re.search(r'\\heiti\s*\\zihao\{-3\}|\\zihao\{-3\}\s*\\heiti', tex),
            'T-0 一级标题未设置小三号黑体',
        ),
        (
            re.search(r'\\heiti\s*\\zihao\{4\}|\\zihao\{4\}\s*\\heiti', tex),
            'T-0 二级标题未设置四号黑体',
        ),
        (
            re.search(r'\\heiti\s*\\zihao\{-4\}|\\zihao\{-4\}\s*\\heiti', tex),
            'T-0 三级标题/关键词标签未设置小四号黑体',
        ),
        (
            re.search(r'\\DeclareCaptionFont\{cjkcaption\}\{[^}]*\\songti[^}]*\\zihao\{-4\}[^}]*\}', tex)
            and re.search(r'\\captionsetup(?:\[[^\]]*\])?\{[^}]*font\s*=\s*cjkcaption', tex),
            'T-0 图题/表题未通过 cjkcaption 固定为小四号宋体',
        ),
    ]
    for passed, message in font_checks:
        if not passed:
            errs.append(message)
            ok = False
    if (r'\lstinputlisting' in tex or r'\begin{lstlisting}' in tex) and not re.search(
        r'basicstyle\s*=\s*\{?[^,}\n]*\\ttfamily[^,}\n]*\\zihao\{5\}', tex
    ):
        errs.append('T-0 附录源码未设置五号等宽字体（\\ttfamily\\zihao{5}）')
        ok = False

    # ---- T-1 表题/图题标签：去冒号 + 用空格 + 标签不带空格 ----
    has_labelsep = re.search(r'\\captionsetup(\[[^\]]*\])?\{[^}]*labelsep\s*=\s*space', tex)
    has_fnum_table = re.search(r'\\renewcommand\{\\fnum@table\}\{[^}]*表\s*\\thetable', tex)
    has_fnum_figure = re.search(r'\\renewcommand\{\\fnum@figure\}\{[^}]*图\s*\\thefigure', tex)
    if not has_labelsep:
        errs.append('T-1 缺少 \\captionsetup{labelsep=space}（表题/图题应用空格分隔，避免冒号）')
    if not (has_fnum_table and has_fnum_figure):
        errs.append('T-1 未将 \\fnum@table/\\fnum@figure 设为 表\\thetable / 图\\thefigure（表号与"表/图"间不应有空格）')
    if not (has_labelsep and has_fnum_table and has_fnum_figure):
        ok = False

    # ---- T-2 表格列对齐：禁止 l / r 列与 raggedright/raggedleft 前缀 ----
    def extract_col_spec(tex: str, brace_pos: int) -> str:
        """从 '{' 起做花括号平衡解析，取完整列定义（@{}、>{...} 前缀一并捕获）。"""
        depth, i, n = 0, brace_pos, len(tex)
        while i < n:
            if tex[i] == '{':
                depth += 1
            elif tex[i] == '}':
                depth -= 1
                if depth == 0:
                    return tex[brace_pos + 1:i]
            i += 1
        return tex[brace_pos + 1:brace_pos + 200]

    for m in re.finditer(r'\\begin\{(tabular\*?|longtable)\}\s*\{', tex):
        spec = extract_col_spec(tex, m.end() - 1)
        line = tex[:m.start()].count('\n') + 1
        # 1) 前缀级左/右对齐（藏在 >{...}、@{...}、*{n}{...} 里，旧正则看不到）
        if re.search(r'raggedright|raggedleft', spec):
            errs.append(f'T-2 表格列含 \\raggedright/\\raggedleft（左/右对齐）列前缀（line ~{line}），长文本应用 >{{\\centering\\arraybackslash}}p{{}} 居中换行')
            ok = False
        # 2) 裸 l / r 列：跳过 {...} 花括号组与 >/@ 前缀后检查顶层列字母
        stripped = re.sub(r'[@!>]\s*\{[^{}]*\}', '', spec)   # 去 @{} >{} 前缀
        stripped = re.sub(r'\*\s*\{\d+\}\s*\{([^{}]*)\}', r'\1', stripped)  # 展开 *{n}{cols}
        stripped = re.sub(r'[CpXmbBw]\s*(\[[^\]]*\])?\s*\{[^{}]*\}', '', stripped)  # 去带参列类型
        for c in stripped:
            if c in 'lr':
                errs.append(f'T-2 表格列含左/右对齐 `{c}`（line ~{line}），应为居中 c / C{{}}')
                ok = False

    # ---- T-3 符号说明：单个 longtable、三列、非浮动、含续表头 ----
    sym = re.search(r'\\section\{符号说明\}(.*?)(?=\\section\{|\Z)', tex, re.S)
    if not sym:
        errs.append('T-3 未找到 \\section{符号说明}')
        ok = False
    else:
        block = sym.group(1)
        if r'\FloatBarrier' in block:
            errs.append('T-3 [符号说明] 章内出现 \\FloatBarrier（应就地排版，避免将其后正文/图表推页留白）')
            ok = False
        if block.count(r'\begin{longtable}') != 1:
            errs.append('T-3 符号说明应恰有一个 longtable（当前 %d 个），不得用两栏并排分组' % block.count(r'\begin{longtable}'))
            ok = False
        if r'\begin{table}' in block or r'\begin{figure}' in block:
            errs.append('T-3 符号说明的 longtable 不应包裹在 table/figure 浮动环境中')
            ok = False
        lt = re.search(r'\\begin\{longtable\}\{', block, re.S)
        if lt:
            spec = extract_col_spec(block, lt.end() - 1)
            ncols = len(re.findall(r'[clrCpX]', spec))  # 近似列数
            if ncols < 3:
                errs.append('T-3 符号说明应至少三列（符号|含义|单位）')
                ok = False
            # 提取 body（列定义之后到 \end{longtable}）
            brace_pos = lt.end() - 1
            body_start = brace_pos + 1 + len(spec) + 1
            end_lt = block.find(r'\end{longtable}', body_start)
            body = block[body_start:end_lt] if end_lt >= 0 else ""
            if not (r'\endfirsthead' in body and r'\endhead' in body):
                errs.append('T-3 longtable 缺少 \\endfirsthead / \\endhead（跨页续表头）')
                ok = False
            if '续表' not in body:
                errs.append('T-3 longtable 续页缺少 "续表 N　原表题" 标记')
                ok = False
            # 预留/唯一出现符号检测：每个符号行首列符号应在正文中被使用
            for row in body.split(chr(10)):
                if '&' not in row:
                    continue
                first = row.split('&')[0]
                key = first.strip()
                if '$' in key:
                    a = key.find('$')
                    b = key.rfind('$')
                    key = key[a+1:b]
                key = key.strip()
                if not key:
                    continue
                # 合并单元格（如 w_i,h_i）按分隔符拆分后分别计数
                parts = [p.strip() for p in re.split(r'[,;；、]', key) if p.strip()]
                if not parts:
                    parts = [key]
                for part in parts:
                    cnt = tex.count(part)
                    if cnt <= 1:
                        errs.append(
                            'T-3 符号 `%s` 仅出现在符号表、正文未使用（疑似预留/未用符号，应删除或更正）' % part)
                        ok = False
                    elif cnt == 2:
                        print('  [WARN] T-3 符号 `%s` 只在正文中出现 1 次（疑为"只出现在个别处"的推导中间量/一次性常量）：'
                              '请按"删除后评委是否需回正文"判断，若是中间量请从符号表移除并在正文首次使用处就地说明' % part)

    # ---- T-4 表格字体：五号宋体 ----
    for m in re.finditer(r'\\begin\{(tabular\*?|longtable)\}', tex):
        pre = tex[max(0, m.start() - 300):m.start()]
        has_size = re.search(r'\\zihao\{5\}', pre)
        has_song = re.search(r'\\songti', pre)
        if not (has_size and has_song):
            errs.append(f'T-4 表格未用五号宋体（line ~{tex[:m.start()].count(chr(10))+1}）：应 \\songti\\zihao{{5}}')
            ok = False

    # ---- T-5 三线表：booktabs ----
    if r'\usepackage{booktabs}' not in tex:
        errs.append('T-5 缺少 \\usepackage{booktabs}（三线表）')
        ok = False
    if re.search(r'\\begin\{(tabular\*?|longtable)\}', tex) and not re.search(r'\\toprule', tex):
        errs.append('T-5 表格未使用 \\toprule（三线表）')
        ok = False

    # ---- T-5b longtable 跨页续表完整性：四件套 + 续页标题带表号 + 仅末页一条底线 ----
    # 硬性：endfirsthead / endhead / endfoot / endlastfoot 缺一即 FAIL；
    #       续页标题必带原表号（\\thetable）；\\bottomrule 只允许出现在 endlastfoot 内。
    for m in re.finditer(r'\\begin\{longtable\}\{([^}]*)\}(.*?)\\end\{longtable\}', tex, re.S):
        spec, body = m.group(1), m.group(2)
        line = tex[:m.start()].count('\n') + 1
        for cmd in (r'\endfirsthead', r'\endhead', r'\endfoot', r'\endlastfoot'):
            if cmd not in body:
                errs.append(f'T-5b longtable（第 {line} 行）缺少 {cmd}（跨页续表必须配齐 endfirsthead/endhead/endfoot/endlastfoot 四件套）')
                ok = False
        if r'\endfirsthead' in body and r'\endhead' in body:
            head = body[body.index(r'\endfirsthead'):body.index(r'\endhead')]
            if '续表' not in head:
                errs.append(f'T-5b longtable（第 {line} 行）续页无 "续表 N　原表题" 标题')
                ok = False
            elif r'\thetable' not in head:
                errs.append(f'T-5b longtable（第 {line} 行）续页标题未带原表号：应 \\multicolumn{{N}}{{c}}{{续表\\quad \\thetable\\quad 原表题}}')
                ok = False
        # 三线表末页底线只允许一条，且须位于 \endfoot 与 \endlastfoot 之间的末页页脚段内：
        #   ...\endhead ... 续下页...\endfoot \bottomrule \endlastfoot
        # 不得在表末数据行后单独写第二个 \bottomrule。
        br_count = len(re.findall(r'\\bottomrule', body))
        if br_count > 1:
            errs.append(f'T-5b longtable（第 {line} 行）出现 {br_count} 个 \\bottomrule；三线表末页底线只能有一条，须放在 \\endfoot 与 \\endlastfoot 之间的末页页脚段内')
            ok = False
        elif br_count == 1:
            br_pos = body.find(r'\bottomrule')
            endfoot_pos = body.find(r'\endfoot')
            endlast_pos = body.find(r'\endlastfoot')
            # \bottomrule 必须在 endfoot（若存在）与 endlastfoot 之间
            if endlast_pos == -1:
                errs.append(f'T-5b longtable（第 {line} 行）未配置 \\endlastfoot，末页底线 \\bottomrule 无处安放')
                ok = False
            elif endfoot_pos != -1 and not (endfoot_pos < br_pos < endlast_pos):
                errs.append(f'T-5b longtable（第 {line} 行）\\bottomrule 不在 \\endfoot 与 \\endlastfoot 之间的末页页脚段内')
                ok = False
            elif endfoot_pos == -1 and not (br_pos < endlast_pos):
                errs.append(f'T-5b longtable（第 {line} 行）\\bottomrule 位置异常（应紧邻 \\endlastfoot 之前）')
                ok = False

    # ---- T-6 end{document} 恰一次 ----
    cnt = tex.count(r'\end{document}')
    if cnt != 1:
        errs.append(f'T-6 \\end{{document}} 出现 {cnt} 次，应为 1 次（防重复/结构错误）')
        ok = False

    # ---- T-8 模型章外层结构（参数化骨架）：每问独立成章，标题形如
    #      "（核心模型名）的构建与求解——问题X"（"问题X"可在标题任意位置，
    #      "构建与求解"/"建立与求解"均可），中文序号按题面从"一"起连续；
    #      每问章内含 \subsection{模型建立} 与 \subsection{模型求解} 且建立在前 ----
    numerals = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']
    sec_re = re.compile(r'\\section\{([^}]*)\}')
    sec_positions = [(m.start(), m.group(1)) for m in sec_re.finditer(tex)]
    prob_secs = []
    for pos, title in sec_positions:
        mn = re.search(r'问题([一二三四五六七八九十]{1,2})', title)
        has_name = ('构建与求解' in title) or ('建立与求解' in title)
        if mn and has_name and mn.group(1) in numerals:
            prob_secs.append((numerals.index(mn.group(1)) + 1, pos, title))
    if not prob_secs:
        errs.append('T-8 未找到任何"（核心模型名）的构建与求解——问题X"一级章节；每问应独立成章（见 chapters/05 骨架）')
        ok = False
    else:
        numbers = [n for n, _, _ in prob_secs]
        if numbers != list(range(1, len(numbers) + 1)):
            errs.append('T-8 问题章未按题面从"一"起连续编号（实际：%s）' % ' / '.join(t for _, _, t in prob_secs))
            ok = False
        for i, (num, pos, title) in enumerate(prob_secs):
            next_pos = None
            for p2, _t2 in sec_positions:
                if p2 > pos:
                    next_pos = p2
                    break
            block = tex[pos:next_pos] if next_pos else tex[pos:]
            has_build = re.search(r'\\subsection\{模型建立\}', block)
            has_solve = re.search(r'\\subsection\{模型求解\}', block)
            if not (has_build and has_solve):
                errs.append('T-8 问题%s章（%s）缺少 \\subsection{模型建立}/\\subsection{模型求解} 二分层' % (numerals[num - 1], title))
                ok = False
            elif has_build.start() > has_solve.start():
                errs.append('T-8 问题%s章内"模型建立"应位于"模型求解"之前' % numerals[num - 1])
                ok = False
            if re.search(r'\\paragraph\{', block):
                errs.append('T-8 模型章标题层级超过三级；请将 paragraph 内容并入三级标题或正文')
                ok = False

    # ---- T-9 公式分区/分组左花括号：同一 equation 出现 ≥2 个等号（链式 a=b=c、逗号/\\qquad 并列），
    #      或仅用 \\quad/\\qquad 并列多个约束/表达式（组）而未加 \\left\\{...\\right. 的，一律 FAIL ----
    for m in re.finditer(r'\\begin\{equation\}(.*?)\\end\{equation\}', tex, re.S):
        body = m.group(1)
        if (r'\left\{' in body) or ('aligned' in body) or ('cases' in body):
            continue
        # 下标（如 \prod_{j=1}、\sum_{i=0}）中的 '=' 不是等式，计数前剔除
        body_no_sub = re.sub(r'(_\{[^{}]*\})', lambda mm: mm.group(0).replace('=', ''), body)
        n_eq = body_no_sub.count('=')
        n_sep = len(re.findall(r'\\quad+|\\qquad', body))
        if n_eq < 2 and n_sep < 2:
            continue
        line = tex[:m.start()].count('\n') + 1
        errs.append('T-9 公式（约第 %d 行）含 ≥2 个等号（链式/并列）或仅用 `\\quad`/`\\qquad` 并列多个约束/表达式，但未用左花括号 `\\left\\{...\\right.`（`aligned`/`cases`）逐行排版、每行一个表达式、共享一个式号' % line)
        ok = False

    # ---- T-10 图题/表题短命名：不得用冒号写"名称：解释"，且长度适中 ----
    for m in re.finditer(r'\\caption\{([^}]*)\}', tex):
        cap = m.group(1)
        if '：' in cap or ':' in cap:
            line = tex[:m.start()].count('\n') + 1
            errs.append(f'T-10 题注（约第 {line} 行）含冒号"{cap}"，应为极简名词短语，说明/结论放正文首次引用处')
            ok = False
        if len(cap) > 22:
            line = tex[:m.start()].count('\n') + 1
            errs.append(f'T-10 题注（约第 {line} 行）过长（{len(cap)} 字）："{cap}"；应缩短为对象名（通常 ≤16 字）')
            ok = False

    # ---- T-11 交叉引用颜色：应使用 hidelinks 或明确把链接颜色设为黑 ----
    has_hidelinks = re.search(r'\\usepackage\[[^\]]*hidelinks[^\]]*\]\{hyperref\}', tex)
    black_setup = re.search(r'\\hypersetup\{[^}]*linkcolor\s*=\s*(black|Black)', tex) or \
                  re.search(r'\\usepackage\[[^\]]*colorlinks=true[^\]]*\][^\n]*black', tex)
    if not (has_hidelinks or black_setup):
        errs.append('T-11 交叉引用被着色：导言区未用 `hidelinks`，也未把 `linkcolor`/`citecolor` 设为 black。'
                    '（引用应显示为普通黑色，可按需用 `\\usepackage[hidelinks]{hyperref}`；不必可点击）')
        ok = False

    return ok, errs


def main():
    if len(sys.argv) < 2:
        print('usage: python audit_paper_tables.py <论文.tex>')
        return 2
    path = sys.argv[1]
    tex = load(path)
    ok, errs = check(tex, path)
    if ok:
        print('paper table checks: PASS')
        return 0
    print('paper table checks: FAIL')
    for e in errs:
        print('  -', e)
    return 1


if __name__ == '__main__':
    sys.exit(main())
