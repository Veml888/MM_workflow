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
  T-6 结构：\\end{document} 恰出现一次（防重复）。

用法：python audit_paper_tables.py <论文.tex>
"""

import re
import sys


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

    # ---- T-2 表格列对齐：禁止 l / r 列 ----
    for m in re.finditer(r'\\begin\{(tabular\*?|longtable)\}\{([^}]*)\}', tex):
        spec = m.group(2)
        # 去除 C{...}（居中定宽列）与 p{...}/X 等后，看剩余单字符列类型的字母
        strip = re.sub(r'[CpX][^{}]*\{[^}]*\}', '', spec)
        bare = [c for c in strip if c.isalpha()]
        for c in bare:
            if c in 'lr':
                errs.append(f'T-2 表格列含左/右对齐 `{c}`（line ~{tex[:m.start()].count(chr(10))+1}），应为居中 c / C{{}}')
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
        lt = re.search(r'\\begin\{longtable\}\{([^}]*)\}(.*?)\\end\{longtable\}', block, re.S)
        if lt:
            spec = lt.group(1)
            ncols = 0
            stripped = re.sub(r'C\{[^}]*\}|p\{[^}]*\}|X|@\{\}|>.*?\{[^}]*\}', '', spec)
            ncols = len(re.findall(r'[clrCpX]', spec))  # 近似列数
            if ncols < 3:
                errs.append('T-3 符号说明应至少三列（符号|含义|单位）')
                ok = False
            body = lt.group(2)
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

    # ---- T-6 end{document} 恰一次 ----
    cnt = tex.count(r'\end{document}')
    if cnt != 1:
        errs.append(f'T-6 \\end{{document}} 出现 {cnt} 次，应为 1 次（防重复/结构错误）')
        ok = False

    # ---- T-8 模型章外层结构：允许条件性的公共数据处理，问题小节按题面顺序；
    #      内层标题按模型内容生成，不强制统一模板或检验位置 ----
    ms = re.search(r'\\section\{模型的建立与求解\}(.*?)(?=\\section\{)', tex, re.S)
    if not ms:
        errs.append('T-8 未找到 \\section{模型的建立与求解}')
        ok = False
    else:
        block = ms.group(1)
        subs = re.findall(r'\\subsection\{([^}]*)\}', block)
        if not subs:
            errs.append('T-8 模型章未找到二级标题；应按题面顺序设置问题小节')
            ok = False
        else:
            numerals = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
            found = []
            for idx, title in enumerate(subs):
                for number, numeral in enumerate(numerals, start=1):
                    if ('问题' + numeral) in title:
                        found.append((number, idx, title))
                        break
            if not found:
                errs.append('T-8 模型章未找到“问题一：任务内容”等问题二级标题')
                ok = False
            else:
                numbers = [item[0] for item in found]
                expected = list(range(1, len(numbers) + 1))
                if numbers != expected:
                    errs.append('T-8 问题二级标题未按题面连续顺序出现（实际：%s）' % ' / '.join(item[2] for item in found))
                    ok = False
                first_problem_idx = found[0][1]
                prefix = subs[:first_problem_idx]
                if len(prefix) > 1 or any(not re.search(r'数据|预处理|字段|样本', title) for title in prefix):
                    errs.append('T-8 问题一之前只允许一个公共数据处理二级标题（实际：%s）' % (' / '.join(prefix) if prefix else '无'))
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
        n_eq = body.count('=')
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
