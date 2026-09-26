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
const renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true });
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

let current = null;
const material = new THREE.MeshLambertMaterial({ color: 0xb8c2cc });

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

async function show(part) {
  hint.textContent = '불러오는 중…';
  const res = await fetch(`mesh/${slug}/${part}`);
  if (!res.ok) { hint.textContent = '아직 export 되지 않았습니다'; return; }
  const geo = new STLLoader().parse(await res.arrayBuffer());
  geo.computeVertexNormals();
  if (current) { scene.remove(current); current.geometry.dispose(); }
  current = new THREE.Mesh(geo, material);
  scene.add(current);
  frame(current);
  hint.textContent = '';
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

document.getElementById('parts').innerHTML = data.parts.map(p => {
  const ready = haveStep.has(p.name);
  return `<button class="item" data-part="${p.name}" ${ready ? '' : 'disabled'}>
    ${p.name}<span class="tag">${ready ? p.source : '빌드 필요'}</span></button>`;
}).join('');

document.getElementById('files').innerHTML = data.artifacts.map(a => `
  <a class="dl" href="dl/${slug}/${a.name}" download>
    ${a.name}<span class="when" title="${new Date(a.mtime).toLocaleString('ko-KR')}">
      ${kb(a.size)} · ${relative(a.mtime)}</span></a>`).join('')
  || '<div class="sec">없음</div>';

document.getElementById('parts').addEventListener('click', e => {
  const btn = e.target.closest('.item');
  if (!btn || btn.disabled) return;
  document.querySelectorAll('.item').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  show(btn.dataset.part);
});

resize();
// 첫 파트를 자동으로 띄운다
document.querySelector('.item:not([disabled])')?.click();
