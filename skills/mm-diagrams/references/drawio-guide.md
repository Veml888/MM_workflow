# Draw.io 可编辑源指南

仅在用户要求 draw.io 可编辑源时生成 `.drawio`。最终论文仍交付矢量 PDF 与 600 DPI PNG；若 draw.io 是唯一编辑源，可同时导出 SVG 作为兼容文件，但不得替代 PDF 嵌入检查。

- 先确定最终单栏或通栏物理宽度，再保证节点文字最终为 8.5~10 pt、边标签不低于 8 pt；不要直接把编辑器字号当成论文字号。
- 白底、细边、最多一种低饱和强调色；不用阴影、渐变、装饰图标、彩色卡片阵列和大面积底板。
- 画布内不重复论文图题或宣传式副标题，图题交给 LaTeX `caption`。
- 输入、处理、模型和输出统一使用矩形，依靠层级、分区标题、节点文字和箭头关系区分；起止/状态才使用圆角矩形，真正的判断才使用菱形，不使用平行四边形。
- 主流程用实线；反馈、假设和约束用虚线并标注。
- 使用正交边，避免交叉；反馈沿外围返回。

节点样式至少显式包含 `whiteSpace=wrap;html=1;fontFamily=Microsoft YaHei;fillColor=#ffffff;strokeColor=#3f444a;shadow=0;gradientColor=none;`，字号按最终物理宽度计算。

若没有 draw.io CLI，保留 `.drawio`，并用 TikZ 复现等价 PDF/PNG；不要因缺少 CLI 省略最终图。
