(() => {
  // ── State ──────────────────────────────────────────────────────────────
  let ws = null;
  let sessionId = null;
  let activeDimId = null;
  // dimChats: { [id]: { messages: [{role, content}], status, name, icon, prompt } }
  const dimChats = {};
  let allDimensions = [];

  // ── DOM refs ────────────────────────────────────────────────────────────
  const apiModal       = document.getElementById('api-modal');
  const apiKeyInput    = document.getElementById('api-key-input');
  const apiKeySubmit   = document.getElementById('api-key-submit');
  const apiKeyError    = document.getElementById('api-key-error');

  const addDimModal    = document.getElementById('add-dim-modal');
  const dimNameInput   = document.getElementById('dim-name-input');
  const dimIconInput   = document.getElementById('dim-icon-input');
  const addDimError    = document.getElementById('add-dim-error');
  const addDimCancel   = document.getElementById('add-dim-cancel');
  const addDimConfirm  = document.getElementById('add-dim-confirm');

  const wsDot          = document.getElementById('ws-status');
  const projectInput   = document.getElementById('project-input-section');
  const progressSec    = document.getElementById('progress-section');
  const projectDesc    = document.getElementById('project-desc');
  const startBtn       = document.getElementById('start-project-btn');
  const dimCheckboxes  = document.getElementById('dim-checkboxes');
  const toggleAllBtn   = document.getElementById('toggle-all-btn');
  const progressList   = document.getElementById('progress-list');
  const projectTitle   = document.getElementById('project-title-text');
  const finalizeBtn    = document.getElementById('finalize-btn');
  const resetBtn       = document.getElementById('reset-btn');

  const welcomeScreen  = document.getElementById('welcome-screen');
  const chatArea       = document.getElementById('chat-area');
  const tabsContainer  = document.getElementById('tabs-container');
  const addDimBtn      = document.getElementById('add-dim-btn');
  const chatWindow     = document.getElementById('chat-window');
  const chatInput      = document.getElementById('chat-input');
  const sendBtn        = document.getElementById('send-btn');

  const previewArea    = document.getElementById('preview-area');
  const previewActions = document.getElementById('preview-actions');
  const copyBtn        = document.getElementById('copy-btn');

  // ── Helpers ─────────────────────────────────────────────────────────────
  function show(el)  { el.classList.remove('hidden'); }
  function hide(el)  { el.classList.add('hidden'); }

  function setWsStatus(state) {
    wsDot.className = 'ws-dot ' + state;
    const labels = { connected: '연결됨', connecting: '연결 중', disconnected: '연결 안됨' };
    wsDot.title = labels[state] || state;
  }

  function showApiError(msg) {
    apiKeyError.textContent = msg;
    show(apiKeyError);
  }

  function generateId(name) {
    return name.toLowerCase().replace(/\s+/g, '_').replace(/[^\w]/g, '') + '_' + Date.now();
  }

  // ── Dimension checkbox list ──────────────────────────────────────────────
  async function loadDefaultDimensions() {
    try {
      const res = await fetch('/api/dimensions/defaults');
      const data = await res.json();
      allDimensions = data.dimensions;
    } catch {
      allDimensions = [
        { id: 'ux_design',    name: 'UI/UX 디자인',   icon: '🎨' },
        { id: 'architecture', name: '시스템 아키텍처', icon: '🏗️' },
        { id: 'database',     name: '데이터베이스 설계', icon: '🗄️' },
        { id: 'api',          name: 'API 설계',        icon: '🔌' },
        { id: 'deployment',   name: '배포 전략',       icon: '🚀' },
        { id: 'testing',      name: '테스트 전략',     icon: '✅' },
      ];
    }
    renderDimCheckboxes();
  }

  function renderDimCheckboxes() {
    dimCheckboxes.innerHTML = '';
    allDimensions.forEach(dim => {
      const label = document.createElement('label');
      label.className = 'dim-check-item';
      label.innerHTML = `
        <input type="checkbox" value="${dim.id}" checked />
        <span>${dim.icon} ${dim.name}</span>
      `;
      dimCheckboxes.appendChild(label);
    });
  }

  function getSelectedDimensions() {
    return allDimensions.filter(dim => {
      const cb = dimCheckboxes.querySelector(`input[value="${dim.id}"]`);
      return cb && cb.checked;
    });
  }

  let allChecked = true;
  toggleAllBtn.addEventListener('click', () => {
    allChecked = !allChecked;
    dimCheckboxes.querySelectorAll('input[type=checkbox]').forEach(cb => cb.checked = allChecked);
    toggleAllBtn.textContent = allChecked ? '모두 해제' : '모두 선택';
  });

  // ── Session / WebSocket ──────────────────────────────────────────────────
  async function createSession(apiKey) {
    const res = await fetch('/api/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '세션 생성 실패');
    return data.session_id;
  }

  function connectWs(sid) {
    setWsStatus('connecting');
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    ws = new WebSocket(`${proto}://${location.host}/ws/${sid}`);

    ws.onopen  = () => setWsStatus('connected');
    ws.onclose = () => setWsStatus('disconnected');
    ws.onerror = () => setWsStatus('disconnected');
    ws.onmessage = ({ data }) => handleServerMessage(JSON.parse(data));
  }

  function wsSend(obj) {
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj));
  }

  // ── API Key Flow ─────────────────────────────────────────────────────────
  apiKeySubmit.addEventListener('click', submitApiKey);
  apiKeyInput.addEventListener('keydown', e => { if (e.key === 'Enter') submitApiKey(); });

  async function submitApiKey() {
    const key = apiKeyInput.value.trim();
    if (!key) { showApiError('API 키를 입력해주세요.'); return; }
    apiKeySubmit.disabled = true;
    apiKeySubmit.textContent = '확인 중...';
    hide(apiKeyError);
    try {
      sessionId = await createSession(key);
      hide(apiModal);
      connectWs(sessionId);
      await loadDefaultDimensions();
    } catch (err) {
      showApiError(err.message);
    } finally {
      apiKeySubmit.disabled = false;
      apiKeySubmit.textContent = '시작하기';
    }
  }

  // ── Project Init ─────────────────────────────────────────────────────────
  startBtn.addEventListener('click', startProject);
  projectDesc.addEventListener('keydown', e => {
    if (e.key === 'Enter' && e.metaKey) startProject();
  });

  function startProject() {
    const desc = projectDesc.value.trim();
    if (!desc) { alert('프로젝트 설명을 입력해주세요.'); return; }
    const selectedDims = getSelectedDimensions();
    if (selectedDims.length === 0) { alert('최소 1개의 영역을 선택해주세요.'); return; }

    wsSend({ type: 'project_init', content: desc, dimensions: selectedDims });
    startBtn.disabled = true;
    startBtn.textContent = '시작 중...';
  }

  // ── Server Message Handler ────────────────────────────────────────────────
  function handleServerMessage(msg) {
    switch (msg.type) {
      case 'project_ready':       onProjectReady(msg); break;
      case 'dimension_question':  onDimQuestion(msg);  break;
      case 'dimension_status':    onDimStatus(msg);    break;
      case 'dimension_complete':  onDimComplete(msg);  break;
      case 'all_complete':        onAllComplete();     break;
      case 'final_document':      onFinalDocument(msg); break;
      case 'error':               onError(msg);        break;
    }
  }

  function onProjectReady(msg) {
    // Initialize dim chats
    msg.dimensions.forEach(d => {
      dimChats[d.id] = { 
        messages: [], 
        status: d.status, 
        name: d.name, 
        icon: d.icon, 
        prompt: d.generated_prompt || '' 
      };
    });

    projectTitle.textContent = msg.project_description;
    hide(projectInput);
    show(progressSec);
    hide(welcomeScreen);
    show(chatArea);

    renderProgressList(msg.dimensions);
    renderTabs(msg.dimensions);
    
    // Activate first tab
    if (msg.dimensions.length > 0) activateTab(msg.dimensions[0].id);
  }

  function onDimQuestion(msg) {
    const chat = dimChats[msg.dimension_id];
    if (!chat) return;
    chat.messages.push({ role: 'assistant', content: msg.content });
    if (activeDimId === msg.dimension_id) renderChatWindow(msg.dimension_id);
    updateTabBadge(msg.dimension_id, 'in_progress');
    updateProgressItem(msg.dimension_id, 'in_progress');
    scrollChat();
    setSending(false);
  }

  function onDimStatus(msg) {
    const chat = dimChats[msg.dimension_id];
    if (chat) chat.status = msg.status;
    updateTabBadge(msg.dimension_id, msg.status);
    updateProgressItem(msg.dimension_id, msg.status);
  }

  function onDimComplete(msg) {
    const chat = dimChats[msg.dimension_id];
    if (chat) { 
      chat.status = 'completed'; 
      chat.prompt = msg.prompt; 
    }
    updateTabBadge(msg.dimension_id, 'completed');
    updateProgressItem(msg.dimension_id, 'completed');
    
    // Only update preview if this dimension is currently active
    if (activeDimId === msg.dimension_id) {
      showPreview(msg.prompt);
    }
    
    // Unlock input bar
    setSending(false);
  }

  function onAllComplete() {
    finalizeBtn.classList.add('pulse');
  }

  function onFinalDocument(msg) {
    showPreview(msg.content);
    finalizeBtn.classList.remove('pulse');
    finalizeBtn.textContent = '✅ 문서 생성 완료';
  }

  function onError(msg) {
    appendMessage(activeDimId, 'error', '⚠️ ' + msg.message);
    setSending(false);
  }

  // ── Tabs ─────────────────────────────────────────────────────────────────
  function renderTabs(dimensions) {
    tabsContainer.innerHTML = '';
    dimensions.forEach(d => {
      const tab = document.createElement('button');
      tab.className = 'tab-btn';
      tab.dataset.id = d.id;
      tab.innerHTML = `<span class="tab-icon">${d.icon || '📋'}</span><span class="tab-name">${d.name}</span><span class="tab-badge pending"></span>`;
      tab.addEventListener('click', () => activateTab(d.id));
      tabsContainer.appendChild(tab);
    });
  }

  function activateTab(id) {
    activeDimId = id;
    tabsContainer.querySelectorAll('.tab-btn').forEach(t => {
      t.classList.toggle('active', t.dataset.id === id);
    });
    renderChatWindow(id);
    
    // Show preview for the active dimension only
    const chat = dimChats[id];
    if (chat && chat.prompt) {
      showPreview(chat.prompt);
    } else {
      showPreview(null); // Show placeholder
    }
    
    scrollChat();

    // If dimension is pending, start it
    if (chat && chat.status === 'pending' && chat.messages.length === 0) {
      wsSend({ type: 'start_dimension', dimension_id: id });
    }
  }

  function updateTabBadge(id, status) {
    const tab = tabsContainer.querySelector(`[data-id="${id}"]`);
    if (!tab) return;
    const badge = tab.querySelector('.tab-badge');
    badge.className = 'tab-badge ' + status;
    badge.title = { pending: '대기 중', in_progress: '진행 중', completed: '완료' }[status] || status;
  }

  function addTab(dim) {
    const tab = document.createElement('button');
    tab.className = 'tab-btn';
    tab.dataset.id = dim.id;
    tab.innerHTML = `<span class="tab-icon">${dim.icon || '📋'}</span><span class="tab-name">${dim.name}</span><span class="tab-badge pending"></span>`;
    tab.addEventListener('click', () => activateTab(dim.id));
    tabsContainer.appendChild(tab);
  }

  // ── Chat Window ───────────────────────────────────────────────────────────
  function renderChatWindow(id) {
    chatWindow.innerHTML = '';
    const chat = dimChats[id];
    if (!chat) return;
    if (chat.messages.length === 0) {
      chatWindow.innerHTML = '<p class="chat-placeholder">잠시 후 질문이 시작됩니다...</p>';
      return;
    }
    chat.messages.forEach(m => appendBubble(m.role, m.content));
  }

  function appendMessage(dimId, role, content) {
    if (!dimChats[dimId]) return;
    dimChats[dimId].messages.push({ role, content });
    if (activeDimId === dimId) appendBubble(role, content);
  }

  function appendBubble(role, content) {
    const wrap = document.createElement('div');
    wrap.className = 'msg-wrap ' + (role === 'user' ? 'user' : role === 'error' ? 'error' : 'assistant');
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = content;
    wrap.appendChild(bubble);
    chatWindow.appendChild(wrap);
  }

  function scrollChat() {
    setTimeout(() => { chatWindow.scrollTop = chatWindow.scrollHeight; }, 50);
  }

  // ── Chat Input ────────────────────────────────────────────────────────────
  sendBtn.addEventListener('click', sendMessage);
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
  });

  function sendMessage() {
    const text = chatInput.value.trim();
    if (!text || !activeDimId) return;
    const chat = dimChats[activeDimId];
    if (!chat) return; // Allow sending even if completed

    appendMessage(activeDimId, 'user', text);
    scrollChat();
    chatInput.value = '';
    chatInput.style.height = 'auto';
    setSending(true);

    wsSend({ type: 'dimension_message', dimension_id: activeDimId, content: text });
  }

  function setSending(bool) {
    sendBtn.disabled = bool;
    chatInput.disabled = bool;
    sendBtn.textContent = bool ? '...' : '전송';
  }

  // ── Progress List ─────────────────────────────────────────────────────────
  function renderProgressList(dimensions) {
    progressList.innerHTML = '';
    dimensions.forEach(d => {
      const item = document.createElement('div');
      item.className = 'progress-item';
      item.dataset.id = d.id;
      item.innerHTML = `<span class="progress-icon">${d.icon || '📋'}</span><span class="progress-name">${d.name}</span><span class="progress-status pending">대기</span>`;
      item.addEventListener('click', () => activateTab(d.id));
      progressList.appendChild(item);
    });
  }

  function updateProgressItem(id, status) {
    const item = progressList.querySelector(`[data-id="${id}"]`);
    if (!item) return;
    const s = item.querySelector('.progress-status');
    const labels = { pending: '대기', in_progress: '진행 중', completed: '완료' };
    s.className = 'progress-status ' + status;
    s.textContent = labels[status] || status;
  }

  // ── Preview ───────────────────────────────────────────────────────────────
  function showPreview(text) {
    previewArea.innerHTML = '';
    if (!text) {
      previewArea.innerHTML = '<p class="preview-placeholder">설계가 완료되면 여기에 프롬프트가 표시됩니다.</p>';
      hide(previewActions);
      return;
    }
    const pre = document.createElement('pre');
    pre.className = 'preview-content';
    pre.textContent = text;
    previewArea.appendChild(pre);
    show(previewActions);
  }

  copyBtn.addEventListener('click', () => {
    const text = previewArea.querySelector('pre')?.textContent || '';
    navigator.clipboard.writeText(text).then(() => {
      copyBtn.textContent = '복사됨!';
      setTimeout(() => { copyBtn.textContent = '복사'; }, 2000);
    });
  });

  // ── Finalize ──────────────────────────────────────────────────────────────
  finalizeBtn.addEventListener('click', () => {
    finalizeBtn.disabled = true;
    finalizeBtn.textContent = '생성 중...';
    wsSend({ type: 'finalize' });
  });

  resetBtn.addEventListener('click', () => {
    location.reload();
  });

  // ── Add Dimension ─────────────────────────────────────────────────────────
  addDimBtn.addEventListener('click', () => {
    dimNameInput.value = '';
    dimIconInput.value = '';
    hide(addDimError);
    show(addDimModal);
  });

  addDimCancel.addEventListener('click', () => hide(addDimModal));

  addDimConfirm.addEventListener('click', () => {
    const name = dimNameInput.value.trim();
    const icon = dimIconInput.value.trim() || '📋';
    if (!name) { addDimError.textContent = '영역 이름을 입력해주세요.'; show(addDimError); return; }

    const id = generateId(name);
    const config = { id, name, icon };

    dimChats[id] = { messages: [], status: 'pending', name, icon, prompt: '' };
    addTab(config);

    const progressItem = document.createElement('div');
    progressItem.className = 'progress-item';
    progressItem.dataset.id = id;
    progressItem.innerHTML = `<span class="progress-icon">${icon}</span><span class="progress-name">${name}</span><span class="progress-status pending">대기</span>`;
    progressItem.addEventListener('click', () => activateTab(id));
    progressList.appendChild(progressItem);

    wsSend({ type: 'add_dimension', config });
    hide(addDimModal);
    activateTab(id);
  });

  // kick off
  loadDefaultDimensions();

  // ── Panel Resize ──────────────────────────────────────────────────────────
  function initPanelResize(handleId, panelId, side) {
    const handle = document.getElementById(handleId);
    const panel  = document.getElementById(panelId);
    if (!handle || !panel) return;

    handle.addEventListener('mousedown', e => {
      e.preventDefault();
      const startX = e.clientX;
      const startW = panel.getBoundingClientRect().width;
      
      handle.classList.add('dragging');
      document.body.classList.add('is-dragging');

      const onMove = (moveEvent) => {
        const delta = side === 'left' 
          ? moveEvent.clientX - startX 
          : startX - moveEvent.clientX;
        
        // Dynamic limits based on window width could be added, but simple min is enough
        const newW = Math.max(startW + delta, 200); 
        const prop = side === 'left' ? '--left-w' : '--right-w';
        
        document.documentElement.style.setProperty(prop, newW + 'px');
      };

      const onUp = () => {
        handle.classList.remove('dragging');
        document.body.classList.remove('is-dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      };

      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });
  }

  initPanelResize('resize-left',  'left-panel',  'left');
  initPanelResize('resize-right', 'right-panel', 'right');

  // ── Zoom Controls ─────────────────────────────────────────────────────────
  const ZOOM_SIZES = [14, 16, 18, 20, 22, 24, 26, 28];
  let zoomIdx = ZOOM_SIZES.indexOf(20); // default 20px = 100%

  function applyZoom() {
    const px   = ZOOM_SIZES[zoomIdx];
    const pct  = Math.round((px / 20) * 100);
    document.documentElement.style.setProperty('--base-font', px + 'px');
    document.getElementById('zoom-label').textContent = pct + '%';
  }

  document.getElementById('zoom-in').addEventListener('click', () => {
    if (zoomIdx < ZOOM_SIZES.length - 1) { zoomIdx++; applyZoom(); }
  });
  document.getElementById('zoom-out').addEventListener('click', () => {
    if (zoomIdx > 0) { zoomIdx--; applyZoom(); }
  });
})();
