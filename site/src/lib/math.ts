import katex from 'katex';

/**
 * Render a string that may contain $...$ inline-math segments to HTML.
 * Unbalanced dollars are treated as literal characters.
 *
 * Math segments are rendered server-side with KaTeX (output: 'html').
 * Non-math text is HTML-escaped.
 */
export function renderInlineMath(input: string): string {
  if (!input.includes('$')) return escapeHtml(input);
  const parts: string[] = [];
  let i = 0;
  while (i < input.length) {
    const dollar = input.indexOf('$', i);
    if (dollar === -1) {
      parts.push(escapeHtml(input.slice(i)));
      break;
    }
    if (dollar > i) parts.push(escapeHtml(input.slice(i, dollar)));
    const end = input.indexOf('$', dollar + 1);
    if (end === -1) {
      parts.push(escapeHtml(input.slice(dollar)));
      break;
    }
    const tex = input.slice(dollar + 1, end);
    try {
      parts.push(
        katex.renderToString(tex, {
          throwOnError: false,
          output: 'html',
          strict: 'ignore',
        }),
      );
    } catch {
      parts.push(escapeHtml(`$${tex}$`));
    }
    i = end + 1;
  }
  return parts.join('');
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
