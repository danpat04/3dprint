/* feedback_tool — ocp_vscode 뷰어 위에 캡처 + 덧그림 + 업로드 오버레이를 주입.
 *
 * 동작:
 *   1. 우하단 "✏️ 피드백" 버튼 → window.__ocpViewer.getImage() 로 현재 모델 캡처
 *   2. 캡처 PNG 를 배경에 깔고 그 위 투명 canvas 에 Pointer Events 로 덧그림
 *      (마우스/터치/펜 통합, 펜은 pressure 로 굵기 가변)
 *   3. 프로젝트 선택 + 메모 입력 후 업로드 → POST /feedback/upload
 */
(function () {
  "use strict";

  const API = "/feedback";
  const PALETTE = ["#ff3b30", "#007aff", "#34c759", "#ffcc00", "#000000", "#ffffff"];
  const LS_PROJECT = "fb_last_project";

  let overlay, stage, bgCanvas, drawCanvas, dctx;
  let projectSel, projectBox, noteInput, widthInput, eraserBtn;
  let drawing = false, last = null, eraser = false;
  let color = PALETTE[0], baseWidth = 4;
  const undoStack = [];
  const UNDO_LIMIT = 25;

  // ---------- styles ----------
  const style = document.createElement("style");
  style.textContent = `
    #fb-launcher{position:fixed;right:16px;bottom:16px;z-index:99999;
      padding:12px 16px;border:none;border-radius:24px;cursor:pointer;
      background:#ff3b30;color:#fff;font-size:15px;font-weight:600;
      box-shadow:0 3px 10px rgba(0,0,0,.35);touch-action:manipulation}
    #fb-launcher:disabled{opacity:.5}
    #fb-overlay{position:fixed;inset:0;z-index:100000;display:flex;flex-direction:column;
      background:rgba(20,20,22,.94);touch-action:none;user-select:none;-webkit-user-select:none}
    #fb-top,#fb-bottom{display:flex;gap:8px;align-items:center;flex-wrap:wrap;
      padding:8px 10px;background:#26262b;color:#eee;font-size:14px}
    #fb-stage{flex:1;position:relative;overflow:hidden}
    #fb-stage canvas{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
      max-width:100%;max-height:100%;box-shadow:0 0 0 1px #444}
    #fb-bg{z-index:1;background:#fff}
    #fb-draw{z-index:2;touch-action:none;cursor:crosshair}
    .fb-swatch{width:26px;height:26px;border-radius:50%;border:2px solid #555;cursor:pointer;padding:0}
    .fb-swatch.active{border-color:#fff;box-shadow:0 0 0 2px #ff3b30}
    .fb-btn{padding:8px 12px;border:none;border-radius:8px;background:#3a3a42;color:#fff;
      font-size:14px;cursor:pointer;touch-action:manipulation}
    .fb-btn.active{background:#ff3b30}
    .fb-btn.primary{background:#34c759;font-weight:600}
    .fb-btn:disabled{opacity:.5}
    #fb-bottom select,#fb-bottom input[type=text]{padding:8px;border-radius:8px;border:1px solid #555;
      background:#1c1c20;color:#fff;font-size:14px}
    #fb-proj{display:flex;align-items:center;gap:8px;background:#1c1c20;border:1px solid #555;
      border-radius:8px;padding:6px 10px;font-size:14px;font-weight:600;color:#fff}
    #fb-proj .name{color:#34c759}
    #fb-proj .change{font-size:12px;font-weight:400;color:#9ab;text-decoration:underline;cursor:pointer}
    #fb-note{flex:1;min-width:120px}
    #fb-width{width:90px}
    #fb-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:100001;
      background:#222;color:#fff;padding:10px 16px;border-radius:8px;font-size:14px;
      box-shadow:0 3px 10px rgba(0,0,0,.4);opacity:0;transition:opacity .2s}
    #fb-toast.show{opacity:1}
  `;
  document.head.appendChild(style);

  // ---------- launcher ----------
  const launcher = document.createElement("button");
  launcher.id = "fb-launcher";
  launcher.textContent = "✏️ 피드백";
  launcher.addEventListener("click", startCapture);
  appendWhenReady(launcher);

  function appendWhenReady(el) {
    if (document.body) document.body.appendChild(el);
    else window.addEventListener("DOMContentLoaded", () => document.body.appendChild(el));
  }

  // ---------- capture ----------
  async function startCapture() {
    const viewer = window.__ocpViewer;
    if (!viewer || !viewer.getImage) { toast("뷰어가 아직 준비되지 않았습니다"); return; }
    launcher.disabled = true;
    let dataUrl = null;
    try {
      const res = await viewer.getImage("feedback");
      dataUrl = res && res.dataUrl;
    } catch (e) { console.error("[feedback] capture failed", e); }
    launcher.disabled = false;
    if (!dataUrl) { toast("캡처에 실패했습니다"); return; }
    const img = new Image();
    img.onload = () => buildOverlay(img);
    img.onerror = () => toast("캡처 이미지를 불러오지 못했습니다");
    img.src = dataUrl;
  }

  // ---------- editor overlay ----------
  function buildOverlay(img) {
    overlay = document.createElement("div");
    overlay.id = "fb-overlay";

    // top bar: colors + width + eraser + undo
    const top = document.createElement("div");
    top.id = "fb-top";
    PALETTE.forEach((c) => {
      const sw = document.createElement("button");
      sw.className = "fb-swatch" + (c === color ? " active" : "");
      sw.style.background = c;
      sw.title = c;
      sw.addEventListener("click", () => {
        color = c; eraser = false;
        eraserBtn.classList.remove("active");
        top.querySelectorAll(".fb-swatch").forEach((s) => s.classList.remove("active"));
        sw.classList.add("active");
      });
      top.appendChild(sw);
    });

    widthInput = document.createElement("input");
    widthInput.type = "range"; widthInput.id = "fb-width";
    widthInput.min = "1"; widthInput.max = "20"; widthInput.value = String(baseWidth);
    widthInput.addEventListener("input", () => { baseWidth = +widthInput.value; });
    top.appendChild(labelWrap("굵기", widthInput));

    eraserBtn = mkBtn("지우개", () => {
      eraser = !eraser;
      eraserBtn.classList.toggle("active", eraser);
    });
    top.appendChild(eraserBtn);
    top.appendChild(mkBtn("↩ 되돌리기", undo));

    // stage
    stage = document.createElement("div");
    stage.id = "fb-stage";
    bgCanvas = document.createElement("canvas");
    bgCanvas.id = "fb-bg";
    drawCanvas = document.createElement("canvas");
    drawCanvas.id = "fb-draw";
    bgCanvas.width = drawCanvas.width = img.naturalWidth;
    bgCanvas.height = drawCanvas.height = img.naturalHeight;
    bgCanvas.getContext("2d").drawImage(img, 0, 0);
    dctx = drawCanvas.getContext("2d");
    dctx.lineCap = "round"; dctx.lineJoin = "round";
    stage.appendChild(bgCanvas);
    stage.appendChild(drawCanvas);

    // bottom bar: project + note + cancel + upload
    const bottom = document.createElement("div");
    bottom.id = "fb-bottom";
    // 고정 라벨(현재 프로젝트) + 숨겨진 드롭다운(변경용)
    projectBox = document.createElement("div");
    projectBox.id = "fb-proj";
    projectBox.style.display = "none";
    bottom.appendChild(projectBox);
    projectSel = document.createElement("select");
    projectSel.innerHTML = `<option value="">프로젝트…</option>`;
    bottom.appendChild(projectSel);
    noteInput = document.createElement("input");
    noteInput.type = "text"; noteInput.id = "fb-note";
    noteInput.placeholder = "메모 (예: 여기 모서리를 2mm 둥글게)";
    bottom.appendChild(noteInput);
    bottom.appendChild(mkBtn("취소", closeOverlay));
    const upBtn = mkBtn("⬆ 업로드", () => upload(upBtn));
    upBtn.classList.add("primary");
    bottom.appendChild(upBtn);

    overlay.appendChild(top);
    overlay.appendChild(stage);
    overlay.appendChild(bottom);
    document.body.appendChild(overlay);

    attachDrawing();
    pushUndo();
    loadProjects();
  }

  function labelWrap(text, el) {
    const w = document.createElement("label");
    w.style.cssText = "display:flex;align-items:center;gap:4px;color:#ccc";
    w.append(text, el);
    return w;
  }
  function mkBtn(text, fn) {
    const b = document.createElement("button");
    b.className = "fb-btn"; b.textContent = text;
    b.addEventListener("click", fn);
    return b;
  }

  // ---------- drawing (Pointer Events) ----------
  function attachDrawing() {
    drawCanvas.addEventListener("pointerdown", (e) => {
      drawCanvas.setPointerCapture(e.pointerId);
      pushUndo();
      drawing = true;
      last = pointInfo(e);
      drawSeg(last, last); // 점 찍기
      e.preventDefault();
    });
    drawCanvas.addEventListener("pointermove", (e) => {
      if (!drawing) return;
      const cur = pointInfo(e);
      drawSeg(last, cur);
      last = cur;
      e.preventDefault();
    });
    const end = (e) => { drawing = false; last = null; if (e) e.preventDefault(); };
    drawCanvas.addEventListener("pointerup", end);
    drawCanvas.addEventListener("pointercancel", end);
    drawCanvas.addEventListener("pointerleave", end);
  }

  function pointInfo(e) {
    const r = drawCanvas.getBoundingClientRect();
    const pen = e.pointerType === "pen";
    const pressure = e.pressure > 0 ? e.pressure : 0.5;
    return {
      x: (e.clientX - r.left) * (drawCanvas.width / r.width),
      y: (e.clientY - r.top) * (drawCanvas.height / r.height),
      // 펜이면 필압으로 굵기 가변, 그 외엔 고정
      w: pen ? baseWidth * (0.35 + 1.3 * pressure) : baseWidth,
    };
  }

  function drawSeg(a, b) {
    dctx.globalCompositeOperation = eraser ? "destination-out" : "source-over";
    dctx.strokeStyle = color;
    dctx.lineWidth = b.w;
    dctx.beginPath();
    dctx.moveTo(a.x, a.y);
    dctx.lineTo(b.x, b.y);
    dctx.stroke();
  }

  // ---------- undo ----------
  function pushUndo() {
    try {
      undoStack.push(dctx.getImageData(0, 0, drawCanvas.width, drawCanvas.height));
      if (undoStack.length > UNDO_LIMIT) undoStack.shift();
    } catch (e) { /* ignore */ }
  }
  function undo() {
    if (undoStack.length <= 1) {
      dctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
      undoStack.length = 0;
      return;
    }
    undoStack.pop();
    dctx.putImageData(undoStack[undoStack.length - 1], 0, 0);
  }

  // ---------- projects ----------
  async function loadProjects() {
    let projects = [], current = null;
    try {
      const [pr, cr] = await Promise.all([
        fetch(`${API}/projects`).then((r) => r.json()),
        fetch(`${API}/current`).then((r) => r.json()).catch(() => ({ project: null })),
      ]);
      projects = pr.projects || [];
      current = cr.project;
    } catch (e) { console.error("[feedback] projects failed", e); }

    projects.forEach((p) => {
      const o = document.createElement("option");
      o.value = p; o.textContent = p;
      projectSel.appendChild(o);
    });

    // 뷰어에 마지막으로 push 된 프로젝트가 있으면 그걸로 고정, 없으면 직전 선택값
    const auto = (current && projects.includes(current)) ? current
               : (localStorage.getItem(LS_PROJECT) || "");
    if (auto) projectSel.value = auto;

    if (current && projects.includes(current)) {
      fixProject(current);   // 라벨로 고정 표시, 드롭다운 숨김
    } else {
      showPicker();          // 통지 없음 → 직접 선택
    }
  }

  function fixProject(name) {
    projectBox.innerHTML = "";
    const tag = document.createElement("span");
    tag.innerHTML = `📁 <span class="name">${name}</span>`;
    const change = document.createElement("span");
    change.className = "change"; change.textContent = "변경";
    change.addEventListener("click", showPicker);
    projectBox.append(tag, change);
    projectBox.style.display = "flex";
    projectSel.style.display = "none";
  }

  function showPicker() {
    projectBox.style.display = "none";
    projectSel.style.display = "";
  }

  // ---------- upload ----------
  async function upload(btn) {
    const project = projectSel.value;
    if (!project) { toast("프로젝트를 선택하세요"); return; }
    // 배경 + 덧그림 합성
    const out = document.createElement("canvas");
    out.width = bgCanvas.width; out.height = bgCanvas.height;
    const octx = out.getContext("2d");
    octx.drawImage(bgCanvas, 0, 0);
    octx.drawImage(drawCanvas, 0, 0);
    const image = out.toDataURL("image/png");

    btn.disabled = true; btn.textContent = "업로드 중…";
    try {
      const res = await fetch(`${API}/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project, note: noteInput.value || "", image }),
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      localStorage.setItem(LS_PROJECT, project);
      closeOverlay();
      toast("저장됨: " + (data.path || project));
    } catch (e) {
      console.error("[feedback] upload failed", e);
      btn.disabled = false; btn.textContent = "⬆ 업로드";
      toast("업로드 실패: " + e.message);
    }
  }

  function closeOverlay() {
    if (overlay) overlay.remove();
    overlay = null; undoStack.length = 0;
  }

  // ---------- toast ----------
  let toastEl, toastTimer;
  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.id = "fb-toast";
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2600);
  }
})();
