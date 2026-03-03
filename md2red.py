
import sys
import os
import argparse
import time
import json
import dataclasses
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path

# Try to import playwright, if not available this script won't work.
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright is not installed. Please install it using 'pip install playwright' and then run 'playwright install chromium'.")
    sys.exit(1)

import markdown
from markdown.extensions import fenced_code, tables

# ============================================
# Style Definitions (Copied from RedBookCards)
# ============================================

@dataclasses.dataclass
class ThemeConfig:
    """Theme Configuration"""
    name: str
    primary_color: str
    secondary_color: str
    text_color: str
    background: str
    font_family: str
    heading_font: str
    code_font: str
    accent_color: str = ""
    link_color: str = ""

class StyleManager:
    """Style Manager for generating CSS"""
    
    THEMES = {
        "xiaohongshu": ThemeConfig(
            name="RedBook Classic",
            primary_color="#FF2442",
            secondary_color="#FF6B6B",
            text_color="#2c3e50",
            background="linear-gradient(135deg, #ffeef8 0%, #ffe0f0 100%)",
            font_family='-apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", sans-serif',
            heading_font='"PingFang SC", "Helvetica Neue", sans-serif',
            code_font='"JetBrains Mono", "Cascadia Code", "Consolas", monospace',
            accent_color="#FFB6C1",
            link_color="#FF69B4"
        ),
        "dark_mode": ThemeConfig(
            name="Dark Mode",
            primary_color="#00E0FF",
            secondary_color="#0096FF",
            text_color="#E0E6ED",
            background="linear-gradient(135deg, #0F0F1E 0%, #1A1A2E 50%, #16213E 100%)",
            font_family='"Inter", "PingFang SC", "Microsoft YaHei", "Apple Color Emoji", "Segoe UI Emoji", sans-serif',
            heading_font='"Inter", "PingFang SC", sans-serif',
            code_font='"Fira Code", "JetBrains Mono", monospace',
            accent_color="#00F0FF",
            link_color="#00B8D4"
        ),
        "notion": ThemeConfig(
            name="Notion Minimal",
            primary_color="#000000",
            secondary_color="#000000",
            text_color="#000000",
            background="#F9F8F4",
            font_family='"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Apple Color Emoji", sans-serif',
            heading_font='"Inter", -apple-system, sans-serif',
            code_font='"SFMono-Regular", "Consolas", "Liberation Mono", monospace',
            accent_color="#EB5757",
            link_color="#0070F3"
        ),
        "wechat": ThemeConfig(
            name="WeChat Simple",
            primary_color="#07C160",
            secondary_color="#4CAF50",
            text_color="#353535",
            background="linear-gradient(180deg, #F7F7F7 0%, #FFFFFF 100%)",
            font_family='"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Apple Color Emoji", sans-serif',
            heading_font='"PingFang SC", "Microsoft YaHei", sans-serif',
            code_font='"SF Mono", "Monaco", "Inconsolata", monospace',
            accent_color="#95EC69",
            link_color="#576B95"
        ),
        "claude": ThemeConfig(
            name="Claude",
            primary_color="#000000",
            secondary_color="#000000",
            text_color="#000000",
            background="linear-gradient(135deg, #FEF3E2 0%, #FDE8CD 50%, #FCE0B8 100%)",
            font_family='"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Apple Color Emoji", sans-serif',
            heading_font='"Inter", -apple-system, sans-serif',
            code_font='"JetBrains Mono", "Cascadia Code", "Consolas", monospace',
            accent_color="#F59E0B",
            link_color="#B45309"
        ),
        "red_premium": ThemeConfig(
            name="RED Premium",
            primary_color="#C84B31",
            secondary_color="#1A1A1A",
            text_color="#1A1A1A",
            background="linear-gradient(180deg, #FFFAF5 0%, #FFF5ED 100%)",
            font_family='"PingFang SC", -apple-system, BlinkMacSystemFont, "Helvetica Neue", "Microsoft YaHei", "Apple Color Emoji", "Segoe UI Emoji", sans-serif',
            heading_font='"PingFang SC", "Helvetica Neue", sans-serif',
            code_font='"JetBrains Mono", "Cascadia Code", monospace',
            accent_color="#D4A574",
            link_color="#C84B31"
        ),
        "reliable": ThemeConfig(
            name="Reliable",
            primary_color="#1B3A5C",
            secondary_color="#1B3A5C",
            text_color="#1A1A1A",
            background="#FFFFFF",
            font_family='"PingFang SC", -apple-system, BlinkMacSystemFont, "Helvetica Neue", "Microsoft YaHei", "Apple Color Emoji", sans-serif',
            heading_font='"PingFang SC", "Helvetica Neue", sans-serif',
            code_font='"JetBrains Mono", "Cascadia Code", monospace',
            accent_color="#3D6A99",
            link_color="#1B3A5C"
        ),
        "million_dollar": ThemeConfig(
            name="Million Dollar",
            primary_color="#FFD700",
            secondary_color="#FFA500",
            text_color="#FFFFFF",
            background="radial-gradient(circle at center, #1a1a1a 0%, #000000 100%)",
            font_family='"Inter", "PingFang SC", "Hiragino Sans GB", sans-serif',
            heading_font='"Inter", "PingFang SC", sans-serif',
            code_font='"JetBrains Mono", monospace',
            accent_color="#FF4500",
            link_color="#FFD700"
        )
    }

    def __init__(self, theme_name: str = "xiaohongshu"):
        self.current_theme = theme_name

    def get_theme(self, theme_name: str = None) -> ThemeConfig:
        if theme_name is None:
            theme_name = self.current_theme
        return self.THEMES.get(theme_name, self.THEMES["xiaohongshu"])
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        # handle shorthand
        if len(hex_color) == 3:
            hex_color = "".join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def add_alpha(self, hex_color: str, alpha: float) -> str:
        try:
            r, g, b = self.hex_to_rgb(hex_color)
            return f"rgba({r}, {g}, {b}, {alpha})"
        except ValueError:
            return hex_color

    def generate_css(self, theme_name: str = None, font_size: int = 42) -> str: # Increased base font size for better reading
        theme = self.get_theme(theme_name)
        is_dark = theme_name in ["dark_mode", "midnight", "douyin", "million_dollar"]
        
        # Theme-specific adjustments
        if theme_name == "million_dollar":
            typography_styles = """
        h1 {
            font-size: 2.8em;
            margin-bottom: 0.8em;
            line-height: 1.1;
            background: linear-gradient(135deg, #FFF, #FFD700);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            letter-spacing: -1px;
            text-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }
        
        h2 {
            font-size: 1.8em;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
            color: var(--primary-color);
            text-transform: uppercase;
            letter-spacing: 2px;
            display: flex;
            align-items: center;
        }

        p { margin-bottom: 1.2em; text-align: left; line-height: 1.8; color: rgba(255,255,255,0.9); font-weight: 400; }
        
        strong { color: var(--primary-color); font-weight: 900; text-decoration: underline; text-decoration-color: rgba(255,215,0,0.5); }
        
        blockquote {
            border: 1px solid rgba(255,215,0,0.3);
            background: rgba(255,215,0,0.05);
            padding: 30px;
            margin: 2em 0;
            border-radius: 20px;
            font-style: italic;
            position: relative;
        }
        
        blockquote::before {
            content: "“";
            position: absolute;
            top: -20px;
            left: 20px;
            font-size: 80px;
            color: var(--primary-color);
            opacity: 0.5;
        }
            """
        else:
            typography_styles = f"""
        h1 {{
            font-size: 2.8em;
            margin-bottom: 0.8em;
            line-height: 1.1;
            color: var(--primary-color);
            font-weight: 800;
        }}
        
        h2 {{
            font-size: 1.8em;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
            color: var(--secondary-color);
            font-weight: 700;
            display: flex;
            align-items: center;
        }}

        p {{ margin-bottom: 1.2em; text-align: left; line-height: 1.8; color: var(--text-color); font-weight: 400; }}
        
        strong {{ color: var(--primary-color); font-weight: 700; }}
        
        blockquote {{
            border-left: 4px solid var(--primary-color);
            background: {self.add_alpha(theme.primary_color, 0.05)};
            padding: 20px 30px;
            margin: 2em 0;
            border-radius: 0 12px 12px 0;
            font-style: italic;
            color: var(--text-color);
            position: relative;
        }}
            """

        return f"""
        :root {{
            --primary-color: {theme.primary_color};
            --secondary-color: {theme.secondary_color};
            --accent-color: {theme.accent_color or theme.secondary_color};
            --text-color: {theme.text_color};
            --font-family: {theme.font_family};
            --heading-font: {theme.heading_font};
            --code-font: {theme.code_font};
            --base-font-size: {font_size}px;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: var(--font-family);
            background: {theme.background};
            color: var(--text-color);
            font-size: var(--base-font-size);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            overflow: hidden; /* Important for snapshotting */
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
        }}

        /* Container for the Card */
        .card-container {{
            width: 100%;
            height: 100%;
            position: relative;
        }}

        .card {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }}
        
        /* Decorative elements */

        .card-content {{
            flex: 1;
            padding: 30px 40px;
            overflow: hidden;
            position: relative;
        }}

        /* Typography */
        {typography_styles}

        code {{
            background: {self.add_alpha(theme.primary_color, 0.1)};
            padding: 2px 6px;
            border-radius: 4px;
            font-family: var(--code-font);
            font-size: 0.9em;
            color: var(--primary-color);
        }}

        pre {{
            background: #282c34;
            color: #abb2bf;
            padding: 24px;
            border-radius: 12px;
            overflow-x: auto;
            margin: 1.5em 0;
            font-family: var(--code-font);
        }}
        
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}

        img {{
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            margin: 1em 0;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }}


        /* Hidden pages */
        .page-container {{ display: none; }}
        .page-container.active {{ display: block; }}
        """

