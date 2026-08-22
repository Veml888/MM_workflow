# 跨页续表排版规范

本规范用于正文或附录中确实无法在单页完整容纳的长表。机制依据 LaTeX 官方 `longtable` 手册与 `booktabs` 手册：

- `longtable`：https://ctan.org/pkg/longtable
- `booktabs`：https://ctan.org/pkg/booktabs

## 1. 适用边界

- 单页能够容纳的表格继续使用 `table` + `tabular`/`tabularx`，默认 `[htbp]`；不得为了展示续表形式主动拆页。
- 只有表格在保持五号表内文字、可读列宽和合理行距后仍无法单页容纳时，才使用 `longtable`。`longtable` 本身不是浮动体，不得再包在 `table` 环境中，也不使用 `[H]`。
- 跨页只允许发生在数据行之间，不拆开同一逻辑数据行。整张续表必须在同一小节内结束，下一小节标题不得插入表格中间。

## 2. 续页格式

1. 首页使用正常表号和完整表题，只设置一个 `\label`。
2. 每个续页顶部标注“续表 N　原表题”，沿用原表编号，不增加新编号，不重复写入表目录。
3. 每个续页完整重复列标题；若表头包含单位行、分组表头或必要注释，这些内容一并重复。
4. 每个非末页底部右侧标注“续下页”；末页不显示“续下页”。
5. 中间页不得使用最终底线；只在末页使用 `\bottomrule`。续页顶部重新使用 `\toprule` 和表头后的 `\midrule`，保持三线表结构，不使用竖线或双横线。
6. 表题与普通表一致使用小四号，表内文字保持五号；表头、文字和数字继续水平居中，长文本使用居中的定宽列换行。

## 3. LaTeX 模板

将 `N` 替换为实际列数，并把两处“原表题”和列标题保持一致：

```latex
{\zihao{5}
\setlength{\LTcapwidth}{\textwidth}
\begin{longtable}{L{0.18\textwidth} L{0.18\textwidth} L{0.54\textwidth}}
  \caption{原表题\label{tab:example}}\\
  \toprule
  列一 & 列二 & 列三 \\
  \midrule
  \endfirsthead

  \multicolumn{3}{c}{\zihao{-4}续表~\thetable\quad 原表题}\\
  \toprule
  列一 & 列二 & 列三 \\
  \midrule
  \endhead

  \midrule
  \multicolumn{3}{r}{续下页}\\
  \endfoot

  \bottomrule
  \endlastfoot

  % 数据行
\end{longtable}
}
```

## 4. 编译与验收

- 至少双遍编译；若日志仍提示 longtable 列宽改变或要求重跑，继续编译直至列宽和交叉引用稳定。
- 逐页检查首页、每个中间页和末页：续表号、原表题、重复表头、单位、续下页提示、末页底线均须正确。
- 检查续页首行与前页末行连续，无漏行、重行、空白续页、单独表题页或下一小节标题插入表内。
- 正文首次引用仍只指向原表号；续页不建立第二个标签，也不作为新表计数。
