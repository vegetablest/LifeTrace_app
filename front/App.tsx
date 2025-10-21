import { useState, useEffect, useRef } from "react";
import { SearchHeader } from "./components/SearchHeader";
import { SearchTabs } from "./components/SearchTabs";
import { SearchResults } from "./components/SearchResults";
import { DetailPanel } from "./components/DetailPanel";
import { Settings } from "./components/Settings";
import { apiClient } from "./services/api";
import { transformScreenshotToResultItem, transformSemanticSearchResult, ResultItem, transformEventToResultItem } from "./utils/dataTransform";

type FocusArea = 'search' | 'tabs' | 'results' | 'details';
type DetailFocusArea = 'content' | 'actions';
type Theme = 'light' | 'dark';

// 常量配置
const TABS = [
  { id: "all", label: "全部" },
  { id: "apps", label: "应用" },
  { id: "docs", label: "文档" },
  { id: "timemachine", label: "时光机" },
];

const TAB_TO_CATEGORY = {
  apps: "应用",
  docs: "文档",
  timemachine: "时光机"
} as const;

const FOCUS_AREAS: FocusArea[] = ['search', 'tabs', 'results', 'details'];
const ACTION_COUNT = 3;
const ACTIONS = ['打开', '以管理员身份运行', '打开文件位置'];

// 模拟数据
const MOCK_RESULTS = [
  {
    id: "onenote-win10",
    title: "OneNote for Windows 10",
    subtitle: "应用",
    category: "应用",
    icon: "📓"
  },
  {
    id: "nvidia-control",
    title: "NVIDIA Control Panel",
    category: "应用",
    icon: "🎮"
  },
  {
    id: "onenote",
    title: "OneNote",
    category: "应用",
    icon: "📓"
  },
  {
    id: "notepad",
    title: "记事本",
    category: "应用",
    icon: "📝"
  },
  {
    id: "notepad-plus",
    title: "Notepad++",
    category: "应用",
    icon: "📄"
  },
  {
    id: "notion",
    title: "Notion",
    category: "应用",
    icon: "📋"
  },
  {
    id: "notes-app",
    title: "Notes",
    category: "应用",
    icon: "🗒️"
  },
  {
    id: "vscode",
    title: "Visual Studio Code",
    category: "应用",
    icon: "💻"
  },
  {
    id: "chrome",
    title: "Google Chrome",
    category: "应用",
    icon: "🌐"
  },
  {
    id: "photoshop",
    title: "Adobe Photoshop",
    category: "应用",
    icon: "🎨"
  },
  {
    id: "my-document1",
    title: "会议记录 - 2024年12月.docx",
    category: "文档",
    icon: "📄"
  },
  {
    id: "my-document2",
    title: "项目计划书.docx",
    category: "文档",
    icon: "📄"
  },
  {
    id: "my-document3",
    title: "年度总结报告.pdf",
    category: "文档",
    icon: "📄"
  },
  {
    id: "my-document4",
    title: "用户需求分析.xlsx",
    category: "文档",
    icon: "📊"
  },
  {
    id: "my-document5",
    title: "产品原型设计.pptx",
    category: "文档",
    icon: "📋"
  },
  {
    id: "my-document6",
    title: "技术文档.md",
    category: "文档",
    icon: "📝"
  },
  {
    id: "my-document7",
    title: "数据库设计.sql",
    category: "文档",
    icon: "🗃️"
  },
  {
    id: "my-document8",
    title: "接口文档.json",
    category: "文档",
    icon: "🔗"
  },
  {
    id: "history1",
    title: "上次搜索：React 组件开发",
    category: "时光机",
    icon: "⏰",
    timeRange: {
      start: "2024年12月15日 10:25",
      end: "2024年12月15日 10:47"
    },
    description: "在开发过程中搜索了React组件的最佳实践和设计模式，主要关注函数组件与Hook的使用方法，以及组件间的数据传递和状态管理。期间浏览了多个技术博客和官方文档，学习了组件生命周期的优化策略。"
  },
  {
    id: "history2",
    title: "常用：Visual Studio Code",
    category: "时光机",
    icon: "⭐",
    timeRange: {
      start: "2024年12月14日 09:00",
      end: "2024年12月14日 18:30"
    },
    description: "作为日常开发的主要编辑器，今天使用VSCode完成了多项开发任务。配置了新的插件，优化了工作区设置，并使用了集成终端进行项目构建。整体工作流程非常顺畅，代码高亮和自动补全功能大大提升了开发效率。"
  },
  {
    id: "history3",
    title: "最近打开：项目计划书.docx",
    category: "时光机",
    icon: "🕰️",
    timeRange: {
      start: "2024年12月15日 14:15",
      end: "2024年12月15日 15:02"
    },
    description: "查看和编辑了下一阶段的项目计划文档，更新了项目进度和里程碑节点。调整了资源分配计划，并添加了风险评估部分。文档结构清晰，便于团队成员理解项目目标和时间安排。"
  },
  {
    id: "history4",
    title: "搜索历史：JavaScript教程",
    category: "时光机",
    icon: "🔮",
    timeRange: {
      start: "2024年12月13日 16:20",
      end: "2024年12月13日 17:45"
    },
    description: "深入学习JavaScript的异步编程概念，包括Promise、async/await和事件循环机制。通过多个在线教程和实践案例，加深了对异步操作的理解。特别关注了错误处理和性能优化方面的内容，对提升代码质量很有帮助。"
  },
  {
    id: "history5",
    title: "访问记录：GitHub仓库",
    category: "时光机",
    icon: "🌀",
    timeRange: {
      start: "2024年12月15日 11:30",
      end: "2024年12月15日 12:15"
    },
    description: "浏览了几个开源项目的源码，学习了优秀的代码架构和设计模式。特别关注了项目的文档结构、测试策略和CI/CD配置。通过阅读其他开发者的代码实现，获得了很多新的编程思路和解决方案。"
  },
  {
    id: "history6",
    title: "打开记录：Photoshop",
    category: "时光机",
    icon: "✨",
    timeRange: {
      start: "2024年12月14日 20:00",
      end: "2024年12月14日 22:30"
    },
    description: "使用Photoshop处理了一批用户界面设计素材，包括图标优化、背景图片调整和色彩搭配。尝试了新的滤镜效果和图层混合模式，创作了几个有创意的视觉效果。整个设计过程很有成就感，最终效果超出预期。"
  }
];

