# AGENTS.md — academic_homepage

## 项目目标

这是陈炎柯个人科研主页的重制版。保留旧站可靠的内容、INSPIRE 数据管线和每日更新能力，重做视觉设计、信息层级、响应式布局与交互。

部署仓库为 `https://github.com/YKChen-PKU/YKChen_academic_homepage`。推送、合并或其他影响远端的操作须由用户明确授权。

开始工作前阅读 `README.md`。本项目没有独立的框架目录约定以外的嵌套 AGENTS.md。

## 技术约定

- 网站位于 `site/`，使用 Astro 6 静态构建；Node.js 必须不低于 22.12。
- 样式集中在 `site/src/styles/global.css`，使用原生 CSS，不使用 Tailwind。
- 主题默认使用 Light，不读取或监听系统配色；手动选择存于 `yk-theme`。中文切换默认英文，选择存于 `yk-lang`。
- 双语短文本使用 `site/src/components/T.astro`，含公式或富文本的内容使用 `i18n-en` / `i18n-zh` 双份渲染；论文题目和报告题目不翻译，国内会议名称使用 `talks.yaml` 的 `event_zh`，已核实的 Indico 会议链接使用可选的 `url` 字段。
- 图表使用构建时生成的静态 SVG；不要为了简单样式或图表擅自引入 D3、Chart.js 等依赖。
- 数学公式由 `site/src/lib/math.ts` 在构建时通过 KaTeX 渲染。
- Python 数据管线位于 `scripts/`，本地依赖安装在 `scripts/.venv/`。
- `site/src/data/inspire.json` 是生成文件，不手工编辑；通过 `python -m scripts.fetch_inspire` 更新。
- 新论文的研究主题映射在 `site/src/data/themes.yaml` 中维护；未映射论文显示为 `untagged`。

## 内容边界

- 论文、作者、引用和指标以 INSPIRE 快照为事实来源，不在前端硬编码副本。
- 研究介绍集中在 `site/src/lib/research.ts`，报告在 `site/src/data/talks.yaml`，双语履历与奖项在 `site/src/lib/experience.ts`，CV 页面在 `site/src/pages/cv.astro`。
- 涉及物理内容的增删、主题归类、措辞变化或数据口径变化，先与用户确认，不自行补充物理判断。
- CV PDF 是完整履历的权威版本；网页摘要与 PDF 冲突时先报告，不自行猜测。
- 保留现有外部链接、可访问性标签、移动端布局与 `prefers-reduced-motion` 支持。

## 常用命令

```bash
# 数据环境（首次）
python3 -m venv scripts/.venv
scripts/.venv/bin/python -m pip install -r scripts/requirements-dev.txt

# 数据管线测试与更新
scripts/.venv/bin/python -m pytest scripts/tests
scripts/.venv/bin/python -m scripts.fetch_inspire

# 网站开发、构建和预览
cd site
npm install
npm run dev
npm run build
npm run preview
```

## 修改后的验收

1. 运行数据管线测试与 `npm run build`。
2. 若改动页面，使用浏览器实际打开本地站点，检查首页及受影响的子页面。
3. 检查桌面和移动布局；论文页需验证搜索、筛选、排序及重置，导航需验证移动菜单。
4. 检查公式、外部链接、图表数值和 INSPIRE 刷新时间，不仅依赖编译成功。
5. 清理测试或构建产生的非交付文件；保留用于部署的锁文件和提交的数据快照。

GitHub Actions 工作流位于 `.github/workflows/deploy.yml`，每日 03:00 UTC 更新数据并部署。修改目录结构、命令、数据流程或上述约定时，同步更新 README.md 和本文件。
