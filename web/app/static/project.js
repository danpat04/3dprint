// 프로젝트 페이지 — 좌: 파트 목록, 우: three.js STL 뷰어
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

const slug = document.body.dataset.slug;
const rtf = new Intl.RelativeTimeFormat('ko', { numeric: 'auto' });
const UNITS = [['year',31536000],['month',2592000],['day',86400],
               ['hour',3600],['minute',60],['second',1]];
const relative = iso => {
  const d = (new Date(iso) - Date.now()) / 1000;
  for (const [u, s] of UNITS)
    if (Math.abs(d) >= s || u === 'second') return rtf.format(Math.round(d / s), u);
};
const kb = n => (n / 1024).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + ' KB';

// ---- 뷰어 ----
const cv = document.getElementById('cv');
const hint = document.getElementById('hint');
// preserveDrawingBuffer 가 없으면 toDataURL 이 빈 이미지를 준다 (프레임 후 버퍼가 비워짐)
const renderer = new THREE.WebGLRenderer({
  canvas: cv, antialias: true, preserveDrawingBuffer: true });
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x16161a);
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 20000);
// build123d 는 Z 가 위다. three.js 기본(Y 위)을 그대로 두면 모델이 누워 보인다.
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, cv);
controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x444450, 2.2));
const key = new THREE.DirectionalLight(0xffffff, 1.6);
key.position.set(1, 1.4, 1);
scene.add(key);

let current = null;                       // 현재 파트의 솔리드 메시들
// 조립품에서 조각을 구분하려고 색을 돌려 쓴다. 단품(1조각)은 첫 색만 쓴다.
const PALETTE = [0xb8c2cc, 0x7fb3e8, 0xe8b87f, 0x9fd8a0, 0xd8a0d0,
                 0xe8e07f, 0x9fd8d8, 0xd89f9f, 0xa8a8e8, 0xc8d89f,
                 0xe8c8a0, 0x9fc0d8];

// 프린터 베드 — 크기 감각의 기준점. 파트를 여기 올려놓고 본다.
const BED = 256;
const bed = new THREE.GridHelper(BED, 16, 0x3a3a44, 0x26262e);
bed.rotation.x = Math.PI / 2;          // GridHelper 는 XZ 평면이라 XY 로 눕힌다
scene.add(bed);

function resize() {
  const { clientWidth: w, clientHeight: h } = cv.parentElement;
  renderer.setSize(w, h, false);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  camera.aspect = w / h; camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(cv.parentElement);

// 정면 위에서 내려다보는 각도 — 프린터 앞에 서서 베드를 보는 자세
const ELEV = 35 * Math.PI / 180;

function fitDistance(radius) {
  // 반지름 radius 인 구가 화면에 들어오는 거리. 세로/가로 중 좁은 쪽이 기준.
  const fovV = camera.fov * Math.PI / 180;
  const fovH = 2 * Math.atan(Math.tan(fovV / 2) * camera.aspect);
  return radius / Math.sin(Math.min(fovV, fovH) / 2);
}

function frame(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());

  // 베드 위에 올려놓는다 — XY 중앙, 바닥을 z=0 에
  obj.position.set(-center.x, -center.y, -box.min.z);

  // 거리는 **베드를 기준**으로 잡는다. 파트마다 배율이 같아 실제 크기가 감이 온다.
  // 베드보다 큰 물체만 더 물러선다.
  const bedR = (BED / 2) * Math.SQRT2;
  const objR = size.length() / 2;
  const dist = fitDistance(Math.max(bedR, objR));

  camera.position.set(0, -dist * Math.cos(ELEV), dist * Math.sin(ELEV));
  camera.near = dist / 500; camera.far = dist * 20;
  camera.updateProjectionMatrix();
  controls.target.set(0, 0, size.z / 2);
  controls.update();
}

function clearMeshes() {
  for (const m of current || []) {
    scene.remove(m); m.geometry.dispose(); m.material.dispose();
  }
  current = null;
}

async function show(part) {
  hint.textContent = '불러오는 중…';
  const info = await fetch(`meshinfo/${slug}/${part}`);
  if (!info.ok) { hint.textContent = '아직 export 되지 않았습니다'; return; }
  const { solids } = await info.json();
  const loader = new STLLoader();
  const group = new THREE.Group();
  const meshes = [];
  for (const s of solids) {
    const res = await fetch(`mesh/${slug}/${part}/${s.index}`);
    if (!res.ok) continue;
    const geo = loader.parse(await res.arrayBuffer());
    geo.computeVertexNormals();
    const mesh = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({
      color: PALETTE[meshes.length % PALETTE.length] }));
    group.add(mesh); meshes.push(mesh);
  }
  clearMeshes();
  current = meshes;
  scene.add(group);
  frame(group);
  renderSolids(solids, meshes);
  hint.textContent = '';
}

// 조립품일 때만 조각 목록을 보여준다 — 단품은 켤 것도 끌 것도 없다
function renderSolids(solids, meshes) {
  const box = document.getElementById('solids');
  if (solids.length < 2) { box.innerHTML = ''; return; }
  box.innerHTML = '<div class="sec">조각</div>' + solids.map((s, i) => `
    <label class="sol"><input type="checkbox" data-i="${i}" checked>
      <span class="sw" style="background:#${PALETTE[i % PALETTE.length]
        .toString(16).padStart(6, '0')}"></span>
      ${s.volume} cm³ <span class="tag">${s.size.join('×')}</span></label>`).join('');
  box.onchange = e => {
    const i = +e.target.dataset.i;
    if (meshes[i]) meshes[i].visible = e.target.checked;
  };
}

