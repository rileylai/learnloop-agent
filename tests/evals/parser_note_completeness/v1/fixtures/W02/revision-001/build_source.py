"""Build the deterministic, self-contained W02 static HTML draft fixture."""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_HTML = """<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="description" content="Project-authored bilingual static article">
  <title>可追蹤的資料流程 / Traceable Data Workflows</title>
</head>
<body>
  <header id="site-header">
    <div class="brand">LearnLoop / 學習循環</div>
    <nav aria-label="site navigation">
      <span>文章 Articles</span>
      <span>方法 Methods</span>
      <span>附錄 Appendix</span>
    </nav>
  </header>
  <main id="article">
    <article>
      <h1>可追蹤的資料流程 / Traceable Data Workflows</h1>
      <p>這篇專案自有文章說明如何讓資料處理保持可追蹤。 This project-owned article explains how to keep data processing traceable.</p>

      <section id="overview">
        <h2>摘要 / Overview</h2>
        <p>清楚的邊界讓讀者能在中英文內容之間建立同一條脈絡。 Clear boundaries preserve one context across Chinese and English content.</p>
        <ul>
          <li>保留 heading 與段落階層 / Preserve heading and paragraph hierarchy.</li>
          <li>把清單項目視為可定位的內容 / Treat list items as locatable content.</li>
          <li>讓 boilerplate 與文章主體保持可區分 / Keep boilerplate distinct from the article body.</li>
        </ul>
        <ol>
          <li>先固定 source snapshot / Freeze the source snapshot first.</li>
          <li>再建立 reference / Then author the reference.</li>
        </ol>
      </section>

      <section id="event-table">
        <h2>事件表 / Event Table</h2>
        <table>
          <caption>表一：處理事件欄位 / Table 1: Processing event fields</caption>
          <thead>
            <tr><th scope="col">欄位 Field</th><th scope="col">值 Value</th><th scope="col">說明 Note</th></tr>
          </thead>
          <tbody>
            <tr><td>Parse / 解析</td><td>18 ms</td><td>讀取結構 / Read structure</td></tr>
            <tr><td>Review / 審核</td><td>42 ms</td><td>保留脈絡 / Keep context</td></tr>
            <tr><td>Publish / 發布</td><td>75 ms</td><td>等待決策 / Await decision</td></tr>
          </tbody>
        </table>
      </section>

      <section id="code-example">
        <h2>程式片段 / Code Example</h2>
        <pre><code class="language-python">def normalize(value):
    # Keep source text stable before reference authoring.
    return value.strip()
</code></pre>
      </section>

      <section id="workflow-figure">
        <h2>流程圖 / Workflow Figure</h2>
        <figure id="workflow-diagram">
          <div role="img" aria-label="Input to normalize to review">[Input] → [Normalize] → [Review]</div>
          <figcaption>圖一：固定流程 / Figure 1: A fixed processing flow.</figcaption>
        </figure>
      </section>
    </article>
    <aside id="article-note">備註 Note：這是 development validation 草稿，不代表正式採用。</aside>
  </main>
  <footer id="site-footer">頁尾資訊 / Footer information · project-owned synthetic content</footer>
</body>
</html>
"""


def build_html() -> bytes:
    """Return the byte-stable offline HTML snapshot."""

    return SOURCE_HTML.encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the W02 static HTML fixture")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("source.html"))
    args = parser.parse_args()
    args.output.write_bytes(build_html())


if __name__ == "__main__":
    main()