# ============================================
# Markdown to HTML Logic
# ============================================

class HtmlGenerator:
    def __init__(self, theme: str = "notion"):
        self.style_manager = StyleManager(theme)
        self.theme_name = theme

    def generate_html_template(self, raw_html: str) -> str:
        css = self.style_manager.generate_css(self.theme_name)
        
        # JS Logic for layout
        js_content = """
                function layoutPages() {
                    const _logs = [];
                    function log(msg) {
                        try {
                            if (typeof msg === 'object') msg = JSON.stringify(msg);
                            _logs.push(String(msg));
                        } catch(e) {}
                    }
                    
                    try {
                        log("Starting layout...");
                        const source = document.getElementById('source-content');
                        const target = document.getElementById('render-target');
                        
                        if (!source || !target) {
                            throw new Error("Source or Target element not found");
                        }
                        
                        // Clear target to ensure no ghosts
                        target.innerHTML = '';
                        
                        const elements = Array.from(source.children);
                        log(`Found ${elements.length} elements to layout.`);
                        
                        let pages = [];
                        // Create first page container
                        let currentPageDiv = document.createElement('div');
                        currentPageDiv.className = 'page-container active'; 
                        target.appendChild(currentPageDiv);
                        pages.push(currentPageDiv);
                        
                        // Force a layout check
                        log(`Target: ClientHeight=${target.clientHeight}, ScrollHeight=${target.scrollHeight}`);

                        // Helper to check overflow
                        function isOverflowing() {
                             // We compare the total scrollHeight of the target content area 
                             // vs its clientHeight (fixed by container).
                             return target.scrollHeight > target.clientHeight;
                        }

                        for (let i = 0; i < elements.length; i++) {
                            let el = elements[i];
                            let clone = el.cloneNode(true);
                            currentPageDiv.appendChild(clone);

                            if (isOverflowing()) {
                                log(`Overflow at Element ${i} (${el.tagName}). ScH=${target.scrollHeight} > ClH=${target.clientHeight}`);
                                
                                // Check if this is the ONLY element in the current page
                                if (currentPageDiv.children.length === 1) {
                                    log("Element too big for single page, keeping it.");
                                    // Just let it be clipped
                                } else {
                                    // Remove element from this page
                                    currentPageDiv.removeChild(clone);
                                    
                                    // Hide the full page
                                    currentPageDiv.className = 'page-container';
                                    
                                    // Create new page
                                    currentPageDiv = document.createElement('div');
                                    currentPageDiv.className = 'page-container active';
                                    target.appendChild(currentPageDiv);
                                    pages.push(currentPageDiv);
                                    
                                    // Add to new page
                                    currentPageDiv.appendChild(clone);
                                    log(`Moved Element ${i} to Page ${pages.length}`);
                                }
                            }
                        }
                        
                        // Reset to show first page
                        if (pages.length > 0) {
                            pages.forEach(p => p.className = 'page-container');
                            pages[0].className = 'page-container active';
                        }
                        
                        log(`Layout complete. Total Pages: ${pages.length}`);
                        
                        var pageTotal = document.getElementById('page-total');
                        if (pageTotal) pageTotal.innerText = pages.length;
                        
                        return JSON.stringify({ count: pages.length, logs: _logs });
                        
                    } catch (e) {
                         _logs.push("ERROR: " + e.toString());
                         return JSON.stringify({ count: 1, logs: _logs, error: e.toString() });
                    }
                }

                function getPageContentHeight() {
                    var activePage = document.querySelector('.page-container.active');
                    if (!activePage) return window.innerHeight;
                    var children = activePage.children;
                    if (children.length === 0) return window.innerHeight;
                    var lastChild = children[children.length - 1];
                    var lastRect = lastChild.getBoundingClientRect();
                    // Add bottom padding to match visual balance
                    return Math.ceil(lastRect.bottom) + 30;
                }

                function showPage(pageIndex) {
                    try {
                        const pages = document.querySelectorAll('.page-container');
                        if (pages.length === 0) return;
                        pages.forEach((p, i) => {
                            if (i === pageIndex) {
                                p.className = 'page-container active';
                                p.style.display = 'block'; // Force visible
                            } else {
                                p.className = 'page-container';
                                p.style.display = 'none'; // Force hidden
                            }
                        });
                        var pageCurrent = document.getElementById('page-current');
                        if (pageCurrent) pageCurrent.innerText = pageIndex + 1;
                        
                        // We use a global variable to track when paint is complete
                        window._paintedPage = -1;
                        requestAnimationFrame(() => {
                            // First rAF: executes before the browser repaints the layout changes
                            requestAnimationFrame(() => {
                                // Second rAF: executes after the browser has finished painting
                                window._paintedPage = pageIndex;
                            });
                        });
                        
                        return "OK"; 
                    } catch(e) {
                         return "Error: " + e.toString();
                    }
                }
        """

        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <style>{css}</style>
        </head>
        <body>
            <div id="source-content" style="display:none;">
                {raw_html}
            </div>

            <div class="card-container">
                <div class="card">
                    <div id="render-target" class="card-content">
                        <!-- Content will be injected here by JS -->
                    </div>
                </div>
            </div>

            <script>
            {js_content}
            </script>
        </body>
        </html>
        """

# ============================================
# Rendering Logic (Playwright)
# ============================================

class PlaywrightRenderer:
    def __init__(self, width: int = 1080, height: int = 1440):
        self.width = width
        self.height = height
        
    def render(self, html_content: str, output_dir: Path):
        # Ensure output directory exists
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            
        # Playwright provides purely sequential, non-flaky execution
        with sync_playwright() as p:
            # Launch hidden chromium instance
            browser = p.chromium.launch(headless=True)
            # Enforce 3:4 aspect ratio for viewport
            viewport_height = int(self.width * 4 / 3)
            page = browser.new_page(
                viewport={"width": self.width, "height": viewport_height},
                device_scale_factor=1  # 1:1 exact pixel rendering
            )
            
            # Synchronously wait for entire DOM and resources to load
            page.set_content(html_content, wait_until="networkidle")
            
            # Execute JS sequentially and wait for the returned value
            layout_result = page.evaluate("layoutPages();")
            
            try:
                if isinstance(layout_result, str):
                    data = json.loads(layout_result)
                else:
                    data = layout_result
                page_count = int(data.get('count', 1))
            except Exception as e:
                print(f"Error parsing layout res: {e}")
                page_count = 1
                
            print(f"Generating {page_count} pages...")

            # Enforce 3:4 aspect ratio
            clip_height = int(self.width * 4 / 3)
            print(f"Uniform page height: {clip_height}px (3:4 aspect ratio)")

            # Second pass: screenshot each page at the uniform height
            for i in range(page_count):
                print(f"Rendering Page {i+1}/{page_count}...")

                page.evaluate(f'''() => {{
                    return new Promise((resolve) => {{
                        showPage({i});
                        requestAnimationFrame(() => {{
                            requestAnimationFrame(resolve);
                        }});
                    }});
                }}''')

                outfile = output_dir / f"{i+1}.png"
                page.screenshot(
                    path=str(outfile),
                    clip={"x": 0, "y": 0, "width": self.width, "height": clip_height}
                )
                print(f"Saved: {outfile}")
                
            browser.close()
            
    def cleanup(self):
        # No residual cleanup needed for context managers
        pass


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Social Media Cards (RedBook Style)")
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("--theme", default="claude", help="Theme name (xiaohongshu, dark_mode, wechat, notion, claude, red_premium, reliable, million_dollar)")
    parser.add_argument("--output", help="Output title/folder name (default: input filename stem)")
    parser.add_argument("--width", type=int, default=1080, help="Image width (default: 1080)")
    parser.add_argument("--height", type=int, default=1440, help="Image height (default: 1440)")

    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File {input_path} not found.")
        sys.exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert MD to HTML
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])
    html_body = md.convert(md_text)
    
    print(f"DEBUG: Markdown text length: {len(md_text)}")
    print(f"DEBUG: HTML body length: {len(html_body)}")
    print(f"DEBUG: HTML body snippet: {html_body[:200]}")
    
    # Generate Full HTML
    generator = HtmlGenerator(args.theme)
    full_html = generator.generate_html_template(html_body)
    
    # Determine Output Directory
    # Rule: output/<title>/<pagenumber>.png
    if args.output:
        title_folder = args.output
    else:
        title_folder = input_path.stem
        
    output_dir = Path("output") / title_folder

    renderer = PlaywrightRenderer(width=args.width, height=args.height)
    try:
        renderer.render(full_html, output_dir)
    finally:
        renderer.cleanup()

    print("Done!")

if __name__ == "__main__":
    main()