(function loop() {
  requestAnimationFrame(loop);
  controls.update();
  renderer.render(scene, camera);
})();

// ---- 목록 ----
const data = await (await fetch(`api/projects/${slug}`)).json();
document.getElementById('ptitle').textContent = data.title || data.name;
document.getElementById('me').textContent =
  (await (await fetch('api/me')).json()).email || '(로컬)';

const haveStep = new Set(
  data.artifacts.filter(a => a.name.endsWith('.step')).map(a => a.name.slice(0, -5)));

let selected = null;
let building = null;

function renderParts(parts, have) {
  document.getElementById('parts').innerHTML = parts.map(p => {
    const ready = have.has(p.name);
    const busy = building === p.name;
    const tag = busy ? '빌드 중…' : (ready ? p.source : '미출력');
    return `<div class="row${ready ? '' : ' dim'}${busy ? ' busy' : ''}">
      <button class="item${selected === p.name ? ' on' : ''}"
        data-part="${p.name}" ${ready ? '' : 'disabled'}
        >${p.name}<span class="tag">${tag}</span></button>
      ${p.buildable ? `<button class="bld" data-build="${p.name}"
        ${building ? 'disabled' : ''} title="다시 빌드">⟳</button>` : ''}
    </div>`;
  }).join('');
}
renderParts(data.parts, haveStep);

function renderFiles(artifacts) {
  document.getElementById('files').innerHTML = artifacts.map(a => `
    <a class="dl" href="dl/${slug}/${a.name}" download>
      ${a.name}<span class="when" title="${new Date(a.mtime).toLocaleString('ko-KR')}">
        ${kb(a.size)} · ${relative(a.mtime)}</span></a>`).join('')
    || '<div class="sec">없음</div>';
}
renderFiles(data.artifacts);

// ---- 빌드 ----
const logBox = document.getElementById('log');

async function refresh() {
  const fresh = await (await fetch(`api/projects/${slug}`)).json();
  const have = new Set(fresh.artifacts
    .filter(a => a.name.endsWith('.step')).map(a => a.name.slice(0, -5)));
  renderParts(fresh.parts, have);
  renderFiles(fresh.artifacts);
  return have;
}

async function runBuild(part) {
  if (building) return;                 // 동시에 하나만
  building = part;
  await refresh();                      // "빌드 중…" 표시
  logBox.hidden = false;
  logBox.textContent = `${part} 빌드 요청…`;
  try {
    const res = await fetch(`build/${slug}/${part}`, { method: 'POST' });
    if (!res.ok) {
      logBox.textContent = `빌드 불가: ${(await res.json()).detail}`;
      return;
    }
    const { id } = await res.json();
    let job;
    do {
      await new Promise(r => setTimeout(r, 1000));
      job = await (await fetch(`jobs/${id}`)).json();
      logBox.textContent =
        `[${job.status}] ${part}\n` + job.log.slice(-14).join('\n');
      logBox.scrollTop = logBox.scrollHeight;
    } while (job.status === 'queued' || job.status === 'running');
    if (job.status === 'done') selected = part;
  } finally {
    // 성공이든 실패든 같은 경로로 되돌린다 — 상태를 손으로 복원하지 않는다
    building = null;
    const have = await refresh();
    if (selected && have.has(selected)) show(selected);
  }
}

document.getElementById('parts').addEventListener('click', e => {
  const bld = e.target.closest('.bld');
  if (bld) { runBuild(bld.dataset.build); return; }
  const btn = e.target.closest('.item');
  if (!btn || btn.disabled) return;
  selected = btn.dataset.part;
  document.querySelectorAll('.item').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  show(selected);
});

// ---- 자동 갱신 ----
// 내가 터미널에서 빌드해도 화면이 알아서 바뀐다.
let rev = null;
setInterval(async () => {
  if (building) return;                   // 빌드 중엔 그쪽이 갱신을 맡는다
  try {
    const r = (await (await fetch(`rev/${slug}`)).json()).rev;
    if (rev === null) { rev = r; return; }
    if (r !== rev) {
      rev = r;
      const have = await refresh();
      if (selected && have.has(selected)) show(selected);
    }
  } catch { /* 네트워크 끊김은 무시 */ }
}, 4000);

// ---- 피드백 · 드래프트 ----
// 프로젝트/파트가 URL 에 이미 있으므로 그리기 페이지에서 고를 일이 없다.
document.getElementById('fb').onclick = async () => {
  if (!current || !current.length) { alert('먼저 파트를 선택하세요'); return; }
  renderer.render(scene, camera);                 // 캔버스를 확실히 채우고 캡처
  const image = cv.toDataURL('image/png');
  const res = await fetch('capture', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image }),
  });
  const { id } = await res.json();
  location.href = `draw?p=${slug}&part=${selected || ''}&bg=${id}`;
};
document.getElementById('df').onclick = () => {
  location.href = `draw?p=${slug}`;
};

resize();
// 첫 파트를 자동으로 띄운다
document.querySelector('.row:not(.dim) .item')?.click();
