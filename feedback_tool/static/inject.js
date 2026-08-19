/* feedback_tool — ocp_vscode 뷰어에 캡처 버튼 주입.
 *
 * 동작:
 *   1. 우하단 "✏️ 피드백" 버튼 → window.__ocpViewer.getImage() 로 현재 모델 캡처
 *   2. POST /feedback/capture 로 임시 저장 → id 수신
 *   3. /draw?bg=<id> 새 탭 → Excalidraw 로 덧그림 + 업로드
 * (덧그림 편집기는 draw.html 의 Excalidraw 가 담당. 예전 내장 canvas 오버레이는
 *  git 히스토리 참조)
 */
(function () {
  "use strict";

  const API = "/feedback";

  const style = document.createElement("style");
  style.textContent = `
    #fb-launcher{position:fixed;right:16px;bottom:16px;z-index:99999;
      padding:12px 16px;border:none;border-radius:24px;cursor:pointer;
      background:#ff3b30;color:#fff;font-size:15px;font-weight:600;
      box-shadow:0 3px 10px rgba(0,0,0,.35);touch-action:manipulation}
    #fb-launcher:disabled{opacity:.5}
    #fb-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:100001;
      background:#222;color:#fff;padding:10px 16px;border-radius:8px;font-size:14px;
      box-shadow:0 3px 10px rgba(0,0,0,.4);opacity:0;transition:opacity .2s}
    #fb-toast.show{opacity:1}
  `;
  document.head.appendChild(style);

  const launcher = document.createElement("button");
  launcher.id = "fb-launcher";
  launcher.textContent = "✏️ 피드백";
  launcher.addEventListener("click", startCapture);
  if (document.body) document.body.appendChild(launcher);
  else window.addEventListener("DOMContentLoaded", () => document.body.appendChild(launcher));

  async function startCapture() {
    const viewer = window.__ocpViewer;
    if (!viewer || !viewer.getImage) { toast("뷰어가 아직 준비되지 않았습니다"); return; }
    launcher.disabled = true;
    try {
      const res = await viewer.getImage("feedback");
      const dataUrl = res && res.dataUrl;
      if (!dataUrl) throw new Error("no image");
      const up = await fetch(`${API}/capture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataUrl }),
      });
      if (!up.ok) throw new Error("HTTP " + up.status);
      const { id } = await up.json();
      window.open(`/draw?bg=${encodeURIComponent(id)}`, "_blank");
    } catch (e) {
      console.error("[feedback] capture failed", e);
      toast("캡처 실패: " + e.message);
    } finally {
      launcher.disabled = false;
    }
  }

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
