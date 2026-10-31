// ==============================================================================
// FinAssistant AI - Frontend Application Logic (Vanilla JS)
// ==============================================================================

// 백엔드 API 기본 주소 (로컬 또는 Vercel 배포 시 환경 설정 지원)
const API_BASE_URL = window.API_BASE_URL || "";

// 전역 상태
let currentConversationId = null;
let currentSummary = null;

// ==============================================================================
// 1. 초기화 및 이벤트 리스너 등록
// ==============================================================================
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  checkHealth();
  loadDataSummary();
  loadDataList();
  loadConversationList();
  setupEventListeners();

  // 날짜 입력창 기본값: 오늘 날짜
  const today = new Date().toISOString().split("T")[0];
  const addDateInput = document.getElementById("add-date");
  if (addDateInput) addDateInput.value = today;
});

function setupEventListeners() {
  // 다크 모드 토글
  const themeBtn = document.getElementById("theme-toggle-btn");
  if (themeBtn) themeBtn.addEventListener("click", toggleTheme);

  // 채팅 전송
  const chatForm = document.getElementById("chat-form");
  if (chatForm) chatForm.addEventListener("submit", handleChatSubmit);

  // 새 대화 시작 버튼
  const newChatBtn = document.getElementById("btn-new-chat");
  if (newChatBtn) newChatBtn.addEventListener("click", startNewChat);

  // 이전 대화 선택 (불러오기)
  const convSelector = document.getElementById("conv-selector");
  if (convSelector) convSelector.addEventListener("change", handleConversationChange);

  // 대화 삭제 버튼
  const deleteConvBtn = document.getElementById("btn-delete-conv");
  if (deleteConvBtn) deleteConvBtn.addEventListener("click", handleDeleteCurrentConversation);

  // 추천 질문 버튼들
  document.querySelectorAll(".suggestion-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const query = e.target.getAttribute("data-query");
      const input = document.getElementById("chat-input");
      if (input && query) {
        input.value = query;
        input.focus();
      }
    });
  });

  // 데이터 추가 폼 제출
  const addForm = document.getElementById("add-data-form");
  if (addForm) addForm.addEventListener("submit", handleAddData);

  // 데이터 목록 새로고침 버튼
  const refreshBtn = document.getElementById("btn-refresh-data");
  if (refreshBtn) refreshBtn.addEventListener("click", () => {
    loadDataSummary();
    loadDataList();
  });

  // 모달 닫기
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const modalCancelBtn = document.getElementById("modal-cancel-btn");
  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeEditModal);
  if (modalCancelBtn) modalCancelBtn.addEventListener("click", closeEditModal);

  // 데이터 수정 폼 제출
  const editForm = document.getElementById("edit-form");
  if (editForm) editForm.addEventListener("submit", handleEditDataSubmit);
}

// ==============================================================================
// 2. 보너스 과제: 다크 모드 토글 로직
// ==============================================================================
function initTheme() {
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const initialTheme = savedTheme || (prefersDark ? "dark" : "light");

  applyTheme(initialTheme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  applyTheme(next);
  localStorage.setItem("theme", next);
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const icon = document.getElementById("theme-icon");
  const text = document.getElementById("theme-text");
  if (icon && text) {
    if (theme === "dark") {
      icon.textContent = "☀️";
      text.textContent = "라이트 모드";
    } else {
      icon.textContent = "🌙";
      text.textContent = "다크 모드";
    }
  }
}

// ==============================================================================
// 3. 서버 헬스체크 및 요약 통계 로드
// ==============================================================================
async function checkHealth() {
  const statusEl = document.getElementById("system-status");
  const statusText = document.getElementById("status-text");

  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (res.ok) {
      const data = await res.json();
      statusText.textContent = data.firebase_connected ? "Firestore 연결됨" : "로컬 모드(정상)";
    } else {
      statusText.textContent = "서버 응답 오류";
      statusEl.style.color = "var(--danger)";
    }
  } catch (err) {
    statusText.textContent = "서버 오프라인";
    statusEl.style.color = "var(--danger)";
  }
}

