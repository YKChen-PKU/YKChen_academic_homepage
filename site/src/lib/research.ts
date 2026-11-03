import { bundle, type Paper } from './data';

export interface ResearchTheme {
  slug: string;
  number: string;
  title: string;
  titleZh: string;
  shortTitle: string;
  shortTitleZh: string;
  summaryTex: string;
  summaryZh: string;
  introTex: string;
  introZh: string;
  methods: string[];
  methodsZh: string[];
}

export const researchThemes: ResearchTheme[] = [
  {
    slug: 'quark_models',
    number: '01',
    title: 'Quark models',
    titleZh: '夸克模型',
    shortTitle: 'Quark models',
    shortTitleZh: '夸克模型',
    summaryTex: 'Tetraquark bound states and resonances using constituent quark models, complex scaling, and diffusion Monte Carlo — including $T_{cc}^+(3875)$, $T_{cs(0,1)}(2900)$, and fully heavy $QQ\\bar{Q}\\bar{Q}$ states.',
    summaryZh: '使用组分夸克模型、复标度方法和扩散蒙特卡洛，研究 $T_{cc}^+(3875)$、$T_{cs(0,1)}(2900)$ 以及全重 $QQ\\bar{Q}\\bar{Q}$ 态等四夸克束缚态与共振态。',
    introTex: 'Whether states like $X(6900)$, $T_{cs(0,1)}(2900)$, and $T_{cc}^+(3875)$ are compact tetraquarks or hadronic molecules can only be settled by treating both configurations on equal footing. We solve the four-body Schrödinger equation in the quark potential model — benchmarking AL1/AP1 against the Gaussian expansion method and confirming $T_{cc}^+(3875)$ — then extend the framework to resonances via the complex scaling method. A new definition of the root-mean-square radius exposes internal quark clustering, letting us cleanly distinguish compact from molecular configurations and predict new partner states awaiting experimental discovery.',
    introZh: '对于 $X(6900)$、$T_{cs(0,1)}(2900)$ 和 $T_{cc}^+(3875)$ 等态，要判断它们是紧凑四夸克态还是强子分子态，需要在同一框架中平等处理两种构型。我们在夸克势模型中求解四体薛定谔方程，利用高斯展开方法对 AL1/AP1 进行基准检验并确认 $T_{cc}^+(3875)$，再通过复标度方法将框架推广到共振态。新的均方根半径定义揭示了内部夸克团簇结构，使我们能够区分紧凑构型与分子构型，并预言有待实验发现的新伙伴态。',
    methods: ['Constituent quark models', 'Gaussian expansion', 'Complex scaling', 'Diffusion Monte Carlo'],
    methodsZh: ['组分夸克模型', '高斯展开', '复标度方法', '扩散蒙特卡洛'],
  },
  {
    slug: 'hadronic_interaction',
    number: '02',
    title: 'Hadronic interaction',
    titleZh: '强子间相互作用',
    shortTitle: 'Hadronic interaction',
    shortTitleZh: '强子间相互作用',
    summaryTex: 'Coupled-channel dynamics and pole structures for near-threshold states such as $X(3872)$ and $T_{cc}^+(3875)$, alongside virtual states and three-body molecules such as $DD^*\\bar{K}^*$.',
    summaryZh: '研究 $X(3872)$、$T_{cc}^+(3875)$ 等近阈值态的耦合道动力学与极点结构，以及虚态和 $DD^*\\bar{K}^*$ 等三体分子态。',
    introTex: 'Many exotic hadron candidates near hadron-hadron thresholds — $X(3872)$, $T_{cc}^+(3875)$ — are dominated by coupled-channel effects that obscure their pole structure. We developed an improved complex scaling method (ICSM) that reveals poles inaccessible to the conventional CSM, and applied it to track the origins of $X(3872)$ and $T_{cc}^+(3875)$. Our analysis ties the dynamical origin of $X(3872)$ to its pole width and predicts a new resonance whose discovery would settle whether the state is a $D\\bar{D}^*$ molecule or a shadow pole of a $P$-wave charmonium.',
    introZh: '许多位于强子—强子阈值附近的奇特强子候选态——$X(3872)$、$T_{cc}^+(3875)$——受到显著的耦合道效应影响，其极点结构因而难以辨认。我们发展了改进复标度方法（ICSM），能够揭示传统 CSM 无法触及的极点，并用于追踪 $X(3872)$ 和 $T_{cc}^+(3875)$ 的起源。我们的分析将 $X(3872)$ 的动力学起源与其极点宽度联系起来，并预言一个新的共振态；发现该态将有助于判断 $X(3872)$ 是 $D\\bar{D}^*$ 分子态，还是 $P$ 波粲偶素的影子极点。',
    methods: ['Coupled-channel dynamics', 'Few-body systems', 'Pole structures', 'Hadronic molecules'],
    methodsZh: ['耦合道动力学', '少体系统', '极点结构', '强子分子态'],
  },
  {
    slug: 'electromagnetic_properties',
    number: '03',
    title: 'Electromagnetic properties',
    titleZh: '电磁性质',
    shortTitle: 'Electromagnetic properties',
    shortTitleZh: '电磁性质',
    summaryTex: 'Electromagnetic properties of heavy hadrons studied in heavy-hadron χPT, with predictions for future experiments and comparisons with lattice QCD.',
    summaryZh: '利用重强子手征微扰论研究重强子的电磁性质，为未来实验及与格点 QCD 的对照提供理论预言。',
    introTex: 'Understanding how the spectrum and internal structure of hadrons emerge from QCD remains a central goal of strong-interaction physics. Hadron electromagnetic properties are sensitive to internal structure and provide valuable insights into nonperturbative QCD and confinement effects. Heavy hadrons provide a particularly instructive setting: their comparatively simple valence structure combines short-distance dynamics associated with the heavy-quark mass and nonperturbative dynamics of the light degrees of freedom. Because such measurements are experimentally challenging, these properties have received limited theoretical attention, making advance theoretical calculations especially important. We use heavy-hadron $\\chi$PT to compute electromagnetic properties of heavy hadrons, with a view toward future experiments, comparisons with lattice QCD, and tests of the validity of the chiral expansion.',
    introZh: '理解强子谱及其内部结构如何从 QCD 中涌现，仍是强相互作用物理的核心目标。强子的电磁性质对其内部结构敏感，可为非微扰 QCD 和禁闭效应提供重要信息。重强子为研究这些问题提供了特别有启发性的体系：其相对简单的价夸克结构将与重夸克质量相关的短程动力学和轻自由度对应的非微扰动力学结合起来。由于实验测量困难，这些性质尚未得到充分的理论研究，因此提前开展理论计算尤为重要。我们使用重强子 $\\chi$PT 计算重强子的电磁性质，为未来实验、与格点 QCD 的对照以及手征展开有效性的检验提供基础。',
    methods: ['Heavy-hadron χPT', 'Electromagnetic observables', 'Nonperturbative QCD', 'Lattice QCD comparisons'],
    methodsZh: ['重强子 χPT', '电磁观测量', '非微扰 QCD', '格点 QCD 对照'],
  },
  {
    slug: 'production_and_decays',
    number: '04',
    title: 'Production and decays',
    titleZh: '产生与衰变',
    shortTitle: 'Production & decays',
    shortTitleZh: '产生与衰变',
    summaryTex: 'Branching fractions in $B^-\\to D^- X_{0,1}(2900)$ and hidden-charm strange molecular states in $B$ and $B_s$ decays.',
    summaryZh: '研究 $B^-\\to D^- X_{0,1}(2900)$ 的分支比，以及 $B$ 和 $B_s$ 衰变中的隐粲奇异分子态。',
    introTex: 'Beyond mass and width, the production mechanism of an exotic state in weak decays of $B$ and $B_s$ mesons offers an independent fingerprint of its nature. We computed branching fractions for $T_{cs(0,1)}(2900)$ and $Z_{cs}$ production in $B_{(s)}$ decays using the factorization approach combined with final-state interactions and rescattering, obtaining branching fractions of order $10^{-5}$–$10^{-4}$ and ratios that depend only weakly on model parameters. These predictions are sharp enough to guide ongoing searches at Belle II and LHCb.',
    introZh: '除了质量和宽度，奇特态在 $B$ 和 $B_s$ 介子弱衰变中的产生机制也为其本质提供独立的判据。我们结合因子化方法、末态相互作用与再散射，计算 $B_{(s)}$ 衰变中 $T_{cs(0,1)}(2900)$ 和 $Z_{cs}$ 产生的分支比，得到 $10^{-5}$–$10^{-4}$ 的量级，且比值对模型参数的依赖较弱。这些预言足以为 Belle II 和 LHCb 正在开展的搜寻提供指导。',
    methods: ['Weak decays', 'Factorization', 'Final-state interactions', 'Branching fractions'],
    methodsZh: ['弱衰变', '因子化', '末态相互作用', '分支比'],
  },
];

export function papersForTheme(slug: string): Paper[] {
  const ids = new Set(bundle.themes[slug] ?? []);
  return bundle.papers.filter((paper) => ids.has(paper.arxiv_id)).sort((a, b) => b.year - a.year);
}