export default function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [selectedResult, setSelectedResult] = useState<string | null>("onenote-win10");
  const [focusArea, setFocusArea] = useState<FocusArea>('search');
  const [selectedTabIndex, setSelectedTabIndex] = useState(0);
  const [selectedResultIndex, setSelectedResultIndex] = useState(0);
  const [detailFocusArea, setDetailFocusArea] = useState<DetailFocusArea>('content');
  const [selectedActionIndex, setSelectedActionIndex] = useState(0);
  const [theme, setTheme] = useState<Theme>('dark');
  const [showSettings, setShowSettings] = useState(false);

  // API数据状态
  const [timeMachineData, setTimeMachineData] = useState<ResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // 搜索状态
  const [searchResults, setSearchResults] = useState<ResultItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [lastSearchQuery, setLastSearchQuery] = useState("");

  const searchInputRef = useRef<HTMLInputElement>(null);

  // 工具函数
  const getThemeColors = () => ({
    background: theme === 'dark' ? 'rgb(47, 48, 49)' : 'rgb(248, 249, 250)',
    panel: theme === 'dark' ? 'rgb(60, 60, 60)' : 'white',
    text: theme === 'dark' ? 'white' : 'rgb(17, 24, 39)',
    textSecondary: theme === 'dark' ? 'text-gray-400' : 'text-gray-600',
    textTertiary: theme === 'dark' ? 'text-gray-500' : 'text-gray-500'
  });

  const getKbdClasses = () =>
    `inline-flex items-center justify-center h-5 px-2 text-xs font-medium rounded border ${
      theme === 'dark'
        ? 'bg-slate-700 text-gray-300 border-slate-600'
        : 'bg-gray-100 text-gray-700 border-gray-300'
    }`;

  const getArrowKbdClasses = () =>
    `inline-flex items-center justify-center min-w-6 h-5 px-1.5 text-xs font-medium rounded border ${
      theme === 'dark'
        ? 'bg-slate-700 text-gray-300 border-slate-600'
        : 'bg-gray-100 text-gray-700 border-gray-300'
    }`;

  // API数据加载函数
  const loadTimeMachineData = async () => {
    try {
      setIsLoading(true);
      setApiError(null);

      // 改为拉取事件列表（事件粒度）
      const events = await apiClient.listEvents({ limit: 50 });
      const transformed = events.map(e => ({
        ...transformEventToResultItem(e),
      }));
      setTimeMachineData(transformed);

    } catch (error) {
      console.error('Failed to load time machine data:', error);
      setApiError(error instanceof Error ? error.message : '加载数据失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 搜索函数（使用语义搜索，回退到简单搜索）
  const performSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      setHasSearched(false);
      setLastSearchQuery("");
      return;
    }

    try {
      setIsSearching(true);
      setApiError(null);

      console.log('开始语义搜索:', query);

      try {
        // 优先使用事件级语义搜索
        const eventResults = await apiClient.semanticSearchEvents(query.trim(), 20);
        const transformedResults = eventResults.map(e => transformEventToResultItem(e));
        setSearchResults(transformedResults);
        setHasSearched(true);
        setLastSearchQuery(query);
        console.log('语义搜索成功，找到', eventResults.length, '个结果');
      } catch (semanticError) {
        console.warn('语义搜索失败，回退到简单搜索:', semanticError);
        // 回退到简单搜索
        const eventResults = await apiClient.searchEvents(query.trim(), 20);
        const transformedResults = eventResults.map(e => transformEventToResultItem(e));
        setSearchResults(transformedResults);
        setHasSearched(true);
        setLastSearchQuery(query);
        console.log('简单搜索成功，找到', eventResults.length, '个结果');
      }

    } catch (error) {
      console.error('搜索失败:', error);
      setApiError(error instanceof Error ? error.message : '搜索失败');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // 实时搜索函数（移除防抖，立即搜索）
  const handleSearchQueryChange = (query: string) => {
    setSearchQuery(query);

    // 如果查询为空，立即清除搜索结果
    if (!query.trim()) {
      setSearchResults([]);
      setHasSearched(false);
      setLastSearchQuery("");
      return;
    }

    // 设置搜索状态为true，即使还没开始搜索
    setHasSearched(true);

    // 立即执行搜索（实时搜索）
    performSearch(query);
  };

  // 组合所有数据源
  const getAllResults = () => {
    // 应用和文档类别继续使用MOCK数据
    const mockAppsAndDocs = MOCK_RESULTS.filter(item =>
      item.category === '应用' || item.category === '文档'
    );

    // 时光机使用API数据
    return [...mockAppsAndDocs, ...timeMachineData];
  };

  const filteredResults = (() => {
    // 如果有搜索查询，只显示搜索结果（即使为空）
    if (searchQuery.trim()) {
      return searchResults;
    }

    // 否则按标签筛选
    if (activeTab === 'all') {
      return getAllResults();
    } else if (activeTab === 'timemachine') {
      return timeMachineData;
    } else {
      return MOCK_RESULTS.filter(result =>
        result.category === TAB_TO_CATEGORY[activeTab as keyof typeof TAB_TO_CATEGORY]
      );
    }
  })();

  // 选中结果的工具函数
  const selectResultByIndex = (index: number) => {
    if (index >= 0 && index < filteredResults.length) {
      setSelectedResultIndex(index);
      setSelectedResult(filteredResults[index].id);
    }
  };

  const navigateToResults = () => {
    setFocusArea('results');
    if (selectedResult && filteredResults.find(r => r.id === selectedResult)) {
      const currentIndex = filteredResults.findIndex(r => r.id === selectedResult);
      setSelectedResultIndex(currentIndex);
    } else {
      selectResultByIndex(0);
    }
  };

  const resetDetailFocus = () => {
    setDetailFocusArea('content');
    setSelectedActionIndex(0);
  };

  // 事件处理
  const handleThemeToggle = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  const handleSettingsClick = () => setShowSettings(true);
  const handleCloseClick = () => {
    if (window.electronAPI && window.electronAPI.minimizeToTray) {
      window.electronAPI.minimizeToTray();
    } else {
      console.log('Electron API not available');
    }
  };

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    const newTabIndex = TABS.findIndex(tab => tab.id === tabId);
    if (newTabIndex !== -1) {
      setSelectedTabIndex(newTabIndex);
    }
    // 切换标签时清除搜索结果
    setSearchResults([]);
    setHasSearched(false);
    setLastSearchQuery("");
  };

  const handleSelectResult = (id: string) => {
    setSelectedResult(id);
    const index = filteredResults.findIndex(result => result.id === id);
    if (index !== -1) {
      setSelectedResultIndex(index);
    }
  };

  // 组件挂载时加载时光机数据
  useEffect(() => {
    loadTimeMachineData();
  }, []);

  // 实时搜索，无需清理定时器

  // 当切换到时光机标签且数据为空时重新加载
  useEffect(() => {
    if (activeTab === 'timemachine' && timeMachineData.length === 0 && !isLoading) {
      loadTimeMachineData();
    }
  }, [activeTab, timeMachineData.length, isLoading]);

  // 键盘事件处理
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (showSettings) {
        if (e.key === 'Escape') {
          e.preventDefault();
          setShowSettings(false);
        }
        return;
      }

      // 只对导航键阻止默认行为，允许文本输入键正常工作
      const isNavigationKey = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Enter', 'Escape', 'Tab'].includes(e.key);

      // 如果焦点在搜索框且不是导航键，则允许默认行为（文本输入、删除等）
      if (focusArea === 'search' && !isNavigationKey) {
        return;
      }

      // 对导航键阻止默认行为
      if (isNavigationKey) {
        e.preventDefault();
      }

      switch (e.key) {
        case 'ArrowUp':
          if (focusArea === 'results' && selectedResultIndex > 0) {
            selectResultByIndex(selectedResultIndex - 1);
          } else if (focusArea === 'results' && selectedResultIndex === 0) {
            setFocusArea('tabs');
          } else if (focusArea === 'details') {
            if (detailFocusArea === 'actions' && selectedActionIndex > 0) {
              setSelectedActionIndex(selectedActionIndex - 1);
            } else if (detailFocusArea === 'actions' && selectedActionIndex === 0) {
              setDetailFocusArea('content');
            }
          }
          break;

        case 'ArrowDown':
          if ((focusArea === 'search' || focusArea === 'tabs') && filteredResults.length > 0) {
            navigateToResults();
          } else if (focusArea === 'results' && selectedResultIndex < filteredResults.length - 1) {
            selectResultByIndex(selectedResultIndex + 1);
          } else if (focusArea === 'details') {
            if (detailFocusArea === 'content') {
              setDetailFocusArea('actions');
              setSelectedActionIndex(0);
            } else if (detailFocusArea === 'actions' && selectedActionIndex < ACTION_COUNT - 1) {
              setSelectedActionIndex(selectedActionIndex + 1);
            }
          }
          break;

        case 'ArrowLeft':
          if (focusArea === 'tabs' && selectedTabIndex > 0) {
            const newIndex = selectedTabIndex - 1;
            setSelectedTabIndex(newIndex);
            setActiveTab(TABS[newIndex].id);
          } else if (focusArea === 'results') {
            setFocusArea('tabs');
          } else if (focusArea === 'details') {
            setFocusArea('results');
            resetDetailFocus();
          }
          break;

        case 'ArrowRight':
          if (focusArea === 'tabs' && selectedTabIndex < TABS.length - 1) {
            const newIndex = selectedTabIndex + 1;
            setSelectedTabIndex(newIndex);
            setActiveTab(TABS[newIndex].id);
          } else if (focusArea === 'results') {
            setFocusArea('details');
            resetDetailFocus();
          }
          break;

        case 'Enter':
          if (focusArea === 'search') {
            // 在搜索框中按回车触发搜索
            performSemanticSearch(searchQuery);
          } else if (focusArea === 'results' && selectedResult) {
            console.log(`Opening: ${filteredResults[selectedResultIndex].title}`);
          } else if (focusArea === 'details' && detailFocusArea === 'actions') {
            console.log(`Executing action: ${ACTIONS[selectedActionIndex]}`);
          }
          break;

        case 'Escape':
          setFocusArea('search');
          resetDetailFocus();
          // 清除搜索结果
          setSearchResults([]);
          setHasSearched(false);
          setLastSearchQuery("");
          searchInputRef.current?.focus();
          break;

        case 'Tab':
          const currentIndex = FOCUS_AREAS.indexOf(focusArea);
          const nextIndex = e.shiftKey
            ? (currentIndex - 1 + FOCUS_AREAS.length) % FOCUS_AREAS.length
            : (currentIndex + 1) % FOCUS_AREAS.length;
          const nextArea = FOCUS_AREAS[nextIndex];

          setFocusArea(nextArea);

          if (nextArea === 'search') {
            searchInputRef.current?.focus();
          } else if (nextArea === 'details') {
            resetDetailFocus();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [focusArea, selectedTabIndex, selectedResultIndex, selectedResult, filteredResults.length, detailFocusArea, selectedActionIndex, showSettings]);

  // 状态同步效果
  useEffect(() => {
    const tabIndex = TABS.findIndex(tab => tab.id === activeTab);
    if (tabIndex !== -1 && selectedTabIndex !== tabIndex) {
      setSelectedTabIndex(tabIndex);
    }
  }, [activeTab, selectedTabIndex]);

  useEffect(() => {
    if (selectedResult) {
      const resultIndex = filteredResults.findIndex(result => result.id === selectedResult);
      if (resultIndex !== -1) {
        setSelectedResultIndex(resultIndex);
      }
    }
  }, [selectedResult, filteredResults]);

  useEffect(() => {
    if (filteredResults.length > 0) {
      selectResultByIndex(0);
    } else {
      setSelectedResult(null);
      setSelectedResultIndex(0);
    }
  }, [activeTab]);

  const colors = getThemeColors();

  if (showSettings) {
    return (
      <Settings
        theme={theme}
        onThemeToggle={handleThemeToggle}
        onClose={() => setShowSettings(false)}
      />
    );
  }

  return (
    <div
      className={`h-screen flex flex-col transition-colors duration-300 ${
        theme === 'dark' ? 'text-white' : 'text-gray-900'
      }`}
      style={{ backgroundColor: colors.background }}
    >
      <SearchHeader
        searchQuery={searchQuery}
        onSearchQueryChange={handleSearchQueryChange}
        focused={focusArea === 'search'}
        theme={theme}
        onThemeToggle={handleThemeToggle}
        onSettingsClick={handleSettingsClick}
        onCloseClick={handleCloseClick}
        ref={searchInputRef}
      />

      <SearchTabs
        activeTab={activeTab}
        onTabChange={handleTabChange}
        focused={focusArea === 'tabs'}
        selectedIndex={selectedTabIndex}
        theme={theme}
      />

      <div className="flex-1 flex overflow-hidden">
        <SearchResults
          results={filteredResults}
          selectedId={selectedResult}
          selectedIndex={selectedResultIndex}
          onSelectResult={handleSelectResult}
          focused={focusArea === 'results'}
          theme={theme}
          isLoading={isSearching}
          error={apiError}
          hasSearched={hasSearched}
          searchQuery={searchQuery}
        />

        <DetailPanel
          selectedResult={selectedResult}
          selectedResultData={selectedResult ? filteredResults.find(r => r.id === selectedResult) : null}
          focused={focusArea === 'details'}
          detailFocusArea={detailFocusArea}
          selectedActionIndex={selectedActionIndex}
          theme={theme}
        />
      </div>

      {/* 键盘提示 */}
      {!showSettings && (
        <div className="px-6 py-3">
          <div
            className="rounded-xl px-4 py-3 backdrop-blur-sm border"
            style={{
              backgroundColor: theme === 'dark' ? 'rgba(60, 60, 60, 0.8)' : 'rgba(255, 255, 255, 0.9)',
              borderColor: theme === 'dark' ? 'rgba(100, 100, 100, 0.2)' : 'rgba(200, 200, 200, 0.3)'
            }}
          >
            <div className="flex items-center justify-between max-w-4xl mx-auto">
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5">
                    <kbd className={getArrowKbdClasses()}>↑</kbd>
                    <kbd className={getArrowKbdClasses()}>↓</kbd>
                  </div>
                  <span className={`text-sm font-medium ml-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                    导航结果
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5">
                    <kbd className={getArrowKbdClasses()}>←</kbd>
                    <kbd className={getArrowKbdClasses()}>→</kbd>
                  </div>
                  <span className={`text-sm font-medium ml-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                    切换标签
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <kbd className={getKbdClasses()}>Enter</kbd>
                  <span className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                    打开
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <kbd className={getKbdClasses()}>Esc</kbd>
                  <span className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                    返回搜索
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <kbd className={getKbdClasses()}>Tab</kbd>
                  <span className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                    切换区域
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