async function loadDataSummary() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/summary`);
    if (!res.ok) throw new Error("요약 데이터 조회 실패");

    currentSummary = await res.json();

    document.getElementById("summary-period").textContent = currentSummary.period || "-";
    document.getElementById("summary-count").textContent = `${currentSummary.count.toLocaleString()}개`;
    document.getElementById("summary-avg").textContent = `${currentSummary.metrics.average.toLocaleString()}원`;
    document.getElementById("summary-minmax").textContent =
      `최저: ${currentSummary.metrics.min.toLocaleString()}원 / 최고: ${currentSummary.metrics.max.toLocaleString()}원`;

    const trendEl = document.getElementById("summary-trend");
    trendEl.textContent = currentSummary.trend || "-";
  } catch (err) {
    console.error("요약 정보 로드 에러:", err);
  }
}

// ==============================================================================
// 4. AI 챗봇 기능 (컨텍스트 주입 & 대화)
// ==============================================================================
async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;

  // 1. 사용자 말풍선 추가
  appendMessage("user", message);
  input.value = "";

  // 2. 로딩 표시 및 입력 비활성화
  const loadingEl = document.getElementById("chat-loading");
  const submitBtn = document.getElementById("chat-submit-btn");
  loadingEl.style.display = "flex";
  submitBtn.disabled = true;

  try {
    // 3. POST /api/chat 요청
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        conversation_id: currentConversationId
      })
    });

    if (!res.ok) {
      throw new Error(`서버 응답 에러: ${res.status}`);
    }

    const data = await res.json();

    // 4. 세션 ID 업데이트
    currentConversationId = data.conversation_id;

    // 5. AI 답변 말풍선 추가
    appendMessage("assistant", data.reply);

    // 6. 대화 목록 갱신
    await loadConversationList();
    document.getElementById("conv-selector").value = currentConversationId;
    document.getElementById("btn-delete-conv").style.display = "inline-block";

  } catch (err) {
    console.error("채팅 오류:", err);
    appendMessage("assistant", `⚠️ 오류가 발생했습니다: ${err.message}`);
  } finally {
    loadingEl.style.display = "none";
    submitBtn.disabled = false;
  }
}

function appendMessage(role, text) {
  const messagesBox = document.getElementById("chat-messages");
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble bubble-${role}`;
  bubble.textContent = text;
  messagesBox.appendChild(bubble);
  messagesBox.scrollTop = messagesBox.scrollHeight;
}

function startNewChat() {
  currentConversationId = null;
  const messagesBox = document.getElementById("chat-messages");
  messagesBox.innerHTML = `
    <div class="chat-bubble bubble-assistant">
      새 대화를 시작합니다. 시계열 데이터 요약을 바탕으로 맞춤형 분석을 질문해 보세요!
    </div>
  `;
  document.getElementById("conv-selector").value = "";
  document.getElementById("btn-delete-conv").style.display = "none";
}

// ==============================================================================
// 5. 대화 기록 관리 (불러오기 & 목록 조회 & 삭제)
// ==============================================================================
async function loadConversationList() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations`);
    if (!res.ok) return;

    const convs = await res.json();
    const selector = document.getElementById("conv-selector");
    const currentVal = selector.value;

    selector.innerHTML = '<option value="">-- 대화 기록 선택 --</option>';
    convs.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      const datePart = c.created_at ? c.created_at.substring(5, 16).replace("T", " ") : "";
      opt.textContent = `[${datePart}] ${c.title}`;
      selector.appendChild(opt);
    });

    if (currentVal) {
      selector.value = currentVal;
    }
  } catch (err) {
    console.error("대화 목록 로드 실패:", err);
  }
}

async function handleConversationChange(e) {
  const selectedId = e.target.value;
  if (!selectedId) {
    startNewChat();
    return;
  }

  try {
    // GET /api/conversations/{id}
    const res = await fetch(`${API_BASE_URL}/api/conversations/${selectedId}`);
    if (!res.ok) throw new Error("대화 상세 조회 실패");

    const conv = await res.json();
    currentConversationId = conv.id;

    // 대화창 복원
    const messagesBox = document.getElementById("chat-messages");
    messagesBox.innerHTML = "";

    if (conv.messages && conv.messages.length > 0) {
      conv.messages.forEach(msg => {
        appendMessage(msg.role, msg.content);
      });
    } else {
      appendMessage("assistant", "저장된 대화 메시지가 없습니다.");
    }

    document.getElementById("btn-delete-conv").style.display = "inline-block";
  } catch (err) {
    alert("대화를 불러오지 못했습니다: " + err.message);
  }
}

async function handleDeleteCurrentConversation() {
  if (!currentConversationId) return;
  if (!confirm("현재 대화 기록을 삭제하시겠습니까?")) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations/${currentConversationId}`, {
      method: "DELETE"
    });
    if (res.ok) {
      alert("대화가 삭제되었습니다.");
      startNewChat();
      await loadConversationList();
    } else {
      alert("삭제 실패");
    }
  } catch (err) {
    alert("오류: " + err.message);
  }
}

