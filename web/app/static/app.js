// 시각은 서버가 UTC ISO 로만 내보낸다. 표기는 여기서 브라우저 로컬로 그린다.
const rtf = new Intl.RelativeTimeFormat('ko', { numeric: 'auto' });
const UNITS = [['year',31536000],['month',2592000],['day',86400],
               ['hour',3600],['minute',60],['second',1]];
const relative = iso => {
  const d = (new Date(iso) - Date.now()) / 1000;
  for (const [u, s] of UNITS)
    if (Math.abs(d) >= s || u === 'second') return rtf.format(Math.round(d / s), u);
};
const localTime = iso => new Date(iso).toLocaleString('ko-KR',
  { dateStyle: 'medium', timeStyle: 'short' });

const ROOT = '·';              // 카테고리 없는 프로젝트를 담는 가상 그룹
const OPEN_KEY = 'openCats';
const isOpen = c => (JSON.parse(localStorage.getItem(OPEN_KEY) || '[]')).includes(c);
function toggleOpen(c) {
  const s = new Set(JSON.parse(localStorage.getItem(OPEN_KEY) || '[]'));
  s.has(c) ? s.delete(c) : s.add(c);
  localStorage.setItem(OPEN_KEY, JSON.stringify([...s]));
}

function render(projects) {
  // 카테고리별로 묶고, **각 카테고리의 가장 최근 작업**을 기준으로 정렬한다
  const groups = new Map();
  for (const p of projects) {
    const c = p.category || ROOT;
    if (!groups.has(c)) groups.set(c, []);
    groups.get(c).push(p);
  }
  const ordered = [...groups.entries()].sort(
    (a, b) => (b[1][0].updated || '').localeCompare(a[1][0].updated || ''));

  document.getElementById('list').className = '';
  document.getElementById('list').innerHTML = ordered.map(([cat, items]) => {
    const open = isOpen(cat);
    const newest = items[0].updated;
    return `<div class="grp${open ? ' open' : ''}" data-cat="${cat}">
      <button class="ghead">
        <span class="arrow">▶</span>
        <b>${cat === ROOT ? '분류 없음' : cat}</b>
        <span class="cnt">${items.length}</span>
        <span class="when muted" title="${newest ? localTime(newest) : ''}"
          >${newest ? relative(newest) : ''}</span>
      </button>
      <div class="gbody">${items.map(p => `
        <a class="card" href="p/${p.slug}">
          <span class="when muted" title="${p.updated ? localTime(p.updated) : ''}"
            >${p.updated ? relative(p.updated) : ''}</span>
          <div class="name">${p.name}</div>
          ${p.title ? `<div class="title">${p.title}</div>` : ''}
        </a>`).join('')}</div>
    </div>`;
  }).join('');

  document.querySelectorAll('.ghead').forEach(h => h.onclick = () => {
    const grp = h.closest('.grp');
    grp.classList.toggle('open');
    toggleOpen(grp.dataset.cat);
  });
}

// ---- 새 프로젝트 ----
const form = document.getElementById('form');
const catSel = document.getElementById('cat');
const newCat = document.getElementById('newcat');
const err = document.getElementById('err');

document.getElementById('new').onclick = () => {
  form.hidden = !form.hidden;
  if (!form.hidden) document.getElementById('name').focus();
};
catSel.onchange = () => {
  newCat.hidden = catSel.value !== '__new__';
  if (!newCat.hidden) newCat.focus();
};
form.onsubmit = async e => {
  e.preventDefault();
  err.textContent = '';
  const category = catSel.value === '__new__' ? newCat.value.trim()
                 : (catSel.value || null);
  const res = await fetch('api/projects', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: document.getElementById('name').value.trim(),
                           category }),
  });
  if (!res.ok) { err.textContent = (await res.json()).detail; return; }
  location.href = `p/${(await res.json()).slug}`;
};

async function main() {
  const [me, projects, cats] = await Promise.all([
    fetch('api/me').then(r => r.json()),
    fetch('api/projects').then(r => r.json()),
    fetch('api/categories').then(r => r.json()),
  ]);
  document.getElementById('me').textContent = me.email || '(로컬)';
  catSel.innerHTML = '<option value="">분류 없음</option>'
    + cats.map(c => `<option>${c}</option>`).join('')
    + '<option value="__new__">+ 새 카테고리…</option>';
  render(projects);
}
main();
