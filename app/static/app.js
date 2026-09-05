// PyForge State and UI Controller

let currentTab = 'scaffolder';
let currentTemplate = null;
let currentSelectedFile = null;
let currentTemplatesList = [];
let allSnippets = [];
let allFrameworks = [];
let currentUser = null;
let currentForumCategory = 'all';
let currentForumSearch = '';
let currentTopicDetail = null;
let currentIdeasStatus = 'all';
let allLeaderboardData = [];

// Auth Helpers
function getAuthToken() {
  return localStorage.getItem('pyforge_token') || null;
}

function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// Global User Role Cache for instant visual updates across all components
window.allUsersRoleCache = window.allUsersRoleCache || {};

// Developer & Role Badge Helpers (Chevels, Creator, Admin, Mod, VIP, Mentor, Custom Roles)
function getUserRole(userOrName) {
  if (!userOrName) return 'user';
  if (typeof userOrName === 'string') {
    const uname = userOrName.toLowerCase().trim();
    if (uname === 'chevels') return 'creator';
    if (currentUser && (currentUser.username || '').toLowerCase() === uname && currentUser.role) {
      return currentUser.role;
    }
    if (window.allUsersRoleCache && window.allUsersRoleCache[uname]) {
      return window.allUsersRoleCache[uname];
    }
    return 'user';
  }
  const uname = (userOrName.username || userOrName.author_username || '').toLowerCase().trim();
  if (uname === 'chevels') return 'creator';
  const resolvedRole = userOrName.role || userOrName.author_role || (userOrName.is_developer ? 'creator' : null) || (window.allUsersRoleCache && window.allUsersRoleCache[uname]) || 'user';
  if (uname && resolvedRole && resolvedRole !== 'user') {
    window.allUsersRoleCache[uname] = resolvedRole;
  }
  return resolvedRole;
}

function isDeveloperUser(userOrName) {
  if (!userOrName) return false;
  const role = getUserRole(userOrName);
  if (typeof userOrName === 'string') {
    const uname = userOrName.toLowerCase().trim();
    return uname === 'chevels' || role === 'creator' || role === 'admin';
  }
  const uname = (userOrName.username || userOrName.author_username || '').toLowerCase().trim();
  return uname === 'chevels' || userOrName.is_developer === true || role === 'creator' || role === 'admin';
}

function getUserBadgeHtml(userOrName, extraClass = '') {
  const role = getUserRole(userOrName);
  if (!role || role === 'user') return '';
  if (role === 'creator') {
    return `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-gradient-to-r from-amber-500/25 via-orange-500/25 to-rose-500/25 border border-amber-500/60 text-amber-300 font-extrabold text-[10px] tracking-wide shadow-sm shadow-amber-500/20 select-none ${extraClass}" title="👑 Создатель платформы PyForge"><i data-lucide="crown" class="w-3 h-3 text-amber-400 flex-shrink-0"></i><span class="bg-gradient-to-r from-amber-300 via-orange-300 to-rose-300 bg-clip-text text-transparent font-black">CREATOR</span></span>`;
  }
  if (role === 'admin') {
    return `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-red-500/20 border border-red-500/50 text-red-300 font-extrabold text-[10px] tracking-wide shadow-sm shadow-red-500/20 select-none ${extraClass}" title="⚡ Администратор"><i data-lucide="shield-alert" class="w-3 h-3 text-red-400 flex-shrink-0"></i><span class="font-black">ADMIN</span></span>`;
  }
  if (role === 'moderator') {
    return `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 font-extrabold text-[10px] tracking-wide shadow-sm shadow-emerald-500/20 select-none ${extraClass}" title="🛡️ Модератор"><i data-lucide="shield-check" class="w-3 h-3 text-emerald-400 flex-shrink-0"></i><span class="font-black">MOD</span></span>`;
  }
  if (role === 'vip') {
    return `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-purple-500/20 border border-purple-500/50 text-purple-300 font-extrabold text-[10px] tracking-wide shadow-sm shadow-purple-500/20 select-none ${extraClass}" title="⭐ VIP Пользователь"><i data-lucide="sparkles" class="w-3 h-3 text-purple-400 flex-shrink-0"></i><span class="font-black">VIP</span></span>`;
  }
  if (role === 'mentor') {
    return `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-cyan-500/20 border border-cyan-500/50 text-cyan-300 font-extrabold text-[10px] tracking-wide shadow-sm shadow-cyan-500/20 select-none ${extraClass}" title="🧠 Эксперт & Ментор"><i data-lucide="brain" class="w-3 h-3 text-cyan-400 flex-shrink-0"></i><span class="font-black">MENTOR</span></span>`;
  }
  const customRole = (window.devLoadedRoles || []).find(r => r.id === role);
  if (customRole) {
    const icon = customRole.icon || 'award';
    const colorClass = customRole.color_class || 'bg-sky-500/20 border-sky-500/50 text-sky-300';
    return `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md border text-[10px] font-extrabold tracking-wide select-none ${colorClass} ${extraClass}" title="${escapeHtml(customRole.name)}"><i data-lucide="${icon}" class="w-3 h-3 flex-shrink-0"></i><span>${escapeHtml(customRole.name.toUpperCase())}</span></span>`;
  }
  return `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-slate-300 text-[10px] font-bold select-none ${extraClass}"><i data-lucide="award" class="w-3 h-3 flex-shrink-0"></i><span>${escapeHtml(role.toUpperCase())}</span></span>`;
}

function getDeveloperBadgeHtml(userOrName, extraClass = '') {
  return getUserBadgeHtml(userOrName, extraClass);
}

// Playground Code Presets
const PLAYGROUND_PRESETS = {
  async: `import asyncio
import time

async def worker(task_id: int, delay: float):
    print(f"▶️ Начало задачи {task_id}")
    await asyncio.sleep(delay)
    print(f"✅ Задача {task_id} завершена за {delay}с")
    return f"Результат {task_id}"

async def main():
    start = time.perf_counter()
    # Запускаем задачи параллельно
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(worker(1, 0.5))
        t2 = tg.create_task(worker(2, 0.3))
        t3 = tg.create_task(worker(3, 0.7))

    total = time.perf_counter() - start
    print(f"\\n⏱️ Все 3 задачи завершены параллельно за {total:.2f} сек!")

if __name__ == "__main__":
    asyncio.run(main())
`,
  dataclass: `from dataclasses import dataclass, field
from typing import List

@dataclass
class Product:
    id: int
    title: str
    price: float
    tags: List[str] = field(default_factory=list)

    @property
    def formatted_price(self) -> str:
        return f"{self.price:.2f} ₽"

p1 = Product(id=1, title="Python Pro Book", price=1250.0, tags=["python", "books"])
p2 = Product(id=2, title="Mechanical Keyboard", price=8900.5, tags=["hardware"])

print("Товар 1:", p1)
print("Форматированная цена:", p1.formatted_price)
print("Товар 2 теги:", p2.tags)
`,
  matching: `def parse_action(command: dict):
    match command:
        case {"action": "create", "type": "user", "name": str(name)}:
            return f"Создание пользователя: {name}"
        case {"action": "delete", "id": int(item_id), "force": True}:
            return f"Принудительное удаление объекта #{item_id}"
        case {"action": "delete", "id": int(item_id)}:
            return f"Мягкое удаление объекта #{item_id}"
        case _:
            return "Неизвестная команда"

print(parse_action({"action": "create", "type": "user", "name": "Алексей"}))
print(parse_action({"action": "delete", "id": 105, "force": True}))
print(parse_action({"action": "unknown"}))
`,
  benchmark: `import time

def benchmark():
    size = 1_000_000
    print(f"Запуск теста производительности для {size:,} элементов...")

    start = time.perf_counter()
    # Генераторное выражение и сумма квадратов
    result = sum(i * 2 for i in range(size))
    elapsed = (time.perf_counter() - start) * 1000

    print(f"Сумма: {result:,}")
    print(f"Время выполнения: {elapsed:.2f} миллисекунд ⚡")

benchmark()
`
};

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', async () => {
  lucide.createIcons();
  loadDevRolesList(true);
  await checkAuthState();
  loadUserProfile();
  loadDailyQuests();
  loadPracticeTasks();
  loadAiSuggestions();
  loadTemplates();
  loadFrameworks();
  loadArchitecture();
  loadDatabases();
  loadPackaging();
  loadSnippets();
  loadTools();

  // Load default playground preset
  const editor = document.getElementById('playground-editor');
  if (editor) {
    editor.value = PLAYGROUND_PRESETS.async;
  }

  // Keyboard shortcut for search (Ctrl+K / Cmd+K)
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openSearchModal();
    }
    if (e.key === 'Escape') {
      closeSearchModal();
      closeDirectoryGenerateModal();
      closeAuthModal();
      closeProfileModal();
      closeTitleShopModal();
      closeNewTopicModal();
      closeTopicDetailModal();
      closeNewIdeaModal();
      closeDevPanelModal();
    }
  });
});

// Toast notification helper
function showToast(message) {
  const toast = document.getElementById('toast');
  const msgElem = document.getElementById('toast-message');
  msgElem.innerText = message;
  toast.classList.remove('translate-y-20', 'opacity-0');
  toast.classList.add('translate-y-0', 'opacity-100');
  setTimeout(() => {
    toast.classList.remove('translate-y-0', 'opacity-100');
    toast.classList.add('translate-y-20', 'opacity-0');
  }, 3000);
}

// Copy helper
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Скопировано в буфер обмена! 📋');
  });
}

// Tab Switching Logic
function switchTab(tabId) {
  currentTab = tabId;

  // Update Sidebar Nav buttons styling
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.classList.remove('active');
  });
  const activeNavBtn = document.getElementById(`nav-${tabId}`);
  if (activeNavBtn) activeNavBtn.classList.add('active');

  // Update Top Nav buttons styling
  document.querySelectorAll('.top-nav-btn').forEach(btn => {
    btn.classList.remove('bg-slate-800', 'text-white', 'border', 'border-slate-700');
    btn.classList.add('text-slate-300');
  });
  const activeTopBtn = document.getElementById(`top-nav-${tabId}`);
  if (activeTopBtn) {
    activeTopBtn.classList.add('bg-slate-800', 'text-white', 'border', 'border-slate-700');
    activeTopBtn.classList.remove('text-slate-300');
  }

  // Update visible section
  document.querySelectorAll('.tab-content').forEach(sec => {
    sec.classList.add('hidden');
  });
  const activeSec = document.getElementById(`tab-${tabId}`);
  if (activeSec) {
    activeSec.classList.remove('hidden');
  }

  // Lazy tab data loading
  if (tabId === 'leaderboard') {
    loadLeaderboard();
  } else if (tabId === 'forum') {
    loadForumCategories();
    loadForumTopics();
  } else if (tabId === 'ideas') {
    loadIdeas();
  } else if (tabId === 'practice') {
    loadDailyQuests();
  }

  // Re-run Prism and Lucide
  setTimeout(() => {
    Prism.highlightAll();
    lucide.createIcons();
  }, 50);
}

// --- TAB 1: TEMPLATES & SCAFFOLDER ---
async function loadTemplates() {
  try {
    const res = await fetch('/api/templates');
    const templates = await res.json();
    currentTemplatesList = templates;

    const container = document.getElementById('templates-list-container');
    container.innerHTML = '';

    templates.forEach((tpl, idx) => {
      const card = document.createElement('div');
      card.className = `p-4 rounded-xl border cursor-pointer transition ${idx === 0 ? 'bg-sky-950/40 border-sky-500/50' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'}`;
      card.id = `tpl-card-${tpl.id}`;
      card.onclick = () => selectTemplate(tpl.id);
      card.innerHTML = `
        <div class="flex items-start space-x-3">
          <div class="p-2.5 rounded-lg bg-slate-800 text-sky-400">
            <i data-lucide="${tpl.icon || 'code'}" class="w-5 h-5"></i>
          </div>
          <div class="flex-1">
            <div class="flex items-center justify-between">
              <h4 class="font-bold text-sm text-white">${tpl.name}</h4>
              <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">${tpl.files_count} файлов</span>
            </div>
            <p class="text-xs text-slate-400 mt-1 line-clamp-2">${tpl.description}</p>
          </div>
        </div>
      `;
      container.appendChild(card);
    });

    if (templates.length > 0) {
      selectTemplate(templates[0].id);
    }
    lucide.createIcons();
  } catch (err) {
    console.error('Ошибка загрузки шаблонов:', err);
  }
}

async function selectTemplate(templateId) {
  try {
    // Update card styling
    currentTemplatesList.forEach(t => {
      const el = document.getElementById(`tpl-card-${t.id}`);
      if (el) {
        if (t.id === templateId) {
          el.className = 'p-4 rounded-xl border cursor-pointer transition bg-sky-950/40 border-sky-500/50 shadow-md';
        } else {
          el.className = 'p-4 rounded-xl border cursor-pointer transition bg-slate-900/60 border-slate-800 hover:border-slate-700';
        }
      }
    });

    const res = await fetch(`/api/templates/${templateId}`);
    currentTemplate = await res.json();

    document.getElementById('selected-template-name').innerText = currentTemplate.name;
    document.getElementById('selected-template-desc').innerText = currentTemplate.description;

    // Render file tabs
    const tabsContainer = document.getElementById('file-tabs-container');
    tabsContainer.innerHTML = '';

    const fileKeys = Object.keys(currentTemplate.files);
    fileKeys.forEach((fileName, idx) => {
      const btn = document.createElement('button');
      btn.className = `px-3 py-1 rounded-md text-xs font-mono font-medium transition flex items-center gap-1.5 ${idx === 0 ? 'bg-sky-600 text-white' : 'bg-slate-800/80 text-slate-400 hover:text-slate-200'}`;
      btn.id = `file-tab-btn-${idx}`;
      btn.onclick = () => selectFileTab(fileName, idx);
      btn.innerHTML = `<span>${fileName}</span>`;
      tabsContainer.appendChild(btn);
    });

    if (fileKeys.length > 0) {
      selectFileTab(fileKeys[0], 0);
    }
  } catch (err) {
    console.error('Ошибка выбора шаблона:', err);
  }
}

function selectFileTab(fileName, index) {
  currentSelectedFile = fileName;
  const fileKeys = Object.keys(currentTemplate.files);
  fileKeys.forEach((_, idx) => {
    const btn = document.getElementById(`file-tab-btn-${idx}`);
    if (btn) {
      if (idx === index) {
        btn.className = 'px-3 py-1 rounded-md text-xs font-mono font-medium transition bg-sky-600 text-white';
      } else {
        btn.className = 'px-3 py-1 rounded-md text-xs font-mono font-medium transition bg-slate-800/80 text-slate-400 hover:text-slate-200';
      }
    }
  });

  const content = currentTemplate.files[fileName] || '';
  const codeElem = document.getElementById('current-file-code-display');
  codeElem.textContent = content;

  // Guess language
  if (fileName.endsWith('.py')) {
    codeElem.className = 'language-python';
  } else if (fileName.endsWith('.toml')) {
    codeElem.className = 'language-toml';
  } else if (fileName.endsWith('.md') || fileName.endsWith('.txt')) {
    codeElem.className = 'language-markdown';
  } else {
    codeElem.className = 'language-python';
  }

  Prism.highlightElement(codeElem);
}

function copyCurrentFileCode() {
  if (currentTemplate && currentSelectedFile) {
    copyToClipboard(currentTemplate.files[currentSelectedFile]);
  }
}

function downloadCurrentProjectZip() {
  if (!currentTemplate) return;
  window.location.href = `/api/scaffold/download/${currentTemplate.id}?project_name=${currentTemplate.id}`;
}

function showDirectoryGenerateModal() {
  if (!currentTemplate) return;
  document.getElementById('modal-project-name').value = currentTemplate.id;
  document.getElementById('dir-modal').classList.remove('hidden');
}

function closeDirectoryGenerateModal() {
  document.getElementById('dir-modal').classList.add('hidden');
}

async function confirmGenerateToDirectory() {
  const projectName = document.getElementById('modal-project-name').value.trim();
  const targetDir = document.getElementById('modal-target-dir').value.trim();
  const submitBtn = document.getElementById('modal-submit-btn');

  if (!projectName || !targetDir) {
    alert('Пожалуйста, заполните имя проекта и директорию');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = 'Создание файлов...';

  try {
    const res = await fetch('/api/scaffold/directory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template_id: currentTemplate.id,
        target_directory: targetDir,
        project_name: projectName
      })
    });

    const data = await res.json();
    if (res.ok) {
      closeDirectoryGenerateModal();
      showToast(`Проект успешно создан в ${data.directory}! 🎉`);
    } else {
      alert(`Ошибка: ${data.detail || 'Не удалось создать проект'}`);
    }
  } catch (err) {
    alert(`Ошибка соединения: ${err.message}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Сгенерировать проект';
  }
}

// --- TAB 2: FRAMEWORKS ---
async function loadFrameworks() {
  try {
    const res = await fetch('/api/frameworks');
    allFrameworks = await res.json();
    renderFrameworkCards(allFrameworks);
  } catch (err) {
    console.error('Ошибка загрузки фреймворков:', err);
  }
}

function filterFrameworks(cat) {
  // Update buttons
  document.querySelectorAll('.fw-filter-btn').forEach(btn => {
    btn.className = 'fw-filter-btn px-3.5 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-400 hover:bg-slate-700 border border-slate-700';
  });
  event.target.className = 'fw-filter-btn px-3.5 py-1.5 rounded-lg text-xs font-medium bg-sky-500/20 text-sky-400 border border-sky-500/30';

  if (cat === 'all') {
    renderFrameworkCards(allFrameworks);
  } else {
    const filtered = allFrameworks.filter(f => f.category === cat);
    renderFrameworkCards(filtered);
  }
}

function renderFrameworkCards(frameworks) {
  const container = document.getElementById('frameworks-cards-container');
  container.innerHTML = '';

  frameworks.forEach(fw => {
    const card = document.createElement('div');
    card.className = 'glass-card rounded-2xl p-6 border border-slate-800 space-y-4 flex flex-col justify-between';

    const prosHtml = fw.pros.map(p => `<li class="flex items-start gap-1.5"><span class="text-emerald-400">✓</span> <span>${p}</span></li>`).join('');
    const consHtml = fw.cons.map(c => `<li class="flex items-start gap-1.5"><span class="text-amber-400">✗</span> <span>${c}</span></li>`).join('');

    card.innerHTML = `
      <div class="space-y-4">
        <div class="flex items-start justify-between">
          <div class="flex items-center space-x-3">
            <div class="p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-sky-400">
              <i data-lucide="${fw.icon || 'layers'}" class="w-6 h-6"></i>
            </div>
            <div>
              <h3 class="font-bold text-lg text-white">${fw.name}</h3>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-medium">${fw.badge}</span>
            </div>
          </div>
        </div>

        <p class="text-sm text-slate-300 leading-relaxed">${fw.description}</p>

        <!-- Pros / Cons -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div class="bg-emerald-950/20 border border-emerald-500/20 p-3 rounded-xl">
            <div class="font-bold text-emerald-400 mb-1.5">Преимущества:</div>
            <ul class="space-y-1 text-slate-300">${prosHtml}</ul>
          </div>
          <div class="bg-amber-950/20 border border-amber-500/20 p-3 rounded-xl">
            <div class="font-bold text-amber-400 mb-1.5">Особенности:</div>
            <ul class="space-y-1 text-slate-300">${consHtml}</ul>
          </div>
        </div>

        <!-- Quickstart snippet -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-xs text-slate-400">
            <span>Установка: <code class="text-sky-400 bg-slate-900 px-2 py-0.5 rounded">${fw.install}</code></span>
            <div class="flex space-x-2">
              <button onclick="sendToPlayground(${JSON.stringify(fw.quickstart).replace(/"/g, '&quot;')})" class="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
                <i data-lucide="play" class="w-3.5 h-3.5"></i> В песочницу
              </button>
              <button onclick="copyToClipboard(${JSON.stringify(fw.quickstart).replace(/"/g, '&quot;')})" class="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1">
                <i data-lucide="copy" class="w-3.5 h-3.5"></i> Копировать
              </button>
            </div>
          </div>
          <div class="max-h-48 overflow-y-auto rounded-lg border border-slate-800">
            <pre class="m-0"><code class="language-python">${escapeHtml(fw.quickstart)}</code></pre>
          </div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });

  Prism.highlightAll();
  lucide.createIcons();
}

