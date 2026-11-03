export function completeYears<T>(record: Record<string, T>, empty: T): Array<{ year: number; value: T }> {
  const years = Object.keys(record).map(Number);
  const min = Math.min(...years);
  const max = Math.max(...years);
  return Array.from({ length: max - min + 1 }, (_, index) => {
    const year = min + index;
    return { year, value: record[String(year)] ?? empty };
  });
}

export function ticksFor(max: number, count = 4): number[] {
  const upper = Math.max(max, 1);
  return Array.from({ length: count + 1 }, (_, index) => Math.round((upper * index) / count));
}
