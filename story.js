/* BLACK YAK 27FW 原廠季節商品資訊（來源：BLACKYAK_27FW_Visual_Strategy_ZH.pdf，2026/11/13 中文版）
   只放商品本身的資訊：材質、規格、機能、穿搭與搭配。
   不放任何價格（含韓國售價）、銷售目標、售罄率、款數／SKU、折扣、內部時程與銷售做法。
   season = 季節商品面板；series = 各系列「商品資訊」（鍵可寫「分頁|系列」，找不到再找「系列」）。 */
window.BY_STORY = {
  season: {
    title: '27FW 季節商品資訊',
    lead: '27FW 的主軸是「輕量＋耐用」，把登山專業延伸成一整套冬季系統：從外層、保暖層到帽子、手套、鞋款，一層一層搭起來。',
    sections: [
      {
        h: '季節主題',
        note: '各款上市月以卡片上的「台灣預計 N 月上市」為準。',
        table: {
          head: ['時期', '服裝', '配件', '鞋款', '重點'],
          rows: [
            ['初秋', 'Tough Shield、Javari GTX', '背包', '—', '洋蔥式穿搭＋防護'],
            ['秋季', 'Stone Master、Javari GTX', '冬季配件 LV1／LV2', '快速健行鞋、越野跑鞋', '活動保暖'],
            ['入冬', 'Diafuse、Dyneema', '帽子、手套', 'Magnum V2、Yorkshire、LOAF', '高山保暖層'],
            ['深冬', 'Diafuse、聯名', 'LV2／LV3 保暖配件', 'YAK LOAD PRO、冬季靴', '全套寒季裝備']
          ]
        }
      },
      {
        h: '服裝系列',
        cards: [
          { t: 'DNS：Javari GTX＋Dyneema', b: ['一整套洋蔥式系列，從外殼、保暖層、厚羽絨到登山滑雪用途串成一套。', '外層／防護：Javari GTX 四季硬殼外套。', '保暖層：Thulagi、Langar、Kangayam，依活動強度設計。', '厚羽絨／高山：源自遠征規格的羽絨，為高山打造的保暖。'] },
          { t: 'Tough Shield', b: ['從長褲系列擴大成整套穿搭：外層、中層、內層互相搭配。', '立體剪裁、耐用布料。', '可搭 Javari GTX 外套與 EXUM GTX 快速健行鞋。'] },
          { t: 'Stone Master', b: ['攀岩出身的保暖系列，訴求輕、暖，也適合冬季日常穿。', '原廠材質方向：10D 布料搭配石墨烯相關材質。', '有女款專屬版型。'] },
          { t: 'Diafuse（Diamond Fuse 保暖系列）', b: ['Pertex Diamond Fuse 表布、撥水羽絨，加上立體隔牆的羽絨格室結構。', '分三個等級：Summit、Alpine、Active，依高山程度選。'] },
          { t: 'Hima & Alaya', b: ['消費者熟悉的冬季羽絨版型。', '這季保留經典設計，修正版型與細節。'] },
          { t: '越野跑', b: ['冬季款 AIR-VENT 管狀羽絨：透氣、好活動、保暖適中。', '寒冷天跑步用，可搭 SKY WEB 鞋款與越野背負裝備。'] }
        ]
      },
      {
        h: '背包',
        cards: [
          { t: '背包系列', b: ['YAK HORN：經典登山包系列，這季翻新。', 'DNS UL：技術型背負，結構依用途設計。', 'MODULE PACK：外掛系統，可依需要擴充。', 'DUFFLE：旅行包型，帶有 BLACK YAK 識別。', '常用容量以 25–35L 為主。'] }
        ]
      },
      {
        h: '冬季配件：保暖分級',
        note: '等級是原廠商品分類，用來說明保暖度與用途，不是 ISO 23537 認證。',
        table: {
          head: ['等級', '適用', '特性'],
          rows: [
            ['LV1 輕量', '涼爽天氣的活動', '輕盈手感、排汗'],
            ['LV2 中等', '一般冬季天氣', '保暖＋多用途、防風'],
            ['LV3 厚重', '寒冷的山上', '包覆＋保暖、可搭配多層穿']
          ]
        }
      },
      {
        h: '帽子與手套',
        cards: [
          { t: '帽子', b: ['季節配色，依保暖程度分級。', '依活動與穿搭層次挑：輕量款活動用，厚款寒冷天用。'] },
          { t: '手套', b: ['輕量／日常：輕薄好活動。', '防風／活動保暖：擋風、健行與活動用。', '寒冷／多層搭配：厚保暖，可搭內層手套。'] }
        ]
      },
      {
        h: '鞋款',
        cards: [
          { t: '登山健行鞋', b: ['YAK LOAD PRO：高階登山鞋，重新打造，加強腳踝保護與山徑穩定性。', 'PALADIN GTX：經典登山鞋設計，GORE-TEX 防水。', 'APPROACH：兼顧山徑抓地與日常穿著。', 'MAGNUM V2：主力經典款。'] },
          { t: '快速健行', b: ['EXUM GTX：Vibram 大底、Y-FRAME 支撐、CORDURA 鞋面，適合快速健行。', '配色和 Javari GTX、Tough Shield 服裝同步，可成套穿。', '343 系列：BOA 旋鈕＋GORE-TEX。'] },
          { t: '越野跑鞋', b: ['TRAIL-X 02 GTX：BOA、Vibram、GORE-TEX，什麼天氣都能跑越野。', 'SKY WEB：路跑到越野都能穿，舒適好上手。', 'SKY ARROW：性能旗艦款。'] },
          { t: '基本款與冬季款', b: ['YORKSHIRE（The First、Classic）：經典外型。', 'LOAF：好穿脫，戶外到日常都適合。', 'LOAF MOC：冬季保暖舒適款。', 'ALASKA：寒季機能靴，搭整條冬季商品線。'] }
        ]
      },
      {
        h: '原廠建議搭配',
        table: {
          head: ['情境', '服裝', '配件', '鞋款'],
          rows: [
            ['秋季健行', 'Javari GTX＋Tough Shield', '經典登山包', 'EXUM GTX'],
            ['冬季活動', 'Stone Master', 'LV2 配件、冬季帽款', 'LOAF'],
            ['寒冷高山', 'Diafuse／Dyneema', 'LV3 配件、保暖手套', 'YAK LOAD PRO']
          ]
        }
      }
    ],
    foot: '以上整理自原廠 27FW 商品簡報。可下單款式、顏色、尺寸與台灣建議售價，以本頁商品卡片為準。'
  },
  series: {
    'ALPINE A': {
      gist: '秋冬登山與日常的基本層次：排汗層、刷毛中層、輕量保暖外層。',
      lines: [
        '27FW 主軸是把登山穿搭做成整套冬季系統，一層一層疊。',
        '可搭 Tough Shield 長褲、冬季帽款與手套。'
      ]
    },
    'ALPINE B': {
      gist: '冬季羽絨與保暖中層，含 Hima、Alaya 經典版型。',
      lines: [
        'Hima & Alaya 是消費者熟悉的冬季羽絨版型，這季保留經典設計、修正版型與細節。',
        '寒冷天可搭 LV2／LV3 帽子、手套。'
      ]
    },
    'TOUGH SHIELD': {
      gist: '從長褲擴大成整套：外層、中層、內層互相搭配。',
      lines: [
        '立體剪裁、耐用布料。',
        '原廠秋季健行搭配：Tough Shield＋Javari GTX，加 EXUM GTX 快速健行鞋與經典登山包。'
      ]
    },
    '攀岩': {
      gist: 'Stone Master：攀岩出身，輕、暖，也適合冬季日常。',
      lines: [
        '原廠材質方向：10D 布料搭配石墨烯相關材質，有女款專屬版型。',
        '原廠冬季活動搭配：Stone Master＋LV2 配件，加 LOAF 鞋款與冬季帽款。'
      ]
    },
    '越野跑': {
      gist: '冬季跑步：透氣、好活動、保暖適中。',
      lines: [
        '冬季主打 AIR-VENT 管狀羽絨。',
        '可搭 SKY WEB 越野鞋與越野背負裝備。'
      ]
    },
    'DNS 頂規線': {
      gist: '完整洋蔥式系列：外層防護、保暖層、厚羽絨。',
      lines: [
        '外層／防護：GORE-TEX 硬殼外套（Javari GTX 為四季硬殼）。',
        '保暖層：依活動強度設計（Thulagi、Langar、Kangayam）。',
        '厚羽絨／高山：源自遠征規格的羽絨，Dyneema 羽絨也在這條線。',
        '原廠寒冷高山搭配：Diafuse／Dyneema＋LV3 配件，加 YAK LOAD PRO 與保暖手套。'
      ]
    },
    '背包／包款': {
      gist: '經典、技術、模組三種用途。',
      lines: [
        'YAK HORN：經典登山包系列，這季翻新。',
        'DNS UL：技術型背負，結構依用途設計。',
        '模組背包：外掛系統，可依需要擴充。'
      ]
    },
    '帽子': {
      gist: '季節配色，依保暖程度分 LV1／LV2／LV3。',
      lines: [
        'LV1 輕量：涼爽天氣活動，輕盈、排汗。',
        'LV2 中等：一般冬季天氣，保暖、防風、多用途。',
        'LV3 厚重：寒冷的山上，包覆保暖，可多層搭配。',
        '等級是原廠商品分類，不是 ISO 23537 認證。'
      ]
    },
    '手套': {
      gist: '三種用途：輕量日常、防風活動、寒冷多層。',
      lines: [
        '輕量／日常：輕薄好活動。',
        '防風／活動保暖：擋風，健行與活動用。',
        '寒冷／多層搭配：厚保暖，可搭內層手套。',
        '等級是原廠商品分類，不是 ISO 23537 認證。'
      ]
    },
    '頸圍／頭帶': {
      gist: '冬季保暖配件，依保暖程度搭配服裝。',
      lines: [
        'LV1 輕量排汗，LV2 保暖防風，LV3 包覆保暖。',
        '可和同材質的帽子、手套成套。'
      ]
    },
    '襪子／綁腿': {
      gist: '冬季健行的腳部保暖與防護。',
      lines: [
        '搭配登山健行鞋與冬季靴，組成完整冬季裝備。'
      ]
    },
    '健行鞋': {
      gist: '快速健行：EXUM GTX 為核心。',
      lines: [
        'EXUM GTX：Vibram 大底、Y-FRAME 支撐、CORDURA 鞋面。',
        '配色和 Javari GTX、Tough Shield 服裝同步，可成套穿。',
        '343 系列：BOA 旋鈕＋GORE-TEX。'
      ]
    },
    '越野跑鞋': {
      gist: '依地形、緩震與用途分級。',
      lines: [
        'TRAIL-X 02 GTX：BOA、Vibram、GORE-TEX，全天候越野。',
        'SKY WEB：路跑到越野都能穿，舒適好上手。',
        'SKY ARROW：性能旗艦款。'
      ]
    },
    '休閒／保暖鞋': {
      gist: '日常經典、好穿脫、寒季保暖分開。',
      lines: [
        'LOAF：好穿脫，戶外到日常都適合；LOAF MOC 是冬季保暖舒適款。',
        'YORKSHIRE：經典外型。',
        'ALASKA：寒季機能靴。'
      ]
    }
  }
};
