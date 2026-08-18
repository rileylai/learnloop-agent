"""Build the deterministic offline rendered-DOM snapshot for W03."""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_HTML = """<!doctype html>
<html lang="zh-Hant" data-rendered-dom-snapshot="offline-revision-001">
<head>
  <meta charset="utf-8">
  <meta name="snapshot-mode" content="rendered-dom">
  <title>離線文章快照 / Offline Article Snapshot</title>
</head>
<body>
  <div id="app" data-rendered="true">
    <main>
      <article data-route="learning/traceability">
        <header>
          <h1>離線文章快照 / Offline Article Snapshot</h1>
          <p>這份 DOM snapshot 模擬已完成渲染的文章，不需要瀏覽器或網路。 This DOM snapshot models a rendered article without a browser or network.</p>
        </header>
        <section id="overview">
          <h2>導讀 / Overview</h2>
          <p>巢狀區段保留文章脈絡。 Nested sections preserve the article context.</p>
          <ul>
            <li>讀取固定的 rendered DOM / Read the fixed rendered DOM.</li>
            <li>保留中英文段落 / Preserve Chinese and English paragraphs.</li>
          </ul>
        </section>
        <section id="details">
          <h2>細節 / Details</h2>
          <p>下面的子區段以相同 snapshot identity 綁定表格與圖形。 Child sections bind the table and figure to one snapshot identity.</p>
          <section id="table-panel">
            <h3>資料表 / Data Table</h3>
            <table>
              <caption>表二：快照狀態 / Table 2: Snapshot states</caption>
              <thead>
                <tr><th scope="col">狀態 State</th><th scope="col">保留 Retained</th><th scope="col">備註 Note</th></tr>
              </thead>
              <tbody>
                <tr><td>Rendered / 已渲染</td><td>yes / 是</td><td>固定 DOM / Fixed DOM</td></tr>
                <tr><td>Network / 網路</td><td>no / 否</td><td>離線建置 / Offline build</td></tr>
              </tbody>
            </table>
          </section>
          <section id="figure-panel">
            <h3>關聯圖 / Relationship Figure</h3>
            <figure id="relationship-figure">
              <div role="img" aria-label="Snapshot to structure to reference">[Snapshot] → [Structure] → [Reference]</div>
              <figcaption>圖二：DOM 到 reference / Figure 2: DOM to reference.</figcaption>
            </figure>
          </section>
        </section>
        <section id="conclusion">
          <h2>結語 / Conclusion</h2>
          <p>所有內容都來自固定 bytes。 Every element comes from fixed bytes.</p>
        </section>
      </article>
    </main>
  </div>
</body>
</html>
"""


def build_html() -> bytes:
    """Return the byte-stable offline rendered-DOM snapshot."""

    return SOURCE_HTML.encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the W03 offline DOM snapshot")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("source.html"))
    args = parser.parse_args()
    args.output.write_bytes(build_html())


if __name__ == "__main__":
    main()
