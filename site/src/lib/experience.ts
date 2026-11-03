export interface Experience {
  kind: 'work' | 'education';
  dateEn: string;
  dateZh: string;
  titleEn: string;
  titleZh: string;
  organizationEn: string;
  organizationZh: string;
  detailEn: string;
  detailZh: string;
}

export const experiences: Experience[] = [
  {
    kind: 'work',
    dateEn: 'Jul 2025 — present',
    dateZh: '2025年7月 — 至今',
    titleEn: 'Postdoctoral Researcher',
    titleZh: '博士后 · 助理研究员',
    organizationEn: 'Center for High Energy Physics, Peking University',
    organizationZh: '北京大学高能物理研究中心',
    detailEn: 'Supervisor: Prof. Shi-Lin Zhu',
    detailZh: '合作导师：朱世琳教授',
  },
  {
    kind: 'education',
    dateEn: 'Sep 2020 — Jun 2025',
    dateZh: '2020年9月 — 2025年6月',
    titleEn: 'PhD in Theoretical Physics',
    titleZh: '理学博士 · 理论物理学',
    organizationEn: 'School of Physics, Peking University',
    organizationZh: '北京大学物理学院',
    detailEn: 'Advisor: Prof. Shi-Lin Zhu',
    detailZh: '导师：朱世琳教授',
  },
  {
    kind: 'education',
    dateEn: 'Sep 2016 — Jul 2020',
    dateZh: '2016年9月 — 2020年7月',
    titleEn: 'BSc in Physics',
    titleZh: '理学学士 · 物理学',
    organizationEn: 'Cuiying Honors College, Lanzhou University',
    organizationZh: '兰州大学萃英学院',
    detailEn: 'Advisor: Prof. Fu-Sheng Yu',
    detailZh: '导师：于福升教授',
  },
];

export const awards = [
  { en: 'President Scholarship', zh: '北京大学校长奖学金', dateEn: '2024', dateZh: '2024' },
  { en: 'National Scholarship', zh: '国家奖学金', dateEn: '2019', dateZh: '2019' },
  { en: 'Merit Student · Merit Student Pacesetter', zh: '三好学生标兵', dateEn: '2024', dateZh: '2024' },
  { en: 'Outstanding graduate', zh: '兰州大学优秀毕业生', dateEn: '2019', dateZh: '2019' },
];
