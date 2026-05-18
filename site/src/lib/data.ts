import bundleJson from '../data/inspire.json';

export interface PaperAuthor {
  name: string;
  is_yk: boolean;
  inspire_id: string | null;
}

export interface JournalRef {
  name: string;
  volume: string | null;
  page: string | null;
  year: number;
}

export interface Paper {
  arxiv_id: string;
  inspire_id: string;
  title: string;
  authors: PaperAuthor[];
  year: number;
  journal_ref: JournalRef | null;
  doi: string | null;
  citation_count: number;
  arxiv_categories: string[];
  author_position: 'first' | 'middle' | 'last' | 'sole';
  theme_slug: string | null;
}

export interface AuthorProfile {
  recid: string;
  name: string;
  current_affiliation: string | null;
  orcid: string | null;
}

export interface CoauthorNode {
  name: string;
  papers_with_yk: number;
  inspire_id: string | null;
}

export interface CoauthorEdge {
  source: string;
  target: string;
  weight: number;
}

export interface CoauthorGraph {
  nodes: CoauthorNode[];
  edges: CoauthorEdge[];
}

export interface TreemapNode {
  name: string;
  value: number | null;
  children: TreemapNode[] | null;
}

export interface PaperRef {
  arxiv_id: string;
  inspire_id: string;
  title: string;
  citation_count: number;
}

export interface DerivedMetrics {
  papers_per_year: Record<string, Record<string, number>>;
  citations_per_year: Record<string, number>;
  citations_per_year_method: 'exact' | 'approximate';
  cumulative_citations: Record<string, number>;
  h_index_curve: Record<string, number>;
  author_position_total: Record<string, number>;
  top_cited: PaperRef[];
  journal_split: Record<string, number>;
  coauthor_graph: CoauthorGraph;
  treemap: TreemapNode;
}

export interface InspireBundle {
  fetched_at: string;
  author: AuthorProfile;
  papers: Paper[];
  metrics: DerivedMetrics;
  themes: Record<string, string[]>;
}

export const bundle = bundleJson as unknown as InspireBundle;

export const fetchedAt = new Date(bundle.fetched_at);

export const refreshedLabel = fetchedAt.toLocaleDateString('en-US', {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
  timeZone: 'UTC',
});