// --- TAB 3: ARCHITECTURE ---
async function loadArchitecture() {
  try {
    const res = await fetch('/api/architecture');
    const topics = await res.json();
    renderTopicCards('architecture-cards-container', topics);
  } catch (err) {
    console.error('Ошибка загрузки архитектуры:', err);
  }
}

// --- TAB 4: DATABASES ---
async function loadDatabases() {
  try {
    const res = await fetch('/api/databases');
    const topics = await res.json();
    renderTopicCards('databases-cards-container', topics);
  } catch (err) {
    console.error('Ошибка загрузки баз данных:', err);
  }
}

// --- TAB 5: PACKAGING ---
async function loadPackaging() {
  try {
    const res = await fetch('/api/packaging');
    const topics = await res.json();
    renderTopicCards('packaging-cards-container', topics);
  } catch (err) {
    console.error('Ошибка загрузки упаковки:', err);
  }
}

// --- TAB 7: TOOLS ---
async function loadTools() {
  try {
    const res = await fetch('/api/tools');
    const topics = await res.json();
    renderTopicCards('tools-cards-container', topics);
  } catch (err) {
    console.error('Ошибка загрузки инструментов:', err);
  }
}

// Render generic knowledge topic cards
function renderTopicCards(containerId, topics) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';

  topics.forEach(topic => {
    const card = document.createElement('div');
    card.className = 'glass-panel rounded-2xl p-6 border border-slate-800 space-y-4';
    card.id = `topic-${topic.id}`;

    // Convert markdown content to styled blocks
    const parsedHtml = formatMarkdownContent(topic.content);

    card.innerHTML = `
      <div class="flex items-start justify-between border-b border-slate-800/80 pb-4">
        <div class="flex items-center space-x-3">
          <div class="p-2.5 rounded-xl bg-slate-800 text-sky-400 border border-slate-700/50">
            <i data-lucide="${topic.icon || 'book-open'}" class="w-6 h-6"></i>
          </div>
          <div>
            <h3 class="font-bold text-lg text-white">${topic.title}</h3>
            <p class="text-xs text-slate-400 mt-0.5">${topic.summary}</p>
          </div>
        </div>
      </div>
      <div class="prose prose-invert max-w-none text-sm text-slate-300 space-y-3">
        ${parsedHtml}
      </div>
    `;
    container.appendChild(card);
  });

  Prism.highlightAll();
  lucide.createIcons();
}

// --- TAB 6: SNIPPETS ---
async function loadSnippets() {
  try {
    const res = await fetch('/api/snippets');
    allSnippets = await res.json();
    renderSnippetCards(allSnippets);
  } catch (err) {
    console.error('Ошибка загрузки сниппетов:', err);
  }
}

function searchSnippets() {
  const query = document.getElementById('snippet-search-input').value.toLowerCase().trim();
  if (!query) {
    renderSnippetCards(allSnippets);
    return;
  }
  const filtered = allSnippets.filter(s => {
    const tagsStr = (s.tags || []).join(' ').toLowerCase();
    return s.title.toLowerCase().includes(query) ||
           s.description.toLowerCase().includes(query) ||
           tagsStr.includes(query) ||
           s.category.toLowerCase().includes(query);
  });
  renderSnippetCards(filtered);
}

function renderSnippetCards(snippets) {
  const container = document.getElementById('snippets-cards-container');
  container.innerHTML = '';

  if (snippets.length === 0) {
    container.innerHTML = '<p class="text-slate-500 text-center py-12">Сниппеты не найдены.</p>';
    return;
  }

  snippets.forEach(s => {
    const card = document.createElement('div');
    card.className = 'glass-card rounded-2xl p-6 border border-slate-800 space-y-4';

    const tagsHtml = (s.tags || []).map(t => `<span class="px-2 py-0.5 rounded bg-slate-800 text-sky-400 text-[11px] font-mono border border-slate-700/50">#${t}</span>`).join(' ');

    card.innerHTML = `
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
        <div>
          <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">${s.category}</span>
          <h3 class="font-bold text-base text-white mt-0.5">${s.title}</h3>
        </div>
        <div class="flex items-center space-x-2">
          <button onclick="sendToPlayground(${JSON.stringify(s.code).replace(/"/g, '&quot;')})" class="px-3 py-1.5 rounded-lg bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-500/30 text-emerald-400 text-xs font-medium flex items-center gap-1.5 transition">
            <i data-lucide="play" class="w-3.5 h-3.5"></i> Песочница
          </button>
          <button onclick="copyToClipboard(${JSON.stringify(s.code).replace(/"/g, '&quot;')})" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition">
            <i data-lucide="copy" class="w-3.5 h-3.5"></i> Копировать
          </button>
        </div>
      </div>

      <p class="text-xs text-slate-300">${s.description}</p>
      <div class="flex flex-wrap gap-1.5">${tagsHtml}</div>

      <div class="rounded-xl border border-slate-800 overflow-hidden">
        <pre class="m-0"><code class="language-python">${escapeHtml(s.code)}</code></pre>
      </div>
    `;
    container.appendChild(card);
  });

  Prism.highlightAll();
  lucide.createIcons();
}

// --- TAB 8: PLAYGROUND ---
function loadPlaygroundPreset() {
  const val = document.getElementById('playground-preset-select').value;
  if (PLAYGROUND_PRESETS[val]) {
    document.getElementById('playground-editor').value = PLAYGROUND_PRESETS[val];
  }
}

function sendToPlayground(code) {
  switchTab('playground');
  document.getElementById('playground-editor').value = code;
  document.getElementById('playground-output').innerText = 'Код загружен. Нажмите «Запустить код»...';
}

async function runPlaygroundCode() {
  const code = document.getElementById('playground-editor').value;
  const outputElem = document.getElementById('playground-output');
  const timerElem = document.getElementById('playground-timer');
  const runBtn = document.getElementById('run-code-btn');

  runBtn.disabled = true;
  runBtn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Выполнение...</span>';
  lucide.createIcons();

  timerElem.innerText = '⏱️ Запуск процесса...';
  outputElem.innerText = 'Исполнение кода на локальном интерпретаторе Python...';

  try {
    const res = await fetch('/api/sandbox/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code, timeout: 6.0 })
    });

    const data = await res.json();
    timerElem.innerText = `⏱️ Время: ${data.execution_time_ms} мс`;

    let out = '';
    if (data.stdout) {
      out += data.stdout;
    }
    if (data.stderr) {
      out += (out ? '\n--- Ошибки (stderr) ---\n' : '') + data.stderr;
    }
    if (!out) {
      out = '(Программа завершилась успешно без текстового вывода stdout)';
    }

    outputElem.innerText = out;
  } catch (err) {
    outputElem.innerText = `Ошибка песочницы: ${err.message}`;
  } finally {
    runBtn.disabled = false;
    runBtn.innerHTML = '<i data-lucide="play" class="w-4 h-4"></i><span>Запустить код</span>';
    lucide.createIcons();
  }
}

// --- INTERACTIVE PYINSTALLER COMMAND BUILDER ---
function updatePyInstallerCommand() {
  const onefile = document.getElementById('pyinst-onefile').checked;
  const windowed = document.getElementById('pyinst-windowed').checked;
  const clean = document.getElementById('pyinst-clean').checked;
  const appName = document.getElementById('pyinst-appname').value.trim() || 'MySuperApp';
  const script = document.getElementById('pyinst-script').value.trim() || 'src/main.py';

  let cmd = 'pyinstaller --noconfirm';
  if (onefile) cmd += ' --onefile';
  else cmd += ' --onedir';

  if (windowed) cmd += ' --windowed';
  if (clean) cmd += ' --clean';

  cmd += ` --name "${appName}" ${script}`;

  document.getElementById('pyinst-cmd-output').innerText = cmd;
}

// --- GLOBAL SEARCH MODAL ---
function openSearchModal() {
  document.getElementById('search-modal').classList.remove('hidden');
  const input = document.getElementById('modal-search-input');
  input.value = '';
  input.focus();
  document.getElementById('modal-search-results').innerHTML = '<p class="text-xs text-slate-500 text-center py-6">Начните вводить текст для поиска по всей базе знаний...</p>';
}

function closeSearchModal() {
  document.getElementById('search-modal').classList.add('hidden');
}

async function performGlobalSearch() {
  const q = document.getElementById('modal-search-input').value.trim();
  const resultsContainer = document.getElementById('modal-search-results');

  if (q.length < 2) {
    resultsContainer.innerHTML = '<p class="text-xs text-slate-500 text-center py-6">Введите минимум 2 символа для поиска...</p>';
    return;
  }

  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    const results = await res.json();

    if (results.length === 0) {
      resultsContainer.innerHTML = '<p class="text-xs text-slate-500 text-center py-6">Ничего не найдено по вашему запросу.</p>';
      return;
    }

    resultsContainer.innerHTML = '';
    results.forEach(item => {
      const row = document.createElement('div');
      row.className = 'p-3 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700/50 cursor-pointer transition flex items-start justify-between gap-3';
      row.onclick = () => {
        closeSearchModal();
        switchTab(item.tab);
        setTimeout(() => {
          const targetEl = document.getElementById(`topic-${item.id}`);
          if (targetEl) targetEl.scrollIntoView({ behavior: 'smooth' });
        }, 150);
      };

      row.innerHTML = `
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-[10px] px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-500/30 font-medium">${item.type}</span>
            <h4 class="text-sm font-bold text-white">${item.title}</h4>
          </div>
          <p class="text-xs text-slate-400 mt-1">${item.snippet}</p>
        </div>
        <i data-lucide="arrow-right" class="w-4 h-4 text-slate-500 flex-shrink-0 mt-1"></i>
      `;
      resultsContainer.appendChild(row);
    });

    lucide.createIcons();
  } catch (err) {
    console.error('Ошибка поиска:', err);
  }
}

// Helpers
function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatMarkdownContent(raw) {
  if (!raw) return '';
  // Basic markdown conversion for headers, code fences, bold, and tables
  let html = raw;

  // Code blocks with language
  html = html.replace(/```([a-zA-Z0-9_\-]+)?\n([\s\S]*?)```/g, (match, lang, code) => {
    const l = lang || 'python';
    return `<pre class="language-${l}"><code class="language-${l}">${escapeHtml(code.trim())}</code></pre>`;
  });

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="bg-slate-900 px-1.5 py-0.5 rounded text-sky-300 font-mono text-xs">$1</code>');

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h4 class="text-base font-bold text-white mt-4 mb-2">$1</h4>');
  html = html.replace(/^#### (.*$)/gim, '<h5 class="text-sm font-bold text-sky-300 mt-3 mb-1.5">$1</h5>');

  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');

  return html;
}

// --- TAB: AI SCOUT ---
async function loadAiSuggestions() {
  try {
    const res = await fetch('/api/ai/suggestions');
    const suggestions = await res.json();
    const container = document.getElementById('ai-suggestions-chips');
    if (!container) return;
    container.innerHTML = '';

    suggestions.forEach(item => {
      const chip = document.createElement('button');
      chip.className = 'px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/60 transition flex items-center gap-1.5';
      chip.onclick = () => setAiScoutQuery(item.query);
      chip.innerText = item.label;
      container.appendChild(chip);
    });
  } catch (err) {
    console.error('Ошибка загрузки подсказок AI:', err);
  }
}

function toggleLlmConfigDrawer() {
  const panel = document.getElementById('llm-config-panel');
  if (panel) {
    panel.classList.toggle('hidden');
  }
}

function setAiScoutQuery(query) {
  const input = document.getElementById('ai-scout-input');
  if (input) {
    input.value = query;
    performAiScoutSearch();
  }
}

async function performAiScoutSearch() {
  const input = document.getElementById('ai-scout-input');
  const query = input.value.trim();
  const mode = document.getElementById('ai-scout-mode').value;
  const resultsContainer = document.getElementById('ai-scout-results');
  const btn = document.getElementById('ai-scout-btn');

  if (!query) {
    alert('Пожалуйста, введите тему или задачу для поиска');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>ИИ анализирует...</span>';
  lucide.createIcons();

  resultsContainer.innerHTML = `
    <div class="p-12 text-center text-slate-400 space-y-3">
      <div class="inline-block p-4 rounded-full bg-emerald-500/10 border border-emerald-500/20 animate-pulse">
        <i data-lucide="bot" class="w-8 h-8 text-emerald-400"></i>
      </div>
      <h4 class="font-bold text-base text-white">ИИ ищет лучшие библиотеки и исходники...</h4>
      <p class="text-xs text-slate-500">Анализ темы: «${escapeHtml(query)}»</p>
    </div>
  `;
  lucide.createIcons();

  // Get LLM config if mode is LLM
  let llmConfig = null;
  if (mode === 'llm') {
    llmConfig = {
      endpoint: document.getElementById('ai-llm-endpoint').value.trim(),
      api_key: document.getElementById('ai-llm-key').value.trim(),
      model: document.getElementById('ai-llm-model').value.trim()
    };
  }

  try {
    const res = await fetch('/api/ai/scout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        mode: mode,
        llm_config: llmConfig
      })
    });

    const data = await res.json();
    renderAiScoutResults(data);
  } catch (err) {
    resultsContainer.innerHTML = `
      <div class="p-6 rounded-2xl bg-red-950/20 border border-red-500/30 text-red-300 text-sm">
        Ошибка при выполнении поиска: ${escapeHtml(err.message)}
      </div>
    `;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="sparkles" class="w-4 h-4"></i><span>Найти решения</span>';
    lucide.createIcons();
  }
}

