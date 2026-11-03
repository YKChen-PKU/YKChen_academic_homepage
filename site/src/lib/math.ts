import katex from 'katex';

export function renderInlineMath(input: string): string {
  if (!input.includes('$')) return escapeHtml(input);
  const parts: string[] = [];
  let index = 0;
  while (index < input.length) {
    const dollar = input.indexOf('$', index);
    if (dollar === -1) {
      parts.push(escapeHtml(input.slice(index)));
      break;
    }
    if (dollar > index) parts.push(escapeHtml(input.slice(index, dollar)));
    const end = input.indexOf('$', dollar + 1);
    if (end === -1) {
      parts.push(escapeHtml(input.slice(dollar)));
      break;
    }
    const tex = input.slice(dollar + 1, end);
    try {
      parts.push(katex.renderToString(tex, { throwOnError: false, output: 'html', strict: 'ignore' }));
    } catch {
      parts.push(escapeHtml(`$${tex}$`));
    }
    index = end + 1;
  }
  return parts.join('');
}

export function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