// ==============================================================================
// 6. 데이터 관리 (CRUD)
// ==============================================================================
async function loadDataList() {
  const tbody = document.getElementById("data-table-body");
  tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">불러오는 중...</td></tr>';

  try {
    const res = await fetch(`${API_BASE_URL}/api/data`);
    if (!res.ok) throw new Error("데이터 목록 조회 실패");

    const data = await res.json();
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">데이터가 없습니다.</td></tr>';
      return;
    }

    tbody.innerHTML = "";
    // 최신 날짜가 위로 오도록 역순 표시
    const sorted = [...data].reverse();

    sorted.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${item.date}</strong></td>
        <td>${item.value.toLocaleString()}원</td>
        <td>${escapeHtml(item.memo)}</td>
        <td style="text-align: center;">
          <div class="action-btns" style="justify-content: center;">
            <button class="btn-secondary" onclick="openEditModal('${item.id}', '${item.date}', ${item.value}, '${escapeAttr(item.memo)}')">수정</button>
            <button class="btn-danger-sm" onclick="handleDeleteData('${item.id}')">삭제</button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--danger);">목록 로드 실패: ${err.message}</td></tr>`;
  }
}

async function handleAddData(e) {
  e.preventDefault();
  const dateInput = document.getElementById("add-date");
  const valueInput = document.getElementById("add-value");
  const memoInput = document.getElementById("add-memo");

  const newRecord = {
    date: dateInput.value,
    value: parseFloat(valueInput.value),
    memo: memoInput.value
  };

  try {
    const res = await fetch(`${API_BASE_URL}/api/data`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newRecord)
    });

    if (!res.ok) throw new Error("데이터 추가 실패");

    valueInput.value = "";
    await loadDataList();
    await loadDataSummary();
  } catch (err) {
    alert("오류: " + err.message);
  }
}

// 수정 모달 열기
window.openEditModal = function(id, date, value, memo) {
  document.getElementById("edit-id").value = id;
  document.getElementById("edit-date").value = date;
  document.getElementById("edit-value").value = value;
  document.getElementById("edit-memo").value = memo;
  document.getElementById("edit-modal").style.display = "flex";
};

function closeEditModal() {
  document.getElementById("edit-modal").style.display = "none";
}

async function handleEditDataSubmit(e) {
  e.preventDefault();
  const id = document.getElementById("edit-id").value;
  const updatePayload = {
    date: document.getElementById("edit-date").value,
    value: parseFloat(document.getElementById("edit-value").value),
    memo: document.getElementById("edit-memo").value
  };

  try {
    const res = await fetch(`${API_BASE_URL}/api/data/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatePayload)
    });

    if (!res.ok) throw new Error("데이터 수정 실패");

    closeEditModal();
    await loadDataList();
    await loadDataSummary();
  } catch (err) {
    alert("수정 오류: " + err.message);
  }
}

window.handleDeleteData = async function(id) {
  if (!confirm("해당 데이터를 삭제하시겠습니까?")) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/data/${id}`, {
      method: "DELETE"
    });

    if (!res.ok) throw new Error("삭제 실패");

    await loadDataList();
    await loadDataSummary();
  } catch (err) {
    alert("삭제 오류: " + err.message);
  }
};

// 유틸리티
function escapeHtml(str) {
  return (str || "").replace(/[&<>'"]/g, tag => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;"
  }[tag] || tag));
}

function escapeAttr(str) {
  return (str || "").replace(/"/g, "&quot;").replace(/'/g, "\\'");
}