function renderAiScoutResults(data) {
  const container = document.getElementById('ai-scout-results');
  container.innerHTML = '';

  // 1. AI Summary Header
  const summaryCard = document.createElement('div');
  summaryCard.className = 'glass-panel rounded-2xl p-5 border border-emerald-500/30 bg-gradient-to-r from-emerald-950/20 via-slate-900/50 to-slate-900/50 space-y-2';
  summaryCard.innerHTML = `
    <div class="flex items-center space-x-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
      <i data-lucide="sparkles" class="w-4 h-4"></i>
      <span>Вердикт ИИ-Ассистента</span>
    </div>
    <h3 class="text-lg font-bold text-white">${data.topic_title || 'Рекомендации по вашему запросу'}</h3>
    <p class="text-sm text-slate-300 leading-relaxed">${escapeHtml(data.summary)}</p>
  `;
  container.appendChild(summaryCard);

  // 2. Libraries Cards
  if (data.libraries && data.libraries.length > 0) {
    const libsGrid = document.createElement('div');
    libsGrid.className = 'grid grid-cols-1 lg:grid-cols-2 gap-6';

    data.libraries.forEach(lib => {
      const card = document.createElement('div');
      card.className = 'glass-card rounded-2xl p-6 border border-slate-800 space-y-4 flex flex-col justify-between';

      card.innerHTML = `
        <div class="space-y-4">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center space-x-2">
                <h4 class="font-bold text-lg text-white">${escapeHtml(lib.name)}</h4>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">${escapeHtml(lib.badge || 'Рекомендовано')}</span>
              </div>
              <p class="text-xs text-slate-400 mt-1 leading-relaxed">${escapeHtml(lib.description)}</p>
            </div>
          </div>

          <!-- Direct links -->
          <div class="flex flex-wrap gap-2 text-xs">
            ${lib.docs ? `<a href="${lib.docs}" target="_blank" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-400 flex items-center gap-1 border border-slate-700 transition"><i data-lucide="book-open" class="w-3.5 h-3.5"></i> Документация</a>` : ''}
            ${lib.github ? `<a href="${lib.github}" target="_blank" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1 border border-slate-700 transition"><i data-lucide="github" class="w-3.5 h-3.5"></i> GitHub</a>` : ''}
            ${lib.pypi ? `<a href="https://pypi.org/project/${lib.pypi}/" target="_blank" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-amber-400 flex items-center gap-1 border border-slate-700 transition"><i data-lucide="package" class="w-3.5 h-3.5"></i> PyPI</a>` : ''}
          </div>

          <!-- Install snippet -->
          <div class="space-y-1.5">
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span>Установка:</span>
              <button onclick="copyToClipboard('${escapeHtml(lib.install)}')" class="text-sky-400 hover:text-sky-300 flex items-center gap-1">
                <i data-lucide="copy" class="w-3.5 h-3.5"></i> Копировать
              </button>
            </div>
            <div class="bg-black/70 rounded-lg p-2.5 border border-slate-800 font-mono text-xs text-emerald-400 select-all">
              ${escapeHtml(lib.install)}
            </div>
          </div>

          <!-- Code Snippet -->
          ${lib.code ? `
          <div class="space-y-1.5">
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span>Пример использования:</span>
              <div class="flex space-x-2">
                <button onclick="sendToPlayground(${JSON.stringify(lib.code).replace(/"/g, '&quot;')})" class="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
                  <i data-lucide="play" class="w-3.5 h-3.5"></i> В песочницу
                </button>
                <button onclick="copyToClipboard(${JSON.stringify(lib.code).replace(/"/g, '&quot;')})" class="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1">
                  <i data-lucide="copy" class="w-3.5 h-3.5"></i> Копировать
                </button>
              </div>
            </div>
            <div class="max-h-48 overflow-y-auto rounded-lg border border-slate-800">
              <pre class="m-0"><code class="language-python">${escapeHtml(lib.code)}</code></pre>
            </div>
          </div>` : ''}
        </div>
      `;
      libsGrid.appendChild(card);
    });

    container.appendChild(libsGrid);
  }

  // 3. Official sources & articles
  if (data.sources && data.sources.length > 0) {
    const sourcesCard = document.createElement('div');
    sourcesCard.className = 'glass-panel rounded-2xl p-5 border border-slate-800 space-y-3';
    
    const linksHtml = data.sources.map(s => `
      <a href="${s.url}" target="_blank" class="p-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 flex items-center justify-between transition text-xs text-slate-300 hover:text-white">
        <span class="font-medium flex items-center gap-2">
          <i data-lucide="link" class="w-3.5 h-3.5 text-sky-400"></i>
          ${escapeHtml(s.title)}
        </span>
        <i data-lucide="external-link" class="w-3.5 h-3.5 text-slate-500"></i>
      </a>
    `).join('');

    sourcesCard.innerHTML = `
      <h4 class="text-sm font-bold text-white flex items-center gap-2">
        <i data-lucide="globe" class="w-4 h-4 text-sky-400"></i>
        Полезные ссылки и источники по теме:
      </h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        ${linksHtml}
      </div>
    `;
    container.appendChild(sourcesCard);
  }

  Prism.highlightAll();
  lucide.createIcons();
}

// --- TAB: PRACTICE QUESTS & GAMIFICATION & REALTIME AI MENTOR ---
let allPracticeTasks = [];
let currentPracticeTask = null;
let userProfile = null;
let mentorDebounceTimer = null;
let lastMentorSuggestedFix = null;

async function loadUserProfile() {
  try {
    const res = await fetch('/api/practice/profile', {
      headers: getAuthHeaders()
    });
    userProfile = await res.json();
    
    // Update Header Widget
    const starsElem = document.getElementById('header-stars-count');
    const titleElem = document.getElementById('header-active-title');
    const shopStarsElem = document.getElementById('shop-stars-balance');
    
    if (starsElem) starsElem.innerText = userProfile.stars || 0;
    if (titleElem) titleElem.innerText = userProfile.active_title ? userProfile.active_title.name : '🐍 Начинающий Змеелов';
    if (shopStarsElem) shopStarsElem.innerText = userProfile.stars || 0;

    if (currentUser) {
      currentUser.stars = userProfile.stars;
      currentUser.active_title = userProfile.active_title;
      currentUser.active_title_id = userProfile.active_title?.id;
      if (userProfile.role) {
        currentUser.role = userProfile.role;
        currentUser.is_developer = (userProfile.role === 'creator' || userProfile.role === 'admin' || (currentUser.username || '').toLowerCase() === 'chevels');
      }
      if (currentUser.username) {
        window.allUsersRoleCache = window.allUsersRoleCache || {};
        window.allUsersRoleCache[currentUser.username.toLowerCase()] = currentUser.role || 'user';
      }
      updateHeaderUserWidget(currentUser);
    }
  } catch (err) {
    console.error('Ошибка загрузки профиля:', err);
  }
}

async function loadPracticeTasks() {
  try {
    const res = await fetch('/api/practice/tasks', {
      headers: getAuthHeaders()
    });
    allPracticeTasks = await res.json();
    renderPracticeTasks(allPracticeTasks);

    if (allPracticeTasks.length > 0 && !currentPracticeTask) {
      selectPracticeTask(allPracticeTasks[0].id);
    }
  } catch (err) {
    console.error('Ошибка загрузки заданий практики:', err);
  }
}

function filterPracticeTasks(diff) {
  // Update buttons
  const container = document.getElementById('practice-filter-btns');
  if (container) {
    container.querySelectorAll('button').forEach(btn => {
      btn.className = 'px-2 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-slate-200';
    });
    event.target.className = 'px-2 py-0.5 rounded bg-sky-500/20 text-sky-400 border border-sky-500/30';
  }

  if (diff === 'all') {
    renderPracticeTasks(allPracticeTasks);
  } else {
    const filtered = allPracticeTasks.filter(t => t.difficulty === diff);
    renderPracticeTasks(filtered);
  }
}

function renderPracticeTasks(tasks) {
  const container = document.getElementById('practice-tasks-list');
  if (!container) return;
  container.innerHTML = '';

  tasks.forEach(task => {
    const isSelected = currentPracticeTask && currentPracticeTask.id === task.id;
    const item = document.createElement('div');
    item.id = `practice-task-item-${task.id}`;
    item.className = `p-3 rounded-xl border cursor-pointer transition flex items-center justify-between gap-2 ${isSelected ? 'bg-sky-950/40 border-sky-500/50 shadow-md' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'}`;
    item.onclick = () => selectPracticeTask(task.id);

    const diffBadgeColor = task.difficulty === 'Junior' ? 'text-emerald-400 bg-emerald-950/30 border-emerald-500/30' :
                           task.difficulty === 'Middle' ? 'text-sky-400 bg-sky-950/30 border-sky-500/30' :
                           task.difficulty === 'Senior' ? 'text-purple-400 bg-purple-950/30 border-purple-500/30' :
                           'text-amber-400 bg-amber-950/30 border-amber-500/30';

    item.innerHTML = `
      <div class="flex items-center space-x-2.5 overflow-hidden">
        <span class="flex-shrink-0 text-sm">${task.is_solved ? '✅' : '📌'}</span>
        <div class="truncate">
          <h5 class="text-xs font-bold text-white truncate">${escapeHtml(task.title)}</h5>
          <span class="text-[10px] text-slate-400 truncate block">${escapeHtml(task.category)}</span>
        </div>
      </div>
      <div class="flex items-center space-x-2 flex-shrink-0">
        <span class="text-[10px] px-1.5 py-0.5 rounded font-mono font-medium border ${diffBadgeColor}">${task.difficulty}</span>
        <span class="text-xs font-bold text-amber-400 flex items-center gap-0.5">
          <i data-lucide="star" class="w-3 h-3 fill-amber-400"></i> +${task.reward_stars}
        </span>
      </div>
    `;
    container.appendChild(item);
  });

  lucide.createIcons();
}

function selectPracticeTask(taskId) {
  const task = allPracticeTasks.find(t => t.id === taskId);
  if (!task) return;
  currentPracticeTask = task;

  // Update list active card style
  allPracticeTasks.forEach(t => {
    const el = document.getElementById(`practice-task-item-${t.id}`);
    if (el) {
      if (t.id === taskId) {
        el.className = 'p-3 rounded-xl border cursor-pointer transition flex items-center justify-between gap-2 bg-sky-950/40 border-sky-500/50 shadow-md';
      } else {
        el.className = 'p-3 rounded-xl border cursor-pointer transition flex items-center justify-between gap-2 bg-slate-900/60 border-slate-800 hover:border-slate-700';
      }
    }
  });

  // Update Task detail card
  document.getElementById('task-detail-title').innerText = task.title;
  document.getElementById('task-detail-category').innerText = task.category;
  document.getElementById('task-detail-reward').innerText = `+${task.reward_stars} ⭐`;
  document.getElementById('task-detail-desc').innerText = task.description;

  // Set editor starter code
  const editor = document.getElementById('practice-code-editor');
  editor.value = task.starter_code;

  // Clear test results
  document.getElementById('practice-test-results').innerHTML = '<p class="text-slate-500 text-center py-4">Нажмите «Проверить решение» для запуска тестов.</p>';
  document.getElementById('tests-status-badge').innerText = 'Тесты готовы к запуску';
  document.getElementById('tests-status-badge').className = 'text-[11px] font-mono text-slate-400';

  // Trigger instant mentor check
  onPracticeCodeInput();
}

function resetPracticeCode() {
  if (currentPracticeTask) {
    document.getElementById('practice-code-editor').value = currentPracticeTask.starter_code;
    onPracticeCodeInput();
  }
}

// --- REAL-TIME AI ERROR MENTOR LISTENER ---
function onPracticeCodeInput() {
  clearTimeout(mentorDebounceTimer);
  mentorDebounceTimer = setTimeout(async () => {
    const code = document.getElementById('practice-code-editor').value;
    await inspectCodeWithMentor(code);
  }, 350);
}

async function inspectCodeWithMentor(code) {
  try {
    const res = await fetch('/api/mentor/inspect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code })
    });
    const report = await res.json();
    renderMentorReport(report);
  } catch (err) {
    console.error('Ошибка проверки ментора:', err);
  }
}

function renderMentorReport(report) {
  const beacon = document.getElementById('mentor-beacon');
  const beaconText = document.getElementById('mentor-beacon-text');
  const msgElem = document.getElementById('mentor-message');
  const lineTag = document.getElementById('mentor-line-tag');
  const solutionBox = document.getElementById('mentor-solution-box');
  const hintElem = document.getElementById('mentor-hint');
  const applyBtn = document.getElementById('mentor-apply-btn');

  lastMentorSuggestedFix = report.suggested_fix;

  if (report.status === 'clean') {
    beacon.className = 'flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-semibold';
    beacon.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span><span>Код чист</span>';
    msgElem.innerText = report.message;
    lineTag.classList.add('hidden');
    solutionBox.classList.add('hidden');
  } else if (report.status === 'warning') {
    beacon.className = 'flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] font-semibold';
    beacon.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-400"></span><span>Внимание</span>';
    msgElem.innerText = report.message;
    lineTag.classList.remove('hidden');
    lineTag.innerText = `Строка ${report.line}`;
    lineTag.className = 'text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 font-mono border border-amber-500/30';
    
    if (report.hint) {
      solutionBox.classList.remove('hidden');
      hintElem.innerText = report.hint;
    } else {
      solutionBox.classList.add('hidden');
    }
    applyBtn.classList.add('hidden');
  } else {
    // Error
    beacon.className = 'flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 text-[10px] font-semibold';
    beacon.innerHTML = '<span class="w-2 h-2 rounded-full bg-red-400 animate-ping"></span><span>Ошибка</span>';
    msgElem.innerText = report.message;
    
    if (report.line) {
      lineTag.classList.remove('hidden');
      lineTag.innerText = `Строка ${report.line}`;
      lineTag.className = 'text-[10px] px-1.5 py-0.5 rounded bg-red-950 text-red-400 font-mono border border-red-500/30';
    } else {
      lineTag.classList.add('hidden');
    }

    if (report.hint) {
      solutionBox.classList.remove('hidden');
      hintElem.innerText = report.hint;
      if (report.suggested_fix) {
        applyBtn.classList.remove('hidden');
      } else {
        applyBtn.classList.add('hidden');
      }
    } else {
      solutionBox.classList.add('hidden');
    }
  }
}

function applyMentorFix() {
  if (lastMentorSuggestedFix) {
    document.getElementById('practice-code-editor').value = lastMentorSuggestedFix;
    showToast('Исправление применено! 🔧');
    onPracticeCodeInput();
  }
}

// --- SUBMIT PRACTICE SOLUTION ---
async function submitPracticeSolution() {
  if (!currentPracticeTask) return;
  const code = document.getElementById('practice-code-editor').value;
  const btn = document.getElementById('submit-solution-btn');
  const resultsContainer = document.getElementById('practice-test-results');
  const badge = document.getElementById('tests-status-badge');

  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Проверка...</span>';
  lucide.createIcons();

  resultsContainer.innerHTML = '<p class="text-slate-400 text-center py-4 animate-pulse">Выполнение тест-кейсов в изолированной среде...</p>';

  try {
    const res = await fetch('/api/practice/submit', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        task_id: currentPracticeTask.id,
        code: code
      })
    });

    const report = await res.json();
    
    if (report.success) {
      badge.innerText = `✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ (${report.execution_time_ms} мс)`;
      badge.className = 'text-[11px] font-mono text-emerald-400 font-bold';

      if (report.award_info && report.award_info.is_first_solve) {
        showToast(`🎉 Потрясающе! Вы заработали +${report.award_info.awarded_stars} ⭐!`);
        await loadUserProfile();
        await loadPracticeTasks();
        await loadDailyQuests();
        if (currentTab === 'leaderboard') loadLeaderboard();
      } else {
        showToast('Задание успешно решено повторно! 👍');
        await loadDailyQuests();
      }
    } else {
      badge.innerText = '❌ ОШИБКА В ТЕСТАХ';
      badge.className = 'text-[11px] font-mono text-red-400 font-bold';
    }

    // Render individual test case rows
    resultsContainer.innerHTML = '';
    if (report.test_results && report.test_results.length > 0) {
      report.test_results.forEach((tc, idx) => {
        const row = document.createElement('div');
        row.className = `p-2.5 rounded-lg border flex items-center justify-between text-xs ${tc.passed ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-red-950/20 border-red-500/30 text-red-300'}`;
        row.innerHTML = `
          <div class="flex items-center space-x-2">
            <span>${tc.passed ? '✅' : '❌'}</span>
            <span class="font-bold">${escapeHtml(tc.name || `Тест #${idx+1}`)}</span>
          </div>
          <div class="font-mono text-[11px] text-slate-400">
            Ожидалось: <span class="text-slate-200">${escapeHtml(JSON.stringify(tc.expected))}</span> | Получено: <span class="${tc.passed ? 'text-emerald-400' : 'text-red-400 font-bold'}">${escapeHtml(JSON.stringify(tc.actual))}</span>
          </div>
        `;
        resultsContainer.appendChild(row);
      });
    } else {
      resultsContainer.innerHTML = `<div class="p-3 bg-red-950/20 border border-red-500/30 rounded-lg text-red-300">${escapeHtml(report.summary)}</div>`;
    }

  } catch (err) {
    resultsContainer.innerHTML = `<div class="p-3 bg-red-950/20 border border-red-500/30 rounded-lg text-red-300">Ошибка отправки: ${escapeHtml(err.message)}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="play" class="w-3.5 h-3.5"></i><span>Проверить решение</span>';
    lucide.createIcons();
  }
}

// --- TITLE SHOP MODAL ---
async function openTitleShopModal() {
  await loadUserProfile();
  const modal = document.getElementById('title-shop-modal');
  const container = document.getElementById('shop-titles-container');
  modal.classList.remove('hidden');

  container.innerHTML = '';
  userProfile.shop_titles.forEach(t => {
    const card = document.createElement('div');
    card.className = `p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${t.color}`;

    let actionBtnHtml = '';
    if (t.is_active) {
      actionBtnHtml = '<span class="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-bold border border-emerald-500/30 flex items-center gap-1">✓ Экипирован</span>';
    } else if (t.is_unlocked) {
      actionBtnHtml = `<button onclick="equipTitle('${t.id}')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold border border-slate-600 transition">Экипировать</button>`;
    } else if (t.can_afford) {
      actionBtnHtml = `<button onclick="buyTitle('${t.id}')" class="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs shadow-md transition flex items-center gap-1"><i data-lucide="star" class="w-3.5 h-3.5 fill-black"></i> Купить (${t.cost_stars} ⭐)</button>`;
    } else {
      actionBtnHtml = `<button disabled class="px-3 py-1.5 rounded-lg bg-slate-800/40 text-slate-500 text-xs font-medium cursor-not-allowed border border-slate-800">Нужно ${t.cost_stars} ⭐</button>`;
    }

    card.innerHTML = `
      <div class="space-y-1">
        <div class="flex items-center space-x-2">
          <h4 class="font-bold text-base text-white">${t.name}</h4>
          <span class="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-black/40">${t.rarity}</span>
        </div>
        <p class="text-xs text-slate-300 leading-relaxed">${t.description}</p>
      </div>
      <div class="flex-shrink-0">${actionBtnHtml}</div>
    `;
    container.appendChild(card);
  });

  lucide.createIcons();
}

function closeTitleShopModal() {
  document.getElementById('title-shop-modal').classList.add('hidden');
}

async function buyTitle(titleId) {
  try {
    const res = await fetch('/api/practice/buy-title', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title_id: titleId })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message);
      await loadUserProfile();
      openTitleShopModal();
      if (currentTab === 'leaderboard') loadLeaderboard();
    } else {
      alert(data.detail || 'Не удалось купить титул');
    }
  } catch (err) {
    alert(err.message);
  }
}

async function equipTitle(titleId) {
  try {
    const res = await fetch('/api/practice/set-active-title', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title_id: titleId })
    });
    if (res.ok) {
      showToast('Титул успешно экипирован! 👑');
      await loadUserProfile();
      openTitleShopModal();
      if (currentTab === 'leaderboard') loadLeaderboard();
    }
  } catch (err) {
    alert(err.message);
  }
}

// --- AI TASK GENERATOR MODAL ---
function generateAiPracticeTaskModal() {
  document.getElementById('ai-task-gen-modal').classList.remove('hidden');
}

function closeAiTaskGenModal() {
  document.getElementById('ai-task-gen-modal').classList.add('hidden');
}

async function confirmGenerateAiTask() {
  const topic = document.getElementById('ai-gen-topic').value.trim() || 'алгоритмы';
  const difficulty = document.getElementById('ai-gen-difficulty').value;
  const btn = document.getElementById('ai-gen-submit-btn');

  btn.disabled = true;
  btn.innerText = 'Генерация...';

  try {
    const res = await fetch('/api/practice/generate-task', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic, difficulty: difficulty })
    });
    const newTask = await res.json();
    
    // Add to task list and select
    allPracticeTasks.unshift(newTask);
    renderPracticeTasks(allPracticeTasks);
    selectPracticeTask(newTask.id);
    closeAiTaskGenModal();
    showToast(`ИИ-квест «${newTask.title}» создан! 🚀`);
  } catch (err) {
    alert(`Ошибка генерации: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Создать квест';
  }
}

// --- LIBRARY TASK RANDOMIZER ---
async function generateRandomLibraryTask() {
  const libSelect = document.getElementById('practice-library-select');
  const diffSelect = document.getElementById('practice-diff-select');
  const btn = document.getElementById('btn-gen-library-task');

  const library = libSelect ? libSelect.value : 'fastapi';
  const difficulty = diffSelect ? diffSelect.value : null;

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Генерация...</span>';
    lucide.createIcons();
  }

  try {
    const res = await fetch('/api/practice/random-by-library', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ library: library, difficulty: difficulty || null })
    });
    const data = await res.json();
    if (data.success && data.task) {
      const task = data.task;
      // Prepend to practice list
      const existingIdx = allPracticeTasks.findIndex(t => t.id === task.id);
      if (existingIdx === -1) {
        allPracticeTasks.unshift(task);
      }
      renderPracticeTasks(allPracticeTasks);
      selectPracticeTask(task.id);
      showToast(`🎲 Создана задача по ${library.toUpperCase()}! Награда: ⭐ ${task.reward_stars} звезд.`);
    } else {
      showToast('Не удалось сгенерировать задачу');
    }
  } catch (err) {
    alert(`Ошибка генератора: ${err.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="shuffle" class="w-3.5 h-3.5"></i><span>🎲 Сгенерировать задачу</span>';
      lucide.createIcons();
    }
  }
}

