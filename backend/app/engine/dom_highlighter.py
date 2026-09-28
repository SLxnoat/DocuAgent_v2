"""DOM Highlight Injector and In-Page Event Interceptor."""

import json
from app.core.config import settings
from app.core.logging import logger


class DOMHighlighter:
    """Manages real-time CSS element highlighting and DOM instrumentation."""

    HIGHLIGHT_CLASS = "docuagent-active-highlight"

    @classmethod
    def get_injection_script(cls, highlight_color: str = "#ef4444") -> str:
        """Generate client-side JavaScript to track user interactions and apply visual highlight outlines."""
        return f"""
        (() => {{
            if (window.__docuagent_initialized) return;
            window.__docuagent_initialized = true;

            // 1. Inject Highlighting Styles
            const style = document.createElement('style');
            style.id = 'docuagent-highlighter-style';
            style.innerHTML = `
                .{cls.HIGHLIGHT_CLASS} {{
                    outline: {settings.PLAYWRIGHT_HIGHLIGHT_OUTLINE_WIDTH} solid {highlight_color} !important;
                    outline-offset: 2px !important;
                    box-shadow: 0 0 12px {highlight_color}88 !important;
                    transition: outline 0.15s ease-in-out !important;
                    position: relative !important;
                    z-index: 2147483640 !important;
                }}
            `;
            document.head.appendChild(style);

            let activeElement = null;

            function highlightElement(el) {{
                if (!el || el === document.body || el === document.documentElement) return;
                if (activeElement && activeElement !== el) {{
                    activeElement.classList.remove('{cls.HIGHLIGHT_CLASS}');
                }}
                activeElement = el;
                el.classList.add('{cls.HIGHLIGHT_CLASS}');
            }}

            function clearHighlight() {{
                if (activeElement) {{
                    activeElement.classList.remove('{cls.HIGHLIGHT_CLASS}');
                    activeElement = null;
                }}
            }}

            function getCssSelector(el) {{
                if (!(el instanceof Element)) return '';
                if (el.id) return `#${{el.id}}`;
                
                const parts = [];
                while (el && el.nodeType === Node.ELEMENT_NODE) {{
                    let selector = el.nodeName.toLowerCase();
                    if (el.className && typeof el.className === 'string') {{
                        const classes = el.className.trim().split(/\\s+/).filter(c => c && c !== '{cls.HIGHLIGHT_CLASS}');
                        if (classes.length > 0) {{
                            selector += '.' + classes.slice(0, 2).join('.');
                        }}
                    }}
                    let sibling = el, count = 1;
                    while (sibling = sibling.previousElementSibling) {{
                        if (sibling.nodeName.toLowerCase() === el.nodeName.toLowerCase()) count++;
                    }}
                    if (count > 1) selector += `:nth-of-type(${{count}})`;
                    parts.unshift(selector);
                    if (parts.length >= 3) break;
                    el = el.parentElement;
                }}
                return parts.join(' > ');
            }}

            function extractElementData(el) {{
                if (!el || !(el instanceof Element)) return null;
                const rect = el.getBoundingClientRect();
                return {{
                    tag_name: el.tagName.toLowerCase(),
                    element_id: el.id || null,
                    class_names: Array.from(el.classList).filter(c => c !== '{cls.HIGHLIGHT_CLASS}'),
                    css_selector: getCssSelector(el),
                    inner_text: (el.innerText || el.textContent || '').trim().substring(0, 150),
                    placeholder: el.getAttribute('placeholder') || null,
                    aria_label: el.getAttribute('aria-label') || null,
                    role: el.getAttribute('role') || null,
                    input_type: el.getAttribute('type') || null,
                    bounding_box: {{
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        top: rect.top,
                        left: rect.left,
                        bottom: rect.bottom,
                        right: rect.right
                    }},
                    attributes: {{
                        name: el.getAttribute('name') || '',
                        value: el.value || '',
                        title: el.getAttribute('title') || ''
                    }}
                }};
            }}

            // Event Listeners for DOM Activity
            document.addEventListener('pointerdown', (e) => {{
                highlightElement(e.target);
                if (window.__docuagent_on_action) {{
                    window.__docuagent_on_action({{
                        action_type: 'click',
                        target: extractElementData(e.target),
                        timestamp: new Date().toISOString()
                    }});
                }}
            }}, true);

            document.addEventListener('input', (e) => {{
                highlightElement(e.target);
                if (window.__docuagent_on_action) {{
                    window.__docuagent_on_action({{
                        action_type: 'input',
                        target: extractElementData(e.target),
                        input_value: e.target.value,
                        timestamp: new Date().toISOString()
                    }});
                }}
            }}, true);

            document.addEventListener('change', (e) => {{
                highlightElement(e.target);
                if (window.__docuagent_on_action) {{
                    window.__docuagent_on_action({{
                        action_type: 'change',
                        target: extractElementData(e.target),
                        input_value: e.target.value,
                        timestamp: new Date().toISOString()
                    }});
                }}
            }}, true);

            window.__docuagent_clear_highlight = clearHighlight;
            window.__docuagent_highlight = highlightElement;
        }})();
        """