// --- VS CODE BRIDGE SERVICE ---
let currentVSCodeFilePath = 'run.py';
let lastVSCodeFixCode = null;
let vsCodeWatchTimer = null;

async function inspectVSCodeFile(silent = false) {
  const pathInput = document.getElementById('vscode-file-input');
  const filePath = (pathInput ? pathInput.value.trim() : '') || 'run.py';
  currentVSCodeFilePath = filePath;

  const btn = document.getElementById('btn-inspect-vscode-file');
  if (!silent && btn) {
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Анализ...</span>';
    lucide.createIcons();
  }

  try {
    const res = await fetch('/api/vscode/inspect-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath })
    });

    if (!res.ok) {
      if (!silent) {
        showToast('Файл не найден на сервере');
      }
      return;
    }

    const data = await res.json();

    const infoBar = document.getElementById('vscode-file-info-bar');
    const nameDisplay = document.getElementById('vscode-file-name-display');
    const sizeDisplay = document.getElementById('vscode-file-size-display');
    const preview = document.getElementById('vscode-code-preview');
    const counter = document.getElementById('vscode-issues-counter');
    const issuesContainer = document.getElementById('vscode-issues-container');
    const saveFixBtn = document.getElementById('btn-save-disk-fix');

    if (!data.success) {
      if (!silent) {
        if (counter) counter.innerText = 'Ошибка открытия файла';
        if (issuesContainer) {
          issuesContainer.innerHTML = `<div class="p-3 bg-red-950/30 border border-red-500/30 rounded-xl text-red-300">${escapeHtml(data.error || 'Файл не найден')}</div>`;
        }
      }
      return;
    }

    if (infoBar) infoBar.classList.remove('hidden');
    if (nameDisplay) nameDisplay.innerText = data.file_name;
    if (sizeDisplay) sizeDisplay.innerText = `(${(data.file_size / 1024).toFixed(1)} KB)`;
    if (preview && (!preview.value || preview.dataset.autoSync !== 'false')) {
      preview.value = data.code;
    }

    const issues = (data.analysis && data.analysis.issues) ? data.analysis.issues : [];
    if (counter) {
      counter.innerText = issues.length === 0 ? '✨ Ошибок не обнаружено' : `Найдено проблем: ${issues.length}`;
      counter.className = issues.length === 0 ? 'text-emerald-400 font-mono text-[11px] font-bold' : 'text-amber-400 font-mono text-[11px] font-bold';
    }

    if (issuesContainer) {
      issuesContainer.innerHTML = '';
      if (issues.length === 0) {
        issuesContainer.innerHTML = `
          <div class="p-3.5 bg-emerald-950/20 border border-emerald-500/30 rounded-xl text-emerald-300 flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span>✨</span>
              <span class="font-bold">Код файла полностью чист и синтаксически корректен!</span>
            </div>
            <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 font-mono">AST OK</span>
          </div>
        `;
        if (saveFixBtn) saveFixBtn.classList.add('hidden');
      } else {
        issues.forEach((iss, idx) => {
          const card = document.createElement('div');
          const isErr = iss.severity === 'error';
          card.className = `p-3 rounded-xl border space-y-1.5 ${isErr ? 'bg-red-950/20 border-red-500/30' : 'bg-amber-950/20 border-amber-500/30'}`;
          card.innerHTML = `
            <div class="flex items-center justify-between">
              <span class="font-bold ${isErr ? 'text-red-400' : 'text-amber-400'} flex items-center gap-1.5">
                <span>${isErr ? '❌' : '⚠️'}</span>
                <span>${escapeHtml(iss.title)}</span>
              </span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-black/40 font-mono text-slate-300">Строка ${iss.line || 1}</span>
            </div>
            <p class="text-xs text-slate-300">${escapeHtml(iss.message)}</p>
            <div class="text-[11px] text-slate-400 bg-black/30 p-2 rounded-lg font-mono">💡 Совет: ${escapeHtml(iss.advice)}</div>
          `;
          issuesContainer.appendChild(card);
        });

        // If an auto-fix is provided in analysis
        if (data.analysis.fix_code && saveFixBtn) {
          lastVSCodeFixCode = data.analysis.fix_code;
          saveFixBtn.classList.remove('hidden');
        }
      }
    }

  } catch (err) {
    if (!silent) {
      showToast(`Проверка файла: ${err.message}`);
    }
  } finally {
    if (!silent && btn) {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="search" class="w-3.5 h-3.5"></i><span>Анализ</span>';
      lucide.createIcons();
    }
  }
}

async function scanVSCodeWorkspace() {
  const dirInput = document.getElementById('vscode-workspace-input');
  const workspaceDir = (dirInput ? dirInput.value.trim() : '') || '.';
  const btn = document.getElementById('btn-scan-workspace');
  const resultsContainer = document.getElementById('vscode-workspace-results');

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Сканирование...</span>';
    lucide.createIcons();
  }

  try {
    const res = await fetch('/api/vscode/inspect-workspace', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workspace_dir: workspaceDir, max_files: 30 })
    });

    if (!res.ok) {
      resultsContainer.innerHTML = `<div class="p-3 bg-slate-900/60 rounded-xl text-slate-400 text-xs text-center">Сканирование локального диска доступно при локальном запуске приложения.</div>`;
      return;
    }

    const data = await res.json();

    if (!data.success) {
      resultsContainer.innerHTML = `<div class="p-3 bg-red-950/30 border border-red-500/30 rounded-xl text-red-300 text-xs">${escapeHtml(data.error)}</div>`;
      return;
    }

    resultsContainer.innerHTML = '';
    if (data.files.length === 0) {
      resultsContainer.innerHTML = `<div class="p-3 bg-slate-900/60 rounded-xl text-slate-400 text-xs text-center">Python (.py) файлы не найдены в папке.</div>`;
      return;
    }

    data.files.forEach(f => {
      const item = document.createElement('div');
      const hasIssues = f.issues_count > 0;
      item.className = `p-2.5 rounded-xl border flex items-center justify-between text-xs cursor-pointer transition ${hasIssues ? 'bg-slate-900/90 border-amber-500/30 hover:border-amber-400' : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'}`;
      item.innerHTML = `
        <div class="flex items-center space-x-2">
          <span>${hasIssues ? '⚠️' : '✅'}</span>
          <span class="font-bold text-white font-mono">${escapeHtml(f.relative_path || f.file_name)}</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-[11px] ${hasIssues ? 'text-amber-400 font-bold' : 'text-emerald-400'}">${hasIssues ? `${f.issues_count} замечаний` : 'Чисто'}</span>
          <button onclick="loadVSCodeFileToInspector('${escapeHtml(f.file_path)}')" class="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 hover:bg-sky-500/30 text-[10px] font-semibold">Открыть</button>
        </div>
      `;
      resultsContainer.appendChild(item);
    });

  } catch (err) {
    resultsContainer.innerHTML = `<div class="p-3 bg-red-950/30 border border-red-500/30 rounded-xl text-red-300 text-xs">Ошибка: ${escapeHtml(err.message)}</div>`;
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i><span>Сканировать</span>';
      lucide.createIcons();
    }
  }
}

function loadVSCodeFileToInspector(filePath) {
  const input = document.getElementById('vscode-file-input');
  if (input) input.value = filePath;
  inspectVSCodeFile(false);
}

async function saveVSCodeFixToDisk() {
  if (!lastVSCodeFixCode || !currentVSCodeFilePath) {
    showToast('Нет готового исправления для сохранения');
    return;
  }

  try {
    const res = await fetch('/api/vscode/apply-fix', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: currentVSCodeFilePath, fixed_code: lastVSCodeFixCode })
    });
    const data = await res.json();
    if (data.success) {
      showToast('✅ Файл успешно сохранен на диске с автофиксом!');
      inspectVSCodeFile(false);
    } else {
      alert(`Не удалось сохранить: ${data.error}`);
    }
  } catch (err) {
    alert(err.message);
  }
}

function syncVSCodeToPlayground() {
  const preview = document.getElementById('vscode-code-preview');
  const playground = document.getElementById('playground-editor');
  if (preview && playground) {
    playground.value = preview.value;
    switchTab('playground');
    showToast('Код перенесен в интерактивную песочницу PyForge!');
  }
}

// Background auto-watcher for VS Code live inspection
setInterval(() => {
  if (currentTab === 'vscode') {
    const autoWatchCheck = document.getElementById('vscode-auto-watch');
    if (autoWatchCheck && autoWatchCheck.checked) {
      inspectVSCodeFile(true);
    }
  }
}, 2500);

// ==========================================
// --- AUTHENTICATION & USER PROFILE ---
// ==========================================

async function checkAuthState() {
  const token = getAuthToken();
  if (!token) {
    currentUser = null;
    updateHeaderUserWidget(null);
    return;
  }
  try {
    const res = await fetch('/api/auth/me', {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      currentUser = data.user;
      if (currentUser && currentUser.username) {
        window.allUsersRoleCache = window.allUsersRoleCache || {};
        window.allUsersRoleCache[currentUser.username.toLowerCase()] = currentUser.role || (currentUser.username.toLowerCase() === 'chevels' ? 'creator' : 'user');
      }
      updateHeaderUserWidget(currentUser);
    } else {
      localStorage.removeItem('pyforge_token');
      currentUser = null;
      updateHeaderUserWidget(null);
    }
  } catch (err) {
    console.error('Ошибка проверки токена:', err);
    updateHeaderUserWidget(null);
  }
}

function updateHeaderUserWidget(user) {
  const container = document.getElementById('user-header-auth-widget');
  const devHeaderBtn = document.getElementById('header-dev-panel-btn');
  if (devHeaderBtn) {
    if (user && isDeveloperUser(user)) {
      devHeaderBtn.classList.remove('hidden');
    } else {
      devHeaderBtn.classList.add('hidden');
    }
  }

  if (!container) return;

  if (user && user.username) {
    const avatar = user.avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${user.username}`;
    const displayName = user.display_name || user.username;
    const isDev = isDeveloperUser(user);
    const isCreator = (user.username || '').toLowerCase() === 'chevels' || user.role === 'creator';
    const role = getUserRole(user);
    const roleLabels = {
      creator: '👑 Создатель',
      admin: '⚡ Администратор',
      moderator: '🛡️ Модератор',
      vip: '⭐ VIP Профиль',
      mentor: '🧠 Эксперт & Ментор',
      user: 'Профиль & Аватар ⚙️'
    };
    const customRoleObj = (window.devLoadedRoles || []).find(r => r.id === role);
    const subLabel = customRoleObj ? `${customRoleObj.name}` : (roleLabels[role] || (isCreator ? '👑 Создатель' : 'Профиль & Аватар ⚙️'));
    const devBadge = getUserBadgeHtml(user);

    const borderClass = isCreator ? 'border-amber-500/60 shadow-md shadow-amber-500/10' :
                        role === 'admin' ? 'border-red-500/60 shadow-md shadow-red-500/10' :
                        role === 'moderator' ? 'border-emerald-500/60' :
                        role === 'vip' ? 'border-purple-500/60' :
                        role === 'mentor' ? 'border-cyan-500/60' :
                        role && role !== 'user' ? 'border-sky-500/60' :
                        'border-slate-700 hover:border-sky-500/50';

    const subColor = isCreator ? 'text-amber-300 font-semibold flex items-center gap-0.5' :
                     role === 'admin' ? 'text-red-300 font-bold' :
                     role === 'moderator' ? 'text-emerald-300 font-bold' :
                     role === 'vip' ? 'text-purple-300 font-bold' :
                     role === 'mentor' ? 'text-cyan-300 font-bold' :
                     role && role !== 'user' ? 'text-sky-300 font-bold' : 'text-slate-400';

    container.innerHTML = `
      <div class="flex items-center space-x-1.5 sm:space-x-2 pl-1">
        <button onclick="openProfileModal()" title="Настройки профиля и аватара" class="flex items-center space-x-2 px-2.5 py-1.5 rounded-xl bg-slate-800/90 hover:bg-slate-750 border ${borderClass} text-xs shadow-sm transition group">
          <div class="relative">
            <img src="${avatar}" class="w-6 h-6 rounded-lg border ${isCreator ? 'border-amber-400' : 'border-slate-600'} bg-slate-900 object-cover flex-shrink-0" alt="${escapeHtml(displayName)}">
            ${isCreator ? '<span class="absolute -top-1 -right-1 flex h-2.5 w-2.5"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span></span>' : ''}
          </div>
          <div class="text-left hidden sm:block">
            <div class="flex items-center gap-1 font-bold text-white group-hover:text-sky-300 transition max-w-[125px] truncate leading-tight">
              <span>${escapeHtml(displayName)}</span>
              ${devBadge}
            </div>
            <div class="text-[9px] ${subColor}">${subLabel}</div>
          </div>
          <i data-lucide="chevron-down" class="w-3 h-3 text-slate-400 group-hover:text-white transition ml-0.5"></i>
        </button>
        <button onclick="logoutUser()" title="Выйти из аккаунта" class="p-2 rounded-xl bg-slate-800/80 hover:bg-rose-500/20 text-slate-400 hover:text-rose-300 border border-slate-700 transition">
          <i data-lucide="log-out" class="w-3.5 h-3.5"></i>
        </button>
      </div>
    `;
  } else {
    container.innerHTML = `
      <button onclick="openAuthModal('login')" class="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-xs font-semibold text-white shadow-md shadow-sky-600/20 transition">
        <i data-lucide="user" class="w-3.5 h-3.5"></i>
        <span>Войти / Регистрация</span>
      </button>
    `;
  }
  lucide.createIcons();
}

function openAuthModal(tab = 'login') {
  const modal = document.getElementById('auth-modal');
  if (modal) {
    modal.classList.remove('hidden');
    switchAuthTab(tab);
    clearAuthError();
  }
}

function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.classList.add('hidden');
}

function switchAuthTab(tab) {
  const tabLogin = document.getElementById('auth-tab-login');
  const tabReg = document.getElementById('auth-tab-register');
  const formLogin = document.getElementById('auth-login-form');
  const formReg = document.getElementById('auth-register-form');
  clearAuthError();

  if (tab === 'login') {
    tabLogin.className = 'flex-1 py-2 text-xs font-bold rounded-lg transition bg-sky-600 text-white shadow';
    tabReg.className = 'flex-1 py-2 text-xs font-bold rounded-lg transition text-slate-400 hover:text-white';
    formLogin.classList.remove('hidden');
    formReg.classList.add('hidden');
  } else {
    tabReg.className = 'flex-1 py-2 text-xs font-bold rounded-lg transition bg-indigo-600 text-white shadow';
    tabLogin.className = 'flex-1 py-2 text-xs font-bold rounded-lg transition text-slate-400 hover:text-white';
    formReg.classList.remove('hidden');
    formLogin.classList.add('hidden');
  }
}

function showAuthError(msg) {
  const box = document.getElementById('auth-error-box');
  const txt = document.getElementById('auth-error-msg');
  if (box && txt) {
    txt.innerText = msg;
    box.classList.remove('hidden');
  }
}

function clearAuthError() {
  const box = document.getElementById('auth-error-box');
  if (box) box.classList.add('hidden');
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  const username = document.getElementById('auth-login-username').value.trim();
  const password = document.getElementById('auth-login-password').value.trim();
  const btn = document.getElementById('auth-login-btn');

  if (!username || !password) {
    showAuthError('Заполните все поля');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Вход...</span>';
  lucide.createIcons();

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      showAuthError(data.detail || 'Неверный логин или пароль');
      return;
    }

    localStorage.setItem('pyforge_token', data.token);
    currentUser = data.user;
    updateHeaderUserWidget(currentUser);
    closeAuthModal();
    showToast(`С возвращением, ${currentUser.display_name || currentUser.username}! 👋`);
    await loadUserProfile();
    await loadPracticeTasks();
    await loadDailyQuests();
    if (currentTab === 'leaderboard') loadLeaderboard();
  } catch (err) {
    showAuthError(err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>Войти</span><i data-lucide="arrow-right" class="w-4 h-4"></i>';
    lucide.createIcons();
  }
}

async function handleRegisterSubmit(event) {
  event.preventDefault();
  const username = document.getElementById('auth-reg-username').value.trim();
  const displayName = document.getElementById('auth-reg-displayname').value.trim();
  const password = document.getElementById('auth-reg-password').value.trim();
  const btn = document.getElementById('auth-reg-btn');

  if (!username || !password) {
    showAuthError('Заполните имя пользователя и пароль');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Регистрация...</span>';
  lucide.createIcons();

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, display_name: displayName || username })
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      showAuthError(data.detail || 'Ошибка регистрации');
      return;
    }

    localStorage.setItem('pyforge_token', data.token);
    currentUser = data.user;
    updateHeaderUserWidget(currentUser);
    closeAuthModal();
    showToast(`Добро пожаловать в PyForge, ${currentUser.display_name || currentUser.username}! 🚀`);
    await loadUserProfile();
    await loadPracticeTasks();
    await loadDailyQuests();
    if (currentTab === 'leaderboard') loadLeaderboard();
  } catch (err) {
    showAuthError(err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>Создать аккаунт</span><i data-lucide="sparkles" class="w-4 h-4"></i>';
    lucide.createIcons();
  }
}

async function logoutUser() {
  const token = getAuthToken();
  if (token) {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ token })
      });
    } catch (e) {}
  }
  localStorage.removeItem('pyforge_token');
  currentUser = null;
  updateHeaderUserWidget(null);
  closeProfileModal();
  showToast('Вы успешно вышли из аккаунта');
  await loadUserProfile();
  await loadPracticeTasks();
  await loadDailyQuests();
  if (currentTab === 'leaderboard') loadLeaderboard();
}

// --- PROFILE SETTINGS & AVATAR STUDIO MODAL ---

let currentAvatarMode = 'upload'; // 'upload' | 'preset' | 'url'
let currentAvatarStyle = 'bottts';
let currentAvatarSeed = '';
let currentCustomAvatarData = null; // Base64 Data URL or direct image URL

function setAvatarMode(mode) {
  currentAvatarMode = mode;

  // Buttons
  const uploadBtn = document.getElementById('avatar-mode-upload-btn');
  const presetBtn = document.getElementById('avatar-mode-preset-btn');
  const urlBtn = document.getElementById('avatar-mode-url-btn');

  const tabUpload = document.getElementById('avatar-tab-upload');
  const tabPreset = document.getElementById('avatar-tab-preset');
  const tabUrl = document.getElementById('avatar-tab-url');

  if (uploadBtn) uploadBtn.className = mode === 'upload' ? 'px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-sky-600 text-white shadow-sm transition flex items-center gap-1' : 'px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-transparent text-slate-400 hover:text-slate-200 transition flex items-center gap-1';
  if (presetBtn) presetBtn.className = mode === 'preset' ? 'px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-sky-600 text-white shadow-sm transition flex items-center gap-1' : 'px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-transparent text-slate-400 hover:text-slate-200 transition flex items-center gap-1';
  if (urlBtn) urlBtn.className = mode === 'url' ? 'px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-sky-600 text-white shadow-sm transition flex items-center gap-1' : 'px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-transparent text-slate-400 hover:text-slate-200 transition flex items-center gap-1';

  // Tabs
  if (tabUpload) tabUpload.classList.toggle('hidden', mode !== 'upload');
  if (tabPreset) tabPreset.classList.toggle('hidden', mode !== 'preset');
  if (tabUrl) tabUrl.classList.toggle('hidden', mode !== 'url');

  // Update preview according to selected mode
  if (mode === 'upload') {
    if (currentCustomAvatarData) {
      updateAvatarPreview(currentCustomAvatarData);
    } else {
      updateAvatarPreview(currentUser?.avatar || buildAvatarUrl('bottts', currentUser?.username || 'user'));
    }
  } else if (mode === 'preset') {
    const seed = document.getElementById('profile-avatar-seed-input')?.value.trim() || currentAvatarSeed || currentUser?.username || 'user';
    updateAvatarPreview(buildAvatarUrl(currentAvatarStyle, seed));
  } else if (mode === 'url') {
    const url = document.getElementById('profile-avatar-url-input')?.value.trim();
    if (url) {
      updateAvatarPreview(url);
    }
  }
  lucide.createIcons();
}

function handleAvatarFileSelect(event) {
  const file = event.target.files && event.target.files[0];
  if (file) {
    processAvatarFile(file);
  }
}

function processAvatarFile(file) {
  if (!file.type.startsWith('image/')) {
    alert('Пожалуйста, выберите файл изображения (PNG, JPG, WEBP, GIF)');
    return;
  }

  // Max 5MB raw
  if (file.size > 5 * 1024 * 1024) {
    alert('Размер файла превышает 5 МБ. Пожалуйста, выберите файл меньшего размера.');
    return;
  }

  const reader = new FileReader();
  reader.onload = function(e) {
    const rawDataUrl = e.target.result;
    const img = new Image();
    img.onload = function() {
      // Resize to max 256x256 for fast transmission and lightweight storage
      const maxDim = 256;
      let width = img.width;
      let height = img.height;

      if (width > height) {
        if (width > maxDim) {
          height = Math.round((height * maxDim) / width);
          width = maxDim;
        }
      } else {
        if (height > maxDim) {
          width = Math.round((width * maxDim) / height);
          height = maxDim;
        }
      }

      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, width, height);

      const mimeType = file.type === 'image/png' ? 'image/png' : 'image/jpeg';
      const resizedDataUrl = canvas.toDataURL(mimeType, 0.92);

      currentCustomAvatarData = resizedDataUrl;
      updateAvatarPreview(resizedDataUrl);

      // Show info box
      const infoBox = document.getElementById('avatar-upload-info-box');
      const nameLabel = document.getElementById('avatar-filename-label');
      if (infoBox && nameLabel) {
        nameLabel.innerText = `${file.name} (${Math.round(file.size / 1024)} KB)`;
        infoBox.classList.remove('hidden');
      }

      setAvatarMode('upload');
      showToast('Фото успешно выбрано! Нажмите «Сохранить» 📷');
      lucide.createIcons();
    };
    img.src = rawDataUrl;
  };
  reader.readAsDataURL(file);
}

function clearUploadedAvatar() {
  currentCustomAvatarData = null;
  const fileInput = document.getElementById('avatar-file-input');
  if (fileInput) fileInput.value = '';
  const infoBox = document.getElementById('avatar-upload-info-box');
  if (infoBox) infoBox.classList.add('hidden');

  const fallback = buildAvatarUrl(currentAvatarStyle, currentUser?.username || 'user');
  updateAvatarPreview(fallback);
  showToast('Пользовательское фото очищено');
}

function setupAvatarDragAndDrop() {
  const dropzone = document.getElementById('avatar-dropzone');
  if (!dropzone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('border-sky-500', 'bg-sky-500/10');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('border-sky-500', 'bg-sky-500/10');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
      processAvatarFile(files[0]);
    }
  }, false);
}

function openProfileModal() {
  if (!currentUser) {
    openAuthModal('login');
    return;
  }
  const modal = document.getElementById('profile-modal');
  if (!modal) return;

  // Reset alert messages
  const errBox = document.getElementById('profile-error-box');
  const okBox = document.getElementById('profile-success-box');
  if (errBox) errBox.classList.add('hidden');
  if (okBox) okBox.classList.add('hidden');

  // Populate data
  const avatar = currentUser.avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${currentUser.username}`;
  const displayName = currentUser.display_name || currentUser.username;
  const isDev = isDeveloperUser(currentUser);
  const devBadge = getDeveloperBadgeHtml(currentUser);
  
  document.getElementById('profile-modal-avatar-preview').src = avatar;
  document.getElementById('profile-modal-display-name').innerHTML = `<span>${escapeHtml(displayName)}</span> ${devBadge}`;
  document.getElementById('profile-modal-username').innerText = `@${currentUser.username}`;
  document.getElementById('profile-modal-stars').innerText = currentUser.stars || 0;
  document.getElementById('profile-modal-tasks').innerText = (currentUser.solved_tasks || []).length;
  
  const titleBadge = document.getElementById('profile-modal-title-badge');
  if (titleBadge) {
    const role = getUserRole(currentUser);
    const customRole = (window.devLoadedRoles || []).find(r => r.id === role);
    if (role === 'creator') {
      titleBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-gradient-to-r from-amber-500/25 to-rose-500/25 text-amber-300 border border-amber-500/50 shadow-sm";
      titleBadge.innerText = "👑 Создатель & Lead Dev";
    } else if (role === 'admin') {
      titleBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-300 border border-red-500/50 shadow-sm";
      titleBadge.innerText = "⚡ Администратор";
    } else if (role === 'moderator') {
      titleBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-sm";
      titleBadge.innerText = "🛡️ Модератор";
    } else if (role === 'vip') {
      titleBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/50 shadow-sm";
      titleBadge.innerText = "⭐ VIP Пользователь";
    } else if (role === 'mentor') {
      titleBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm";
      titleBadge.innerText = "🧠 Эксперт & Ментор";
    } else if (customRole) {
      titleBadge.className = `px-2 py-0.5 rounded text-[10px] font-bold border ${customRole.color_class || 'bg-sky-500/20 text-sky-300 border-sky-500/50'}`;
      titleBadge.innerText = customRole.name;
    } else if (currentUser.active_title) {
      titleBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-amber-400 border border-slate-700";
      titleBadge.innerText = currentUser.active_title.name || '🐍 Pythonist';
    } else {
      titleBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700";
      titleBadge.innerText = "🐍 Pythonist";
    }
  }
  
  // Inputs
  document.getElementById('profile-displayname-input').value = displayName;
  document.getElementById('profile-bio-input').value = currentUser.bio || '';
  document.getElementById('profile-new-password').value = '';

  // Initialize Avatar Mode & Values based on current avatar
  currentAvatarSeed = currentUser.username;
  const infoBox = document.getElementById('avatar-upload-info-box');
  const nameLabel = document.getElementById('avatar-filename-label');

  if (avatar.startsWith('data:image/')) {
    currentCustomAvatarData = avatar;
    if (infoBox && nameLabel) {
      nameLabel.innerText = 'Загруженное фото профиля ✅';
      infoBox.classList.remove('hidden');
    }
    setAvatarMode('upload');
  } else if (avatar.includes('api.dicebear.com')) {
    const match = avatar.match(/\/7\.x\/([a-z\-]+)\/svg\?seed=([^&]+)/);
    if (match) {
      currentAvatarStyle = match[1];
      currentAvatarSeed = decodeURIComponent(match[2]);
    }
    document.getElementById('profile-avatar-seed-input').value = currentAvatarSeed;
    highlightAvatarStyleButton(currentAvatarStyle);
    if (infoBox) infoBox.classList.add('hidden');
    setAvatarMode('preset');
  } else if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    document.getElementById('profile-avatar-url-input').value = avatar;
    if (infoBox) infoBox.classList.add('hidden');
    setAvatarMode('url');
  } else {
    currentCustomAvatarData = null;
    if (infoBox) infoBox.classList.add('hidden');
    setAvatarMode('upload');
  }

  highlightAvatarStyleButton(currentAvatarStyle);
  populateProfileTitleSelect();
  setupAvatarDragAndDrop();

  modal.classList.remove('hidden');
  lucide.createIcons();
}

function closeProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (modal) modal.classList.add('hidden');
}

function highlightAvatarStyleButton(style) {
  document.querySelectorAll('.avatar-style-btn').forEach(btn => {
    const s = btn.getAttribute('data-style');
    if (s === style) {
      btn.className = 'avatar-style-btn p-1.5 rounded-xl border border-sky-500 bg-sky-500/15 flex flex-col items-center gap-1 transition shadow-sm';
    } else {
      btn.className = 'avatar-style-btn p-1.5 rounded-xl border border-slate-800 bg-slate-900 hover:border-slate-700 flex flex-col items-center gap-1 transition';
    }
  });
}

function selectAvatarStyle(style) {
  currentAvatarStyle = style;
  highlightAvatarStyleButton(style);
  const inputVal = document.getElementById('profile-avatar-seed-input')?.value.trim();
  const newUrl = buildAvatarUrl(currentAvatarStyle, inputVal || currentUser?.username || 'user');
  updateAvatarPreview(newUrl);
}

function randomizeAvatar() {
  const randomSeeds = ['CyberPy', 'Pythonista', 'AsyncMaster', 'ByteCoder', 'DevWizard', 'QuantumPy', 'CodeAlchemist', 'FastDev', 'SnakeHero', 'TurboPython', 'DevKing', 'ShadowCoder'];
  const randNum = Math.floor(Math.random() * 9000) + 1000;
  const pickedSeed = randomSeeds[Math.floor(Math.random() * randomSeeds.length)] + '_' + randNum;
  currentAvatarSeed = pickedSeed;
  const seedInput = document.getElementById('profile-avatar-seed-input');
  if (seedInput) seedInput.value = pickedSeed;
  const newUrl = buildAvatarUrl(currentAvatarStyle, pickedSeed);
  updateAvatarPreview(newUrl);
  setAvatarMode('preset');
}

function onAvatarSeedChange(val) {
  currentAvatarSeed = val.trim();
  const newUrl = buildAvatarUrl(currentAvatarStyle, currentAvatarSeed || currentUser?.username || 'user');
  updateAvatarPreview(newUrl);
}

function onAvatarUrlInputChange(val) {
  const clean = val.trim();
  if (clean) {
    updateAvatarPreview(clean);
  }
}

function buildAvatarUrl(style, seedOrUrl) {
  if (!seedOrUrl) return `https://api.dicebear.com/7.x/${style || 'bottts'}/svg?seed=user`;
  if (seedOrUrl.startsWith('http://') || seedOrUrl.startsWith('https://') || seedOrUrl.startsWith('data:image/')) {
    return seedOrUrl;
  }
  return `https://api.dicebear.com/7.x/${style || 'bottts'}/svg?seed=${encodeURIComponent(seedOrUrl)}`;
}

function updateAvatarPreview(url) {
  const img = document.getElementById('profile-modal-avatar-preview');
  if (img && url) img.src = url;
}

function populateProfileTitleSelect() {
  const sel = document.getElementById('profile-title-select');
  const badge = document.getElementById('profile-modal-title-badge');
  if (!sel || !userProfile) return;

  const unlocked = currentUser?.unlocked_titles || ['title_novice'];
  const allShopTitles = userProfile.shop_titles || [];
  
  sel.innerHTML = '';
  allShopTitles.forEach(t => {
    if (unlocked.includes(t.id)) {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.innerText = `${t.icon} ${t.name}`;
      if (t.id === currentUser?.active_title_id) {
        opt.selected = true;
        if (badge) badge.innerText = `${t.icon} ${t.name}`;
      }
      sel.appendChild(opt);
    }
  });
}

async function onProfileTitleChange(titleId) {
  try {
    const res = await fetch('/api/practice/set-active-title', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title_id: titleId })
    });
    const data = await res.json();
    if (data.success && data.active_title) {
      if (currentUser) currentUser.active_title_id = titleId;
      const badge = document.getElementById('profile-modal-title-badge');
      if (badge) badge.innerText = `${data.active_title.icon} ${data.active_title.name}`;
      const headerTitle = document.getElementById('header-active-title');
      if (headerTitle) headerTitle.innerText = `${data.active_title.icon} ${data.active_title.name}`;
      showToast(`Звание обновлено: ${data.active_title.name}! 👑`);
    }
  } catch (err) {
    console.error('Ошибка выбора звания:', err);
  }
}

async function handleSaveProfileSubmit(event) {
  event.preventDefault();
  const displayName = document.getElementById('profile-displayname-input').value.trim();
  const bio = document.getElementById('profile-bio-input').value.trim();
  const newPassword = document.getElementById('profile-new-password').value.trim();
  const errBox = document.getElementById('profile-error-box');
  const errMsg = document.getElementById('profile-error-msg');
  const okBox = document.getElementById('profile-success-box');
  const btn = document.getElementById('btn-save-profile');

  if (errBox) errBox.classList.add('hidden');
  if (okBox) okBox.classList.add('hidden');

  let finalAvatar = null;
  if (currentAvatarMode === 'upload') {
    finalAvatar = currentCustomAvatarData || currentUser?.avatar || buildAvatarUrl('bottts', currentUser?.username || 'user');
  } else if (currentAvatarMode === 'url') {
    const urlVal = document.getElementById('profile-avatar-url-input')?.value.trim();
    finalAvatar = urlVal || currentUser?.avatar || buildAvatarUrl('bottts', currentUser?.username || 'user');
  } else {
    const seedVal = document.getElementById('profile-avatar-seed-input')?.value.trim();
    finalAvatar = buildAvatarUrl(currentAvatarStyle, seedVal || currentUser?.username || 'user');
  }

  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Сохранение...</span>';
  lucide.createIcons();

  try {
    const bodyPayload = {
      display_name: displayName,
      avatar: finalAvatar,
      bio: bio
    };
    if (newPassword) {
      bodyPayload.new_password = newPassword;
    }

    const res = await fetch('/api/auth/profile', {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(bodyPayload)
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      if (errBox && errMsg) {
        errMsg.innerText = data.detail || 'Не удалось сохранить профиль';
        errBox.classList.remove('hidden');
      }
      return;
    }

    currentUser = data.user;
    updateHeaderUserWidget(currentUser);
    document.getElementById('profile-modal-display-name').innerText = currentUser.display_name || currentUser.username;
    document.getElementById('profile-modal-avatar-preview').src = currentUser.avatar;

    if (okBox) okBox.classList.remove('hidden');
    showToast('Профиль и аватар успешно сохранены! 🎉');

    if (currentTab === 'leaderboard') loadLeaderboard();
    if (currentTab === 'forum') loadForumTopics();
    if (currentTab === 'ideas') loadIdeas();

    setTimeout(() => {
      closeProfileModal();
    }, 900);
  } catch (err) {
    if (errBox && errMsg) {
      errMsg.innerText = err.message;
      errBox.classList.remove('hidden');
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="save" class="w-3.5 h-3.5"></i><span>Сохранить</span>';
    lucide.createIcons();
  }
}

// ==========================================
// --- LEADERBOARD ---
// ==========================================

async function loadLeaderboard() {
  try {
    const res = await fetch('/api/leaderboard', {
      headers: getAuthHeaders()
    });
    const data = await res.json();
    allLeaderboardData = data.rankings || [];
    renderLeaderboard(data);
  } catch (err) {
    console.error('Ошибка загрузки таблицы лидеров:', err);
  }
}

function renderLeaderboard(data) {
  // Total players
  const totalElem = document.getElementById('leaderboard-total-count');
  if (totalElem) totalElem.innerText = data.total_players || 0;

  // User Card
  const userCard = document.getElementById('leaderboard-user-card');
  if (userCard) {
    if (data.current_user_rank) {
      const u = data.current_user_rank;
      const isDev = isDeveloperUser(u);
      userCard.innerHTML = `
        <div class="flex items-center space-x-3.5">
          <div class="w-12 h-12 rounded-2xl ${isDev ? 'bg-amber-500/25 border-2 border-amber-400 text-amber-300 shadow-lg shadow-amber-500/20' : 'bg-amber-500/20 border border-amber-500/30 text-amber-400'} flex items-center justify-center font-extrabold text-lg shadow-inner">
            #${u.rank}
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                <span>${escapeHtml(u.display_name)}</span>
                ${getDeveloperBadgeHtml(u)}
              </h3>
              <span class="text-[10px] px-2 py-0.5 rounded ${isDev ? 'bg-gradient-to-r from-amber-500/25 to-rose-500/25 text-amber-300 font-extrabold border border-amber-500/50' : 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30'}">${escapeHtml(u.title_name)}</span>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">${isDev ? '👑 Создатель и разработчик платформы PyForge' : 'Ваш глобальный ранг среди всех участников сообщества'}</p>
          </div>
        </div>
        <div class="flex items-center space-x-6 sm:border-l sm:border-slate-800 sm:pl-6">
          <div class="text-center">
            <div class="text-[10px] uppercase font-bold text-slate-400">Решено задач</div>
            <div class="text-base font-extrabold text-white">${u.solved_tasks_count}</div>
          </div>
          <div class="text-center">
            <div class="text-[10px] uppercase font-bold text-slate-400">Баланс ⭐</div>
            <div class="text-base font-extrabold text-amber-400 flex items-center justify-center gap-1">
              <i data-lucide="star" class="w-4 h-4 fill-amber-400"></i> ${u.stars}
            </div>
          </div>
        </div>
      `;
    } else {
      userCard.innerHTML = `
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-slate-800 text-slate-400 flex items-center justify-center font-bold">
            <i data-lucide="user" class="w-5 h-5"></i>
          </div>
          <div>
            <h3 class="text-xs font-bold text-white">Вы еще не вошли в аккаунт</h3>
            <p class="text-[11px] text-slate-400">Войдите или зарегистрируйтесь, чтобы занять свое место в Таблице Лидеров!</p>
          </div>
        </div>
        <button onclick="openAuthModal('login')" class="px-4 py-2 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 text-white font-bold text-xs shadow-md">
          Войти в профиль
        </button>
      `;
    }
  }

  // Top 3 Podium
  const podiumContainer = document.getElementById('leaderboard-podium');
  if (podiumContainer) {
    podiumContainer.innerHTML = '';
    const top3 = data.top_3 || [];
    const podiumRanks = [
      { rank: 1, medal: '🥇', border: 'border-amber-400/50', glow: 'shadow-amber-500/20 bg-amber-950/20', text: 'text-amber-300' },
      { rank: 2, medal: '🥈', border: 'border-slate-400/50', glow: 'shadow-slate-400/10 bg-slate-900/60', text: 'text-slate-200' },
      { rank: 3, medal: '🥉', border: 'border-orange-500/50', glow: 'shadow-orange-500/10 bg-orange-950/20', text: 'text-orange-300' }
    ];

    podiumRanks.forEach(pr => {
      const player = top3.find(p => p.rank === pr.rank);
      const card = document.createElement('div');
      card.className = `glass-panel rounded-2xl p-5 border ${pr.border} ${pr.glow} flex flex-col items-center text-center space-y-3 relative overflow-hidden transition hover:scale-[1.02]`;
      if (player) {
        const isPlayerDev = isDeveloperUser(player);
        card.innerHTML = `
          <div class="absolute top-3 left-3 text-2xl">${pr.medal}</div>
          <div class="relative mt-2">
            <img src="${player.avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${player.username}`}" class="w-16 h-16 rounded-2xl border-2 ${isPlayerDev ? 'border-amber-400' : pr.border} bg-slate-950 shadow-lg" alt="${escapeHtml(player.display_name)}">
            ${isPlayerDev ? '<span class="absolute -bottom-1 -right-1 px-1 py-0.2 rounded bg-amber-500 text-black font-black text-[9px] shadow">DEV</span>' : ''}
          </div>
          <div class="space-y-1">
            <h4 class="font-bold text-sm text-white flex items-center justify-center gap-1.5 flex-wrap">
              <span>${escapeHtml(player.display_name)}</span>
              ${getDeveloperBadgeHtml(player)}
              ${player.is_current_user ? '<span class="text-[9px] px-1.5 py-0.2 rounded bg-sky-500/20 text-sky-400 border border-sky-500/30">Вы</span>' : ''}
            </h4>
            <div class="text-[11px] font-semibold ${isPlayerDev ? 'text-amber-300' : pr.text}">${escapeHtml(player.title_name)}</div>
          </div>
          <div class="w-full pt-3 border-t border-slate-800/80 flex items-center justify-around text-xs">
            <div>
              <span class="text-[10px] text-slate-500 block">Задачи</span>
              <span class="font-bold text-slate-200">${player.solved_tasks_count}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 block">Очки</span>
              <span class="font-bold text-amber-400 flex items-center justify-center gap-0.5">
                <i data-lucide="star" class="w-3 h-3 fill-amber-400"></i> ${player.stars}
              </span>
            </div>
          </div>
        `;
      } else {
        card.innerHTML = `
          <div class="text-2xl">${pr.medal}</div>
          <div class="w-16 h-16 rounded-2xl border border-dashed border-slate-700 flex items-center justify-center text-slate-600">?</div>
          <p class="text-xs text-slate-500">Место свободно</p>
        `;
      }
      podiumContainer.appendChild(card);
    });
  }

  // Full Table
  renderLeaderboardRows(data.rankings || []);
  lucide.createIcons();
}

function renderLeaderboardRows(rankings) {
  const tbody = document.getElementById('leaderboard-table-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (rankings.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-slate-500">Пользователи не найдены</td></tr>`;
    return;
  }

  rankings.forEach(p => {
    const tr = document.createElement('tr');
    const isDev = isDeveloperUser(p);
    tr.className = `transition hover:bg-slate-850/60 ${p.is_current_user ? 'bg-sky-950/30 border-l-2 border-sky-500 font-medium' : isDev ? 'bg-amber-950/15' : ''}`;

    let medalEmoji = p.rank === 1 ? '🥇' : p.rank === 2 ? '🥈' : p.rank === 3 ? '🥉' : `#${p.rank}`;

    tr.innerHTML = `
      <td class="py-3 px-4 font-bold text-center text-xs text-slate-400">${medalEmoji}</td>
      <td class="py-3 px-4">
        <div class="flex items-center space-x-3">
          <div class="relative">
            <img src="${p.avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${p.username}`}" class="w-8 h-8 rounded-xl border ${isDev ? 'border-amber-400' : 'border-slate-700'} bg-slate-900" alt="">
          </div>
          <div>
            <div class="font-bold text-white text-xs flex items-center gap-1.5">
              <span>${escapeHtml(p.display_name)}</span>
              ${getDeveloperBadgeHtml(p)}
              ${p.is_current_user ? '<span class="text-[9px] px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-400 font-bold border border-sky-500/30">ВЫ</span>' : ''}
            </div>
            <div class="text-[10px] ${isDev ? 'text-amber-400 font-semibold' : 'text-slate-500'} font-mono">@${escapeHtml(p.username)}</div>
          </div>
        </div>
      </td>
      <td class="py-3 px-4">
        <span class="text-xs font-semibold ${isDev ? 'text-amber-300' : 'text-slate-300'}">${escapeHtml(p.title_name)}</span>
      </td>
      <td class="py-3 px-4 text-center">
        <span class="px-2 py-0.5 rounded-md bg-slate-900 text-slate-300 font-mono text-[11px] border border-slate-800">${p.solved_tasks_count}</span>
      </td>
      <td class="py-3 px-4 text-right font-bold text-amber-400 font-mono text-xs">
        <span class="flex items-center justify-end gap-1">
          <i data-lucide="star" class="w-3.5 h-3.5 fill-amber-400"></i> ${p.stars} ⭐
        </span>
      </td>
    `;
    tbody.appendChild(tr);
  });
  lucide.createIcons();
}

function filterLeaderboardTable() {
  const query = (document.getElementById('leaderboard-search')?.value || '').toLowerCase().trim();
  if (!query) {
    renderLeaderboardRows(allLeaderboardData);
    return;
  }
  const filtered = allLeaderboardData.filter(p =>
    (p.display_name && p.display_name.toLowerCase().includes(query)) ||
    (p.username && p.username.toLowerCase().includes(query)) ||
    (p.title_name && p.title_name.toLowerCase().includes(query))
  );
  renderLeaderboardRows(filtered);
}

// ==========================================
// --- COMMUNITY FORUM ---
// ==========================================

let allForumCategories = [];
let allForumTopics = [];

async function loadForumCategories() {
  try {
    const res = await fetch('/api/forum/categories');
    allForumCategories = await res.json();
    renderForumCategoryPills(allForumCategories);
  } catch (err) {
    console.error('Ошибка загрузки категорий форума:', err);
  }
}

function renderForumCategoryPills(categories) {
  const bar = document.getElementById('forum-categories-bar');
  if (!bar) return;
  bar.innerHTML = '';

  categories.forEach(cat => {
    const btn = document.createElement('button');
    const isActive = currentForumCategory === cat.id;
    btn.className = `px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${isActive ? 'bg-sky-600 text-white shadow-md' : 'bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800'}`;
    btn.onclick = () => selectForumCategory(cat.id);
    btn.innerHTML = `<i data-lucide="${cat.icon || 'folder'}" class="w-3.5 h-3.5"></i> <span>${cat.name}</span>`;
    bar.appendChild(btn);
  });
  lucide.createIcons();
}

function selectForumCategory(catId) {
  currentForumCategory = catId;
  renderForumCategoryPills(allForumCategories);
  loadForumTopics();
}

async function loadForumTopics() {
  const container = document.getElementById('forum-topics-container');
  if (container) {
    container.innerHTML = '<p class="text-slate-500 text-center py-6">Загрузка тем обсуждения...</p>';
  }
  try {
    let url = `/api/forum/topics?category=${currentForumCategory}`;
    if (currentForumSearch) {
      url += `&search=${encodeURIComponent(currentForumSearch)}`;
    }
    const res = await fetch(url);
    allForumTopics = await res.json();
    renderForumTopics(allForumTopics);
  } catch (err) {
    if (container) container.innerHTML = `<p class="text-rose-400 text-center py-6">Ошибка: ${err.message}</p>`;
  }
}

function renderForumTopics(topics) {
  const container = document.getElementById('forum-topics-container');
  if (!container) return;
  container.innerHTML = '';

  if (topics.length === 0) {
    container.innerHTML = `
      <div class="glass-panel rounded-2xl p-8 border border-slate-800 text-center space-y-3">
        <div class="w-12 h-12 rounded-2xl bg-sky-500/10 text-sky-400 flex items-center justify-center mx-auto">
          <i data-lucide="messages-square" class="w-6 h-6"></i>
        </div>
        <h4 class="text-sm font-bold text-white">Темы не найдены</h4>
        <p class="text-xs text-slate-400">Будьте первым, кто создаст тему в этой категории!</p>
        <button onclick="openNewTopicModal()" class="px-4 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs">
          + Создать тему
        </button>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  topics.forEach(t => {
    const card = document.createElement('div');
    const authorObj = { username: t.author_username, display_name: t.author_display_name, role: t.author_role, is_developer: t.author_is_dev };
    const isAuthorDev = isDeveloperUser(authorObj);
    const badgeHtml = getUserBadgeHtml(authorObj);
    if (t.author_username && t.author_role) {
      window.allUsersRoleCache[t.author_username.toLowerCase()] = t.author_role;
    }

    card.className = 'glass-panel rounded-2xl p-5 border border-slate-800/80 hover:border-sky-500/50 transition cursor-pointer space-y-3 group';
    card.onclick = (e) => {
      if (e.target.closest('.no-modal-open')) return;
      openTopicDetail(t.id);
    };

    const tagsHtml = (t.tags || []).map(tag => `<span class="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] text-slate-400 font-mono">#${escapeHtml(tag)}</span>`).join('');

    card.innerHTML = `
      <div class="flex items-start justify-between gap-4">
        <div class="space-y-1 flex-1">
          <div class="flex items-center space-x-2">
            <span class="px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 text-[10px] font-bold uppercase tracking-wider">${escapeHtml(t.category)}</span>
            <span class="text-[11px] text-slate-500">${t.created_at ? t.created_at.split('T')[0] : ''}</span>
          </div>
          <h3 class="font-bold text-sm text-white group-hover:text-sky-300 transition leading-snug">${escapeHtml(t.title)}</h3>
          <p class="text-xs text-slate-300 line-clamp-2 leading-relaxed font-sans">${escapeHtml(t.preview)}</p>
        </div>
        <div class="flex items-center space-x-3 flex-shrink-0 pt-1">
          <div class="flex items-center space-x-1 text-slate-400 text-xs">
            <i data-lucide="eye" class="w-3.5 h-3.5"></i>
            <span>${t.views || 0}</span>
          </div>
          <div class="flex items-center space-x-1 text-sky-400 text-xs font-semibold">
            <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
            <span>${t.comments_count || 0}</span>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-850">
        <div class="flex items-center space-x-2">
          <img src="${t.author_avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${t.author_username}`}" class="w-5 h-5 rounded-md border ${isAuthorDev ? 'border-amber-400' : 'border-slate-700'} bg-slate-900" alt="">
          <span class="text-xs font-semibold text-slate-300 flex items-center gap-1">
            <span>${escapeHtml(t.author_display_name || t.author_username)}</span>
            ${badgeHtml}
          </span>
          <span class="text-[10px] ${isAuthorDev ? 'text-amber-300 font-bold' : 'text-amber-400 font-medium'}">${escapeHtml(t.author_title || (isAuthorDev ? '👑 Создатель' : '🐍 Pythonist'))}</span>
        </div>
        <div class="flex items-center space-x-2">
          ${tagsHtml}
        </div>
      </div>
    `;
    container.appendChild(card);
  });
  lucide.createIcons();
}

function filterForumTopics() {
  currentForumSearch = (document.getElementById('forum-search-input')?.value || '').trim();
  loadForumTopics();
}

function openNewTopicModal() {
  const token = getAuthToken();
  if (!token) {
    showToast('Пожалуйста, авторизуйтесь для создания темы на форуме');
    openAuthModal('login');
    return;
  }
  document.getElementById('forum-topic-modal').classList.remove('hidden');
}

function closeNewTopicModal() {
  document.getElementById('forum-topic-modal').classList.add('hidden');
}

async function handleCreateTopicSubmit(event) {
  event.preventDefault();
  const title = document.getElementById('new-topic-title').value.trim();
  const category = document.getElementById('new-topic-category').value;
  const tagsStr = document.getElementById('new-topic-tags').value.trim();
  const content = document.getElementById('new-topic-content').value.trim();
  const btn = document.getElementById('btn-submit-topic');

  const tags = tagsStr ? tagsStr.split(',').map(s => s.trim()).filter(Boolean) : [];

  btn.disabled = true;
  btn.innerHTML = 'Публикация...';

  try {
    const res = await fetch('/api/forum/topics/create', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title, category, tags, content })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Не удалось опубликовать');
    }
    const topic = await res.json();
    closeNewTopicModal();
    showToast('Тема успешно создана на форуме! 🎉');
    document.getElementById('new-topic-title').value = '';
    document.getElementById('new-topic-content').value = '';
    document.getElementById('new-topic-tags').value = '';
    loadForumTopics();
    openTopicDetail(topic.id);
  } catch (err) {
    alert(err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Опубликовать тему';
  }
}

async function openTopicDetail(topicId) {
  try {
    const res = await fetch(`/api/forum/topics/${topicId}`);
    if (!res.ok) throw new Error('Тема не найдена');
    currentTopicDetail = await res.json();
    renderTopicDetailModal(currentTopicDetail);
    document.getElementById('forum-detail-modal').classList.remove('hidden');
  } catch (err) {
    alert(err.message);
  }
}

function renderTopicDetailModal(topic) {
  const authorObj = { username: topic.author_username, display_name: topic.author_display_name, role: topic.author_role, is_developer: topic.author_is_dev };
  const isDev = isDeveloperUser(authorObj);
  if (topic.author_username && topic.author_role) {
    window.allUsersRoleCache[topic.author_username.toLowerCase()] = topic.author_role;
  }
  document.getElementById('topic-detail-title').innerText = topic.title;
  document.getElementById('topic-detail-category-badge').innerText = topic.category.toUpperCase();
  document.getElementById('topic-detail-date').innerText = topic.created_at ? topic.created_at.replace('T', ' ').slice(0, 16) : '';
  document.getElementById('topic-detail-author-avatar').src = topic.author_avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${topic.author_username}`;
  document.getElementById('topic-detail-author-name').innerHTML = `<span>${escapeHtml(topic.author_display_name || topic.author_username)}</span> ${getUserBadgeHtml(authorObj)}`;
  
  const authorTitleElem = document.getElementById('topic-detail-author-title');
  if (authorTitleElem) {
    authorTitleElem.innerText = isDev ? '👑 Создатель & Lead Dev' : (topic.author_title || '🐍 Pythonist');
    authorTitleElem.className = isDev ? 'text-[10px] text-amber-300 font-extrabold' : 'text-[10px] text-amber-400 font-medium';
  }

  document.getElementById('topic-detail-content').innerText = topic.content;
  document.getElementById('topic-detail-upvotes-count').innerText = topic.upvotes || 0;
  document.getElementById('topic-detail-comments-count').innerText = (topic.comments || []).length;

  const tagsContainer = document.getElementById('topic-detail-tags');
  tagsContainer.innerHTML = (topic.tags || []).map(t => `<span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] text-slate-400 font-mono">#${escapeHtml(t)}</span>`).join('');

  // Render comments
  renderTopicComments(topic.comments || []);
  lucide.createIcons();
}

function renderTopicComments(comments) {
  const container = document.getElementById('topic-comments-list');
  if (!container) return;
  container.innerHTML = '';

  if (comments.length === 0) {
    container.innerHTML = '<p class="text-slate-500 text-xs text-center py-4 bg-slate-950/40 rounded-xl border border-slate-850">Пока нет ответов. Напишите первый комментарий!</p>';
    return;
  }

  comments.forEach(c => {
    const card = document.createElement('div');
    const authorObj = { username: c.author_username, display_name: c.author_display_name, role: c.author_role, is_developer: c.author_is_dev };
    const isDev = isDeveloperUser(authorObj);
    const badgeHtml = getUserBadgeHtml(authorObj);
    if (c.author_username && c.author_role) {
      window.allUsersRoleCache[c.author_username.toLowerCase()] = c.author_role;
    }
    card.className = `p-3.5 rounded-xl ${isDev ? 'bg-amber-950/20 border border-amber-500/30' : 'bg-slate-950/60 border border-slate-800'} space-y-2`;
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <img src="${c.author_avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${c.author_username}`}" class="w-6 h-6 rounded-md border ${isDev ? 'border-amber-400' : 'border-slate-700'} bg-slate-900">
          <span class="font-bold text-white text-xs flex items-center gap-1">
            <span>${escapeHtml(c.author_display_name || c.author_username)}</span>
            ${badgeHtml}
          </span>
          <span class="text-[10px] ${isDev ? 'text-amber-300 font-extrabold' : 'text-amber-400'}">${isDev ? '👑 Создатель & Lead Dev' : escapeHtml(c.author_title || '🐍 Pythonist')}</span>
        </div>
        <span class="text-[10px] text-slate-500 font-mono">${c.created_at ? c.created_at.slice(0, 16).replace('T', ' ') : ''}</span>
      </div>
      <div class="text-xs text-slate-300 leading-relaxed font-sans pl-8 whitespace-pre-wrap">${escapeHtml(c.content)}</div>
    `;
    container.appendChild(card);
  });
}

function closeTopicDetailModal() {
  document.getElementById('forum-detail-modal').classList.add('hidden');
}

async function upvoteCurrentTopic() {
  if (!currentTopicDetail) return;
  try {
    const res = await fetch('/api/forum/upvote', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ topic_id: currentTopicDetail.id })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      document.getElementById('topic-detail-upvotes-count').innerText = data.upvotes;
      showToast(data.voted ? 'Голос учтен! 👍' : 'Голос отозван');
      loadForumTopics();
    }
  } catch (e) {
    showToast('Ошибка при голосовании');
  }
}

async function handleAddCommentSubmit(event) {
  event.preventDefault();
  const token = getAuthToken();
  if (!token) {
    showToast('Пожалуйста, авторизуйтесь для добавления комментария');
    openAuthModal('login');
    return;
  }
  if (!currentTopicDetail) return;

  const contentElem = document.getElementById('new-comment-content');
  const content = contentElem.value.trim();
  const btn = document.getElementById('btn-submit-comment');

  if (!content) return;

  btn.disabled = true;
  btn.innerHTML = 'Отправка...';

  try {
    const res = await fetch('/api/forum/comments/create', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ topic_id: currentTopicDetail.id, content })
    });
    if (!res.ok) throw new Error('Ошибка добавления комментария');
    const newComment = await res.json();
    if (!currentTopicDetail.comments) currentTopicDetail.comments = [];
    currentTopicDetail.comments.push(newComment);
    contentElem.value = '';
    renderTopicComments(currentTopicDetail.comments);
    document.getElementById('topic-detail-comments-count').innerText = currentTopicDetail.comments.length;
    showToast('Комментарий успешно добавлен!');
    loadForumTopics();
  } catch (err) {
    alert(err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="send" class="w-3.5 h-3.5"></i><span>Отправить ответ</span>';
    lucide.createIcons();
  }
}

// ==========================================
// --- CREATOR IDEAS HUB ---
// ==========================================

let allIdeas = [];

async function loadIdeas() {
  const container = document.getElementById('ideas-container');
  if (container) {
    container.innerHTML = '<p class="text-slate-500 text-center col-span-2 py-8">Загрузка предложений...</p>';
  }
  const sortBy = document.getElementById('ideas-sort-select')?.value || 'popular';
  try {
    const res = await fetch(`/api/ideas/list?status=${currentIdeasStatus}&sort_by=${sortBy}`);
    allIdeas = await res.json();
    renderIdeas(allIdeas);
  } catch (err) {
    if (container) container.innerHTML = `<p class="text-rose-400 text-center col-span-2 py-8">Ошибка: ${err.message}</p>`;
  }
}

function filterIdeas(status) {
  currentIdeasStatus = status;
  document.querySelectorAll('.idea-filter-btn').forEach(btn => {
    btn.className = 'idea-filter-btn px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800';
  });
  event.target.className = 'idea-filter-btn active px-3 py-1.5 rounded-xl text-xs font-semibold bg-yellow-500/20 text-yellow-300 border border-yellow-500/30';
  loadIdeas();
}

function renderIdeas(ideas) {
  const container = document.getElementById('ideas-container');
  if (!container) return;
  container.innerHTML = '';

  if (ideas.length === 0) {
    container.innerHTML = `
      <div class="col-span-2 glass-panel rounded-2xl p-8 border border-slate-800 text-center space-y-3">
        <div class="w-12 h-12 rounded-2xl bg-yellow-500/10 text-yellow-400 flex items-center justify-center mx-auto">
          <i data-lucide="lightbulb" class="w-6 h-6"></i>
        </div>
        <h4 class="text-sm font-bold text-white">В этой категории пока нет предложений</h4>
        <p class="text-xs text-slate-400">Предложите свою крутую идею создателям PyForge!</p>
        <button onclick="openNewIdeaModal()" class="px-4 py-2 rounded-xl bg-yellow-500 hover:bg-yellow-400 text-black font-bold text-xs">
          Предложить идею
        </button>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  ideas.forEach(idea => {
    const card = document.createElement('div');
    const authorObj = { username: idea.author_username, display_name: idea.author_display_name, role: idea.author_role, is_developer: idea.author_is_dev };
    const isAuthorDev = isDeveloperUser(authorObj);
    const badgeHtml = getUserBadgeHtml(authorObj);
    if (idea.author_username && idea.author_role) {
      window.allUsersRoleCache[idea.author_username.toLowerCase()] = idea.author_role;
    }

    card.className = `glass-panel rounded-2xl p-5 border ${isAuthorDev ? 'border-amber-500/40 bg-amber-950/10' : 'border-slate-800'} flex flex-col justify-between space-y-4 hover:border-yellow-500/40 transition shadow-sm`;

    const statusColor = idea.status === 'completed' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
                        idea.status === 'in_progress' ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' :
                        'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';

    card.innerHTML = `
      <div class="space-y-3">
        <div class="flex items-start justify-between gap-3">
          <div class="space-y-1">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${statusColor}">
                ${escapeHtml(idea.status_label || '💡 На рассмотрении')}
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-900 text-slate-400 font-mono border border-slate-800">
                ${escapeHtml(idea.category)}
              </span>
            </div>
            <h3 class="font-bold text-sm text-white pt-1">${escapeHtml(idea.title)}</h3>
          </div>

          <!-- Upvote Vote Button -->
          <button onclick="voteForIdea('${idea.id}')" class="flex flex-col items-center justify-center p-2 rounded-xl bg-slate-900 hover:bg-yellow-500/20 border border-slate-800 hover:border-yellow-500/40 text-slate-300 hover:text-yellow-400 transition min-w-[50px] flex-shrink-0 group">
            <i data-lucide="chevron-up" class="w-4 h-4 group-hover:-translate-y-0.5 transition"></i>
            <span class="font-extrabold text-xs text-white group-hover:text-yellow-400 font-mono">${idea.votes || 0}</span>
          </button>
        </div>

        <p class="text-xs text-slate-300 leading-relaxed font-sans">${escapeHtml(idea.description)}</p>

        <!-- Developer Response Box -->
        ${idea.dev_response ? `
          <div class="p-3 rounded-xl bg-gradient-to-r from-yellow-950/30 to-slate-950 border border-yellow-500/20 text-xs space-y-1">
            <div class="flex items-center space-x-1.5 text-yellow-400 font-bold text-[11px]">
              <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
              <span>Ответ создателей PyForge:</span>
            </div>
            <p class="text-slate-300 text-[11px] leading-normal">${escapeHtml(idea.dev_response)}</p>
          </div>
        ` : ''}
      </div>

      <div class="flex items-center justify-between pt-3 border-t border-slate-850 text-xs text-slate-400">
        <div class="flex items-center space-x-2">
          <img src="${idea.author_avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${idea.author_username}`}" class="w-5 h-5 rounded-md border ${isAuthorDev ? 'border-amber-400' : 'border-slate-700'} bg-slate-900">
          <span class="text-[11px] text-slate-300 font-medium flex items-center gap-1">
            <span>${escapeHtml(idea.author_display_name || idea.author_username)}</span>
            ${badgeHtml}
          </span>
        </div>
        <span class="text-[10px] text-slate-500 font-mono">${idea.created_at ? idea.created_at.split('T')[0] : ''}</span>
      </div>
    `;
    container.appendChild(card);
  });
  lucide.createIcons();
}

async function voteForIdea(ideaId) {
  try {
    const res = await fetch('/api/ideas/vote', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ idea_id: ideaId })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.has_voted ? 'Голос за идею отдан! 🚀' : 'Голос отменен');
      loadIdeas();
    }
  } catch (e) {
    showToast('Ошибка при голосовании');
  }
}

function openNewIdeaModal() {
  const token = getAuthToken();
  if (!token) {
    showToast('Пожалуйста, авторизуйтесь для отправки предложений');
    openAuthModal('login');
    return;
  }
  document.getElementById('new-idea-modal').classList.remove('hidden');
}

function closeNewIdeaModal() {
  document.getElementById('new-idea-modal').classList.add('hidden');
}

async function handleCreateIdeaSubmit(event) {
  event.preventDefault();
  const title = document.getElementById('new-idea-title').value.trim();
  const category = document.getElementById('new-idea-category').value;
  const description = document.getElementById('new-idea-description').value.trim();
  const btn = document.getElementById('btn-submit-idea');

  btn.disabled = true;
  btn.innerHTML = 'Отправка...';

  try {
    const res = await fetch('/api/ideas/create', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title, category, description })
    });
    if (!res.ok) throw new Error('Ошибка отправки идеи');
    closeNewIdeaModal();
    showToast('Ваша идея успешно отправлена создателям! 🎉');
    document.getElementById('new-idea-title').value = '';
    document.getElementById('new-idea-description').value = '';
    loadIdeas();
  } catch (err) {
    alert(err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Отправить предложение';
  }
}

// ==========================================
// --- DAILY QUESTS & REWARDS SYSTEM ---
// ==========================================

let questResetTimerInterval = null;
let currentQuestsData = null;

async function loadDailyQuests() {
  try {
    const res = await fetch('/api/quests/daily', {
      headers: getAuthHeaders()
    });
    if (!res.ok) return;
    const data = await res.json();
    currentQuestsData = data;
    renderDailyQuests(data);
    startQuestResetTimer(data.seconds_to_reset || 0);
  } catch (err) {
    console.error('Ошибка загрузки ежедневных квестов:', err);
  }
}

function renderDailyQuests(data) {
  const container = document.getElementById('daily-quests-list');
  const badge = document.getElementById('quests-completed-badge');
  const topNavCount = document.getElementById('top-nav-quests-count');
  
  if (!container || !data) return;

  if (badge) {
    badge.innerText = `${data.completed_count || 0} / ${data.total_count || 4}`;
  }
  if (topNavCount) {
    topNavCount.innerText = `[${data.completed_count || 0}/${data.total_count || 4}]`;
  }

  container.innerHTML = '';

  (data.quests || []).forEach(q => {
    const isDone = q.completed;
    const isClaimed = q.claimed;
    const percent = Math.min(100, Math.round((q.progress / q.target_count) * 100));

    let actionButtonHtml = '';
    if (isClaimed) {
      actionButtonHtml = `
        <span class="px-3 py-1.5 rounded-xl bg-slate-800/80 text-emerald-400 text-xs font-bold border border-emerald-500/30 flex items-center gap-1">
          <i data-lucide="check-check" class="w-3.5 h-3.5"></i>
          <span>Получено</span>
        </span>
      `;
    } else if (isDone) {
      actionButtonHtml = `
        <button onclick="claimQuestReward('${q.id}')" class="px-3 py-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 text-xs font-extrabold shadow-lg shadow-amber-500/25 animate-pulse transition flex items-center gap-1.5">
          <i data-lucide="gift" class="w-3.5 h-3.5"></i>
          <span>Забрать +${q.reward_stars} ⭐</span>
        </button>
      `;
    } else {
      actionButtonHtml = `
        <span class="px-3 py-1.5 rounded-xl bg-slate-800/50 text-slate-400 text-xs font-mono font-medium border border-slate-700/50 flex items-center gap-1">
          <i data-lucide="clock" class="w-3 h-3 text-slate-500"></i>
          <span>${q.progress}/${q.target_count}</span>
        </span>
      `;
    }

    const card = document.createElement('div');
    card.className = `p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition ${isClaimed ? 'bg-slate-900/40 border-slate-800/60 opacity-80' : isDone ? 'bg-amber-950/20 border-amber-500/40 shadow-md shadow-amber-500/5' : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'}`;
    
    card.innerHTML = `
      <div class="flex items-start space-x-3 flex-1">
        <div class="w-10 h-10 rounded-xl ${isDone ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-slate-800 text-sky-400 border border-slate-700'} flex items-center justify-center font-bold text-lg flex-shrink-0">
          <i data-lucide="${q.icon || 'target'}" class="w-5 h-5"></i>
        </div>
        <div class="space-y-1.5 flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <h4 class="font-bold text-xs sm:text-sm text-white">${escapeHtml(q.title)}</h4>
            <span class="px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/30 text-amber-300 font-bold text-[10px] font-mono">+${q.reward_stars} ⭐</span>
            <span class="px-2 py-0.5 rounded-md bg-sky-500/15 border border-sky-500/30 text-sky-300 font-bold text-[10px] font-mono">+${q.reward_xp} XP</span>
          </div>
          <p class="text-xs text-slate-400 leading-snug">${escapeHtml(q.description)}</p>
          
          <!-- Progress Bar -->
          <div class="space-y-1 pt-1 max-w-md">
            <div class="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>Прогресс: ${q.progress} из ${q.target_count}</span>
              <span class="${isDone ? 'text-amber-400 font-bold' : 'text-slate-400'}">${percent}%</span>
            </div>
            <div class="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
              <div class="h-full rounded-full transition-all duration-500 ${isDone ? 'bg-gradient-to-r from-amber-500 to-yellow-400' : 'bg-gradient-to-r from-sky-500 to-indigo-500'}" style="width: ${percent}%;"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="flex-shrink-0 self-end sm:self-center">
        ${actionButtonHtml}
      </div>
    `;

    container.appendChild(card);
  });

  lucide.createIcons();
}

async function claimQuestReward(questId) {
  try {
    const res = await fetch('/api/quests/claim', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ quest_id: questId })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`🎁 Награда получена: +${data.reward_stars} ⭐ и +${data.reward_xp} XP!`);
      await loadUserProfile();
      await loadDailyQuests();
      if (currentTab === 'leaderboard') loadLeaderboard();
    } else {
      showToast(data.detail || 'Не удалось забрать награду');
    }
  } catch (err) {
    showToast('Ошибка при получении награды');
  }
}

function startQuestResetTimer(initialSeconds) {
  let secondsRemaining = Math.max(0, initialSeconds);

  if (questResetTimerInterval) {
    clearInterval(questResetTimerInterval);
  }

  const updateDisplay = () => {
    const hours = Math.floor(secondsRemaining / 3600);
    const minutes = Math.floor((secondsRemaining % 3600) / 60);
    const seconds = secondsRemaining % 60;
    const formatted = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    
    const timerElem = document.getElementById('daily-quests-timer');
    if (timerElem) {
      timerElem.innerText = formatted;
    }

    if (secondsRemaining <= 0) {
      clearInterval(questResetTimerInterval);
      loadDailyQuests();
    } else {
      secondsRemaining--;
    }
  };

  updateDisplay();
  questResetTimerInterval = setInterval(updateDisplay, 1000);
}

function scrollToDailyQuests() {
  switchTab('practice');
  setTimeout(() => {
    const sec = document.getElementById('daily-quests-section');
    if (sec) {
      sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, 100);
}


// ==========================================
// --- CREATOR & DEVELOPER DEV PANEL (CHEVELS) ---
// ==========================================

// ==========================================
// --- CREATOR & DEVELOPER DEV PANEL (CHEVELS) ---
// ==========================================

let devPanelActiveTab = 'stars';
let devLoadedIdeas = [];
window.devLoadedRoles = [
  { id: 'creator', name: 'Создатель', icon: 'crown', color_class: 'from-amber-500/25 via-orange-500/25 to-rose-500/25 border-amber-500/60 text-amber-300', is_builtin: true },
  { id: 'admin', name: 'Администратор', icon: 'shield-alert', color_class: 'bg-red-500/20 border-red-500/50 text-red-300', is_builtin: true },
  { id: 'moderator', name: 'Модератор', icon: 'shield-check', color_class: 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300', is_builtin: true },
  { id: 'vip', name: 'VIP / Pro', icon: 'sparkles', color_class: 'bg-purple-500/20 border-purple-500/50 text-purple-300', is_builtin: true },
  { id: 'mentor', name: 'Эксперт & Ментор', icon: 'brain', color_class: 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300', is_builtin: true },
  { id: 'user', name: 'Пользователь', icon: 'user', color_class: 'text-slate-400 border-slate-700 bg-slate-800/40', is_builtin: true }
];

async function openDevPanelModal() {
  if (!currentUser || !isDeveloperUser(currentUser)) {
    showToast('⛔ Доступ к Дев-панели разрешен только Создателю Chevels');
    return;
  }
  const modal = document.getElementById('dev-panel-modal');
  if (!modal) return;

  modal.classList.remove('hidden');
  await loadDevRolesList(true); // background load roles
  switchDevPanelTab(devPanelActiveTab || 'stars');
  lucide.createIcons();
}

function closeDevPanelModal() {
  const modal = document.getElementById('dev-panel-modal');
  if (modal) modal.classList.add('hidden');
}

function switchDevPanelTab(tabName) {
  devPanelActiveTab = tabName;

  // Update tabs buttons
  document.querySelectorAll('.dev-panel-nav-btn').forEach(btn => {
    btn.classList.remove('active', 'text-amber-400', 'bg-amber-500/15', 'border-amber-500/30');
    btn.classList.add('text-slate-400', 'border-transparent');
  });
  const activeBtn = document.getElementById(`dev-tab-btn-${tabName}`);
  if (activeBtn) {
    activeBtn.classList.add('active', 'text-amber-400', 'bg-amber-500/15', 'border-amber-500/30');
    activeBtn.classList.remove('text-slate-400', 'border-transparent');
  }

  // Update tabs content
  document.querySelectorAll('.dev-panel-content-tab').forEach(tab => {
    tab.classList.add('hidden');
  });
  const activeContent = document.getElementById(`dev-tab-${tabName}`);
  if (activeContent) {
    activeContent.classList.remove('hidden');
  }

  // Lazy loaders
  if (tabName === 'titles') {
    loadDevGrantTitlesSelect();
  } else if (tabName === 'roles') {
    loadDevRolesList();
  } else if (tabName === 'ideas') {
    loadDevIdeasSelect();
  } else if (tabName === 'users') {
    loadDevUsersTable();
  }

  lucide.createIcons();
}

// --- TAB 1: STARS & BALANCE ---
async function handleDevAddStars(amount) {
  const targetUser = document.getElementById('dev-stars-target-user')?.value.trim() || 'Chevels';
  try {
    const res = await fetch('/api/dev/stars/modify', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        username: targetUser,
        amount: amount
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`⭐ Пользователю ${targetUser} начислено +${amount.toLocaleString()} звезд! Новый баланс: ${data.user_stars.toLocaleString()}`);
      await loadUserProfile();
      if (currentTab === 'leaderboard') loadLeaderboard();
    } else {
      alert(data.detail || 'Ошибка изменения баланса');
    }
  } catch (err) {
    alert(err.message);
  }
}

async function handleDevSetStarsSubmit(exactAmount) {
  const targetUser = document.getElementById('dev-stars-target-user')?.value.trim() || 'Chevels';
  try {
    const res = await fetch('/api/dev/stars/modify', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        username: targetUser,
        exact_amount: exactAmount
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`⭐ Баланс ${targetUser} установлен на ${exactAmount.toLocaleString()} звезд!`);
      await loadUserProfile();
      if (currentTab === 'leaderboard') loadLeaderboard();
    } else {
      alert(data.detail || 'Ошибка изменения баланса');
    }
  } catch (err) {
    alert(err.message);
  }
}

function handleDevCustomSetStars() {
  const input = document.getElementById('dev-exact-stars-input');
  const val = parseInt(input?.value);
  if (isNaN(val) || val < 0) {
    alert('Пожалуйста, введите корректное число звезд (от 0 до 999999)');
    return;
  }
  handleDevSetStarsSubmit(val);
}

// --- TAB 2: TITLES MANAGEMENT & GRANTING ---
async function loadDevGrantTitlesSelect() {
  const select = document.getElementById('dev-grant-title-select');
  if (!select) return;

  try {
    const res = await fetch('/api/practice/profile', { headers: getAuthHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    const titles = data.shop_titles || [];

    select.innerHTML = '';
    titles.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.innerText = `${t.icon || '👑'} ${t.name} (${t.rarity} - ${t.cost_stars} ⭐)`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Ошибка загрузки титулов для выдачи:', err);
  }
}

function onDevGrantToAllToggle(isChecked) {
  const targetInput = document.getElementById('dev-grant-target-username');
  if (!targetInput) return;
  if (isChecked) {
    targetInput.value = '';
    targetInput.disabled = true;
    targetInput.placeholder = '👑 Будет выдано ВСЕМ пользователям платформы';
    targetInput.classList.add('opacity-50', 'bg-slate-950');
  } else {
    targetInput.disabled = false;
    targetInput.placeholder = 'Логин (например, AlexPy)';
    targetInput.classList.remove('opacity-50', 'bg-slate-950');
  }
}

async function handleDevGrantTitleSubmit(event) {
  event.preventDefault();
  const titleId = document.getElementById('dev-grant-title-select')?.value;
  const username = document.getElementById('dev-grant-target-username')?.value.trim();
  const grantToAll = document.getElementById('dev-grant-to-all-check')?.checked || false;
  const setActive = document.getElementById('dev-grant-set-active-check')?.checked || false;

  if (!titleId) {
    alert('Выберите титул для выдачи');
    return;
  }

  if (!grantToAll && !username) {
    alert('Укажите логин пользователя или включите опцию «Выдать ВСЕМ»');
    return;
  }

  try {
    const res = await fetch('/api/dev/titles/grant', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        title_id: titleId,
        username: username,
        grant_to_all: grantToAll,
        set_active: setActive
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message || 'Титул успешно выдан!');
      await loadUserProfile();
      if (currentTab === 'leaderboard') loadLeaderboard();
      if (currentTab === 'forum') loadForumTopics();
      if (devPanelActiveTab === 'users') loadDevUsersTable();
    } else {
      alert(data.detail || 'Ошибка при выдаче титула');
    }
  } catch (err) {
    alert(err.message);
  }
}

function quickDevOpenGrantTitleForUser(targetUsername) {
  switchDevPanelTab('titles');
  setTimeout(() => {
    const userInput = document.getElementById('dev-grant-target-username');
    const toAllCheck = document.getElementById('dev-grant-to-all-check');
    if (userInput) {
      userInput.value = targetUsername;
      userInput.disabled = false;
    }
    if (toAllCheck) {
      toAllCheck.checked = false;
    }
    userInput?.focus();
  }, 100);
}

async function handleDevCreateTitleSubmit(event) {
  event.preventDefault();
  const id = document.getElementById('dev-title-id').value.trim();
  const name = document.getElementById('dev-title-name').value.trim();
  const icon = document.getElementById('dev-title-icon').value.trim() || '⚡';
  const rarity = document.getElementById('dev-title-rarity').value;
  const cost = parseInt(document.getElementById('dev-title-cost').value) || 0;
  const description = document.getElementById('dev-title-desc').value.trim();
  const color = document.getElementById('dev-title-color').value;
  const autoUnlock = document.getElementById('dev-title-auto-unlock').checked;

  try {
    const res = await fetch('/api/dev/titles/create', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        id,
        name,
        icon,
        rarity,
        cost_stars: cost,
        description,
        color_class: color,
        auto_unlock_for_creator: autoUnlock
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`👑 Титул «${name}» успешно создан и добавлен в Каталог!`);
      document.getElementById('dev-title-id').value = '';
      document.getElementById('dev-title-name').value = '';
      document.getElementById('dev-title-desc').value = '';
      await loadUserProfile();
      loadDevGrantTitlesSelect();
    } else {
      alert(data.detail || 'Ошибка создания титула');
    }
  } catch (err) {
    alert(err.message);
  }
}

// --- TAB: CUSTOM ROLES MANAGEMENT ---
async function loadDevRolesList(silent = false) {
  try {
    const res = await fetch('/api/dev/roles', { headers: getAuthHeaders() });
    if (!res.ok) return;
    const roles = await res.json();
    window.devLoadedRoles = roles;

    if (!silent) {
      renderDevRolesList(roles);
    }
  } catch (err) {
    console.error('Ошибка загрузки ролей:', err);
  }
}

function renderDevRolesList(roles) {
  const container = document.getElementById('dev-roles-list-container');
  if (!container) return;
  container.innerHTML = '';

  roles.forEach(r => {
    const card = document.createElement('div');
    const isBuiltin = r.is_builtin;
    const isCreatorRole = r.id === 'creator';
    card.className = `p-3.5 rounded-xl border flex items-center justify-between gap-3 ${isBuiltin ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-900/90 border-sky-500/40 shadow-sm'}`;
    
    card.innerHTML = `
      <div class="space-y-1 min-w-0 flex-1">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border text-[11px] font-extrabold ${r.color_class || 'bg-slate-800 text-white'}">
            <i data-lucide="${r.icon || 'shield'}" class="w-3.5 h-3.5 flex-shrink-0"></i>
            <span>${escapeHtml(r.name)}</span>
          </span>
          <span class="font-mono text-[10px] text-slate-400">id: ${escapeHtml(r.id)}</span>
          ${isBuiltin ? '<span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">Системная</span>' : '<span class="text-[9px] px-1.5 py-0.2 rounded bg-sky-500/20 text-sky-300 font-bold border border-sky-500/30">Кастомная ✨</span>'}
        </div>
        ${r.description ? `<p class="text-[11px] text-slate-400 truncate">${escapeHtml(r.description)}</p>` : ''}
      </div>

      <div class="flex-shrink-0">
        ${!isBuiltin ? `
          <button onclick="handleDevDeleteRole('${escapeHtml(r.id)}')" title="Удалить роль" class="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 transition text-xs flex items-center gap-1">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            <span>Удалить</span>
          </button>
        ` : `
          <span class="text-[10px] text-slate-600 font-mono">Защищена</span>
        `}
      </div>
    `;
    container.appendChild(card);
  });
  lucide.createIcons();
}

async function handleDevCreateRoleSubmit(event) {
  event.preventDefault();
  const id = document.getElementById('dev-role-id').value.trim();
  const name = document.getElementById('dev-role-name').value.trim();
  const icon = document.getElementById('dev-role-icon').value.trim() || 'award';
  const colorClass = document.getElementById('dev-role-color').value;
  const desc = document.getElementById('dev-role-desc').value.trim();

  if (!id || !name) {
    alert('Заполните ID и название роли');
    return;
  }

  try {
    const res = await fetch('/api/dev/roles/create', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        id: id,
        name: name,
        icon: icon,
        color_class: colorClass,
        description: desc
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`🛡️ Роль «${name}» успешно создана и доступна для выдачи!`);
      document.getElementById('dev-role-id').value = '';
      document.getElementById('dev-role-name').value = '';
      document.getElementById('dev-role-desc').value = '';
      await loadDevRolesList();
      if (devPanelActiveTab === 'users') loadDevUsersTable();
    } else {
      alert(data.detail || 'Ошибка создания роли');
    }
  } catch (err) {
    alert(err.message);
  }
}

async function handleDevDeleteRole(roleId) {
  if (!confirm(`Вы действительно хотите удалить кастомную роль «${roleId}»? У пользователей с этой ролью права вернутся к стандартным.`)) {
    return;
  }

  try {
    const res = await fetch('/api/dev/roles/delete', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ role_id: roleId })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message || 'Роль успешно удалена');
      await loadDevRolesList();
      if (devPanelActiveTab === 'users') loadDevUsersTable();
    } else {
      alert(data.detail || 'Ошибка удаления роли');
    }
  } catch (err) {
    alert(err.message);
  }
}

// --- TAB 3: PRACTICE TASKS GENERATOR ---
async function handleDevCreateTaskSubmit(event) {
  event.preventDefault();
  const id = document.getElementById('dev-task-id').value.trim();
  const title = document.getElementById('dev-task-title').value.trim();
  const category = document.getElementById('dev-task-category').value;
  const difficulty = document.getElementById('dev-task-difficulty').value;
  const xpReward = parseInt(document.getElementById('dev-task-xp').value) || 100;
  const starsReward = parseInt(document.getElementById('dev-task-stars').value) || 25;
  const description = document.getElementById('dev-task-desc').value.trim();
  const starterCode = document.getElementById('dev-task-starter').value;
  const testInput = document.getElementById('dev-task-test-input').value.trim();
  const expectedOutput = document.getElementById('dev-task-expected').value.trim();

  const testCases = [];
  if (testInput || expectedOutput) {
    testCases.push({
      input: testInput,
      expected: expectedOutput,
      name: 'Базовый тест кейс'
    });
  }

  try {
    const res = await fetch('/api/dev/tasks/create', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        id,
        title,
        category,
        difficulty,
        xp_reward: xpReward,
        stars_reward: starsReward,
        description,
        starter_code: starterCode,
        test_cases: testCases
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`💻 Задание «${title}» успешно добавлено в Тренажёр!`);
      document.getElementById('dev-task-id').value = '';
      document.getElementById('dev-task-title').value = '';
      document.getElementById('dev-task-desc').value = '';
      await loadPracticeTasks();
    } else {
      alert(data.detail || 'Ошибка создания задания');
    }
  } catch (err) {
    alert(err.message);
  }
}

// --- TAB 4: IDEAS MODERATION ---
async function loadDevIdeasSelect() {
  const select = document.getElementById('dev-ideas-select');
  if (!select) return;

  select.innerHTML = '<option value="">-- Загрузка предложений... --</option>';

  try {
    const res = await fetch('/api/ideas/list?status=all&sort_by=new', {
      headers: getAuthHeaders()
    });
    const ideas = await res.json();
    devLoadedIdeas = Array.isArray(ideas) ? ideas : [];

    if (devLoadedIdeas.length === 0) {
      select.innerHTML = '<option value="">(Пока нет предложений от сообщества)</option>';
      return;
    }

    select.innerHTML = '<option value="">-- Выберите предложение из списка --</option>';
    devLoadedIdeas.forEach(idea => {
      const opt = document.createElement('option');
      opt.value = idea.id;
      opt.innerText = `[${(idea.status || 'under_review').toUpperCase()}] ${idea.title} (от @${idea.author_username})`;
      select.appendChild(opt);
    });
  } catch (err) {
    select.innerHTML = '<option value="">Ошибка загрузки предложений</option>';
  }
}

function onDevIdeaSelected() {
  const select = document.getElementById('dev-ideas-select');
  const ideaId = select.value;
  const preview = document.getElementById('dev-selected-idea-preview');
  const authorTag = document.getElementById('dev-idea-author-tag');
  const dateTag = document.getElementById('dev-idea-date-tag');
  const descPreview = document.getElementById('dev-idea-desc-preview');
  const statusSelect = document.getElementById('dev-idea-new-status');
  const responseInput = document.getElementById('dev-idea-response-text');

  if (!ideaId) {
    preview.classList.add('hidden');
    return;
  }

  const idea = devLoadedIdeas.find(i => i.id === ideaId);
  if (!idea) return;

  preview.classList.remove('hidden');
  authorTag.innerText = `Автор: @${idea.author_username} (${idea.author_display_name || ''})`;
  dateTag.innerText = idea.created_at ? idea.created_at.split('T')[0] : '';
  descPreview.innerText = idea.description;

  if (statusSelect) statusSelect.value = idea.status || 'under_review';
  if (responseInput) responseInput.value = idea.dev_response || '';
}

async function handleDevRespondIdeaSubmit(event) {
  event.preventDefault();
  const select = document.getElementById('dev-ideas-select');
  const ideaId = select.value;
  const status = document.getElementById('dev-idea-new-status').value;
  const devResponse = document.getElementById('dev-idea-response-text').value.trim();

  if (!ideaId) {
    alert('Пожалуйста, выберите предложение для ответа');
    return;
  }

  try {
    const res = await fetch('/api/dev/ideas/status', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        idea_id: ideaId,
        status: status,
        dev_response: devResponse
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Ответ Создателя и статус предложения успешно обновлены! 💡');
      await loadIdeas();
      await loadDevIdeasSelect();
    } else {
      alert(data.detail || 'Ошибка обновления статуса');
    }
  } catch (err) {
    alert(err.message);
  }
}

// --- TAB 5: ALL USERS LIST & ROLES ASSIGNMENT ---
async function loadDevUsersTable() {
  const tbody = document.getElementById('dev-users-table-body');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-slate-500">Загрузка пользователей...</td></tr>';

  try {
    // Make sure we have the latest roles
    if (!window.devLoadedRoles || window.devLoadedRoles.length === 0) {
      await loadDevRolesList(true);
    }

    const res = await fetch('/api/dev/users', {
      headers: getAuthHeaders()
    });
    const data = await res.json();
    const users = Array.isArray(data) ? data : (data.users || []);

    if (!Array.isArray(users) || users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-slate-500">Пользователи не найдены</td></tr>';
      return;
    }

    const allRoles = window.devLoadedRoles || [];

    tbody.innerHTML = '';
    users.forEach(u => {
      const isCreator = (u.username || '').toLowerCase() === 'chevels' || u.role === 'creator';
      const currentRole = u.role || (isCreator ? 'creator' : 'user');
      if (u.username) {
        window.allUsersRoleCache[u.username.toLowerCase()] = currentRole;
      }
      const badgeHtml = getUserBadgeHtml(u);

      // Build options from all available roles
      let roleOptionsHtml = '';
      allRoles.forEach(r => {
        roleOptionsHtml += `<option value="${escapeHtml(r.id)}" ${currentRole === r.id ? 'selected' : ''}>${escapeHtml(r.name)} (${escapeHtml(r.id)})</option>`;
      });

      // If current role is not in list
      if (!allRoles.some(r => r.id === currentRole)) {
        roleOptionsHtml += `<option value="${escapeHtml(currentRole)}" selected>${escapeHtml(currentRole)}</option>`;
      }

      const row = document.createElement('tr');
      row.className = 'hover:bg-slate-900/60 transition';
      row.innerHTML = `
        <td class="p-2.5 flex items-center gap-2">
          <img src="${u.avatar || `https://api.dicebear.com/7.x/bottts/svg?seed=${u.username}`}" class="w-7 h-7 rounded-lg border ${isCreator ? 'border-amber-400 shadow-sm shadow-amber-500/20' : 'border-slate-700'} bg-slate-950 object-cover flex-shrink-0">
          <div class="leading-tight min-w-0">
            <div class="font-bold text-white flex items-center gap-1.5 flex-wrap">
              <span>${escapeHtml(u.display_name || u.username)}</span>
              ${badgeHtml}
            </div>
            <div class="text-[10px] text-slate-400 font-mono">@${escapeHtml(u.username)}</div>
          </div>
        </td>
        <td class="p-2.5">
          <select onchange="handleDevChangeUserRole('${escapeHtml(u.username)}', this.value)" class="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-white text-[11px] font-bold focus:outline-none focus:border-amber-500 cursor-pointer">
            ${roleOptionsHtml}
          </select>
        </td>
        <td class="p-2.5 font-bold text-amber-400 font-mono">Ур. ${u.level || 1}</td>
        <td class="p-2.5 font-mono font-bold text-yellow-300">${(u.stars || 0).toLocaleString()} ⭐</td>
        <td class="p-2.5 font-mono text-sky-400">${(u.xp || 0).toLocaleString()} XP</td>
        <td class="p-2.5">
          <div class="flex items-center gap-1.5">
            <button onclick="quickDevOpenGrantTitleForUser('${escapeHtml(u.username)}')" title="Выдать титул этому пользователю" class="px-2 py-1 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 font-bold rounded-lg text-[10px] transition flex items-center gap-1">
              <i data-lucide="crown" class="w-3.5 h-3.5"></i>
              <span>Титул</span>
            </button>
            <button onclick="handleDevQuickGiveStarsToUser('${escapeHtml(u.username)}', 1000)" title="Начислить +1,000 ⭐" class="px-2 py-1 bg-slate-800 hover:bg-amber-500/15 border border-slate-700 hover:border-amber-500/30 text-amber-300 font-bold rounded-lg text-[10px] transition flex items-center gap-1">
              +1k ⭐
            </button>
            <button onclick="document.getElementById('dev-stars-target-user').value = '${escapeHtml(u.username)}'; switchDevPanelTab('stars');" title="Управлять точным балансом в табе Звёзды" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-semibold rounded-lg text-[10px] transition">
              ⚙️
            </button>
          </div>
        </td>
      `;
      tbody.appendChild(row);
    });
    lucide.createIcons();
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-red-400">Ошибка загрузки списка пользователей</td></tr>';
  }
}

async function handleDevChangeUserRole(username, newRole) {
  try {
    const res = await fetch('/api/dev/users/role', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        username: username,
        role: newRole
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`👑 Роль @${username} успешно изменена на «${newRole.toUpperCase()}»!`);
      window.allUsersRoleCache[username.toLowerCase()] = newRole;
      if (currentUser && currentUser.username.toLowerCase() === username.toLowerCase()) {
        currentUser.role = newRole;
        currentUser.is_developer = (newRole === 'creator' || newRole === 'admin' || username.toLowerCase() === 'chevels');
        updateHeaderUserWidget(currentUser);
        await loadUserProfile();
      }
      loadDevUsersTable();
      if (currentTab === 'leaderboard') loadLeaderboard();
      if (currentTab === 'forum') loadForumTopics();
      if (currentTab === 'ideas') loadIdeas();
    } else {
      alert(data.detail || 'Ошибка изменения роли');
      loadDevUsersTable();
    }
  } catch (err) {
    alert(err.message);
    loadDevUsersTable();
  }
}

async function handleDevQuickGiveStarsToUser(username, amount) {
  try {
    const res = await fetch('/api/dev/stars/modify', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        username: username,
        amount: amount
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`⭐ Пользователю @${username} начислено +${amount.toLocaleString()} звезд!`);
      loadDevUsersTable();
      if (currentUser && currentUser.username.toLowerCase() === username.toLowerCase()) {
        await loadUserProfile();
      }
    } else {
      alert(data.detail || 'Ошибка начисления звезд');
    }
  } catch (err) {
    alert(err.message);
  }
}

// --- TAB 6: BACKUP & RESTORE DATABASE ---
async function handleDevExportBackup() {
  try {
    const res = await fetch('/api/dev/backup/export', {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Ошибка экспорта бэкапа');
    }
    const backupData = await res.json();
    const jsonStr = JSON.stringify(backupData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const dateStr = new Date().toISOString().slice(0, 10);
    a.href = url;
    a.download = `pyforge_backup_${dateStr}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('💾 Резервная копия базы успешно скачана на ваш компьютер!');
  } catch (err) {
    alert(err.message);
  }
}

async function handleDevImportBackupFile(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  const confirmImport = confirm('Вы уверены, что хотите восстановить базу из этого файла? Текущие данные пользователей и сессий будут обновлены данными из бэкапа.');
  if (!confirmImport) {
    event.target.value = '';
    return;
  }

  try {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const backupData = JSON.parse(e.target.result);
        const res = await fetch('/api/dev/backup/import', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify(backupData)
        });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast(data.message || 'База данных успешно восстановлена! 🎉');
          await loadUserProfile();
          await loadDevRolesList(true);
          loadDevUsersTable();
          if (currentTab === 'leaderboard') loadLeaderboard();
          if (currentTab === 'forum') loadForumTopics();
          if (currentTab === 'ideas') loadIdeas();
        } else {
          alert(data.detail || 'Ошибка при восстановлении базы');
        }
      } catch (parseErr) {
        alert('Некорректный файл JSON: ' + parseErr.message);
      } finally {
        event.target.value = '';
      }
    };
    reader.readAsText(file, 'utf-8');
  } catch (err) {
    alert('Ошибка чтения файла: ' + err.message);
    event.target.value = '';
  }
}




