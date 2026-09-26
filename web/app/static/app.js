// 시각은 서버가 UTC ISO 로만 내보낸다. 표기는 여기서 브라우저 로컬로 그린다.
const rtf = new Intl.RelativeTimeFormat('ko', { numeric: 'auto' });
const UNITS = [['year',31536000],['month',2592000],['day',86400],
               ['hour',3600],['minute',60],['second',1]];

function relative(iso) {
  const diff = (new Date(iso) - Date.now()) / 1000;
  for (const [unit, secs] of UNITS) {
    if (Math.abs(diff) >= secs || unit === 'second') {
      return rtf.format(Math.round(diff / secs), unit);
    }
  }
}
function localTime(iso) {
  return new Date(iso).toLocaleString('ko-KR',
    { dateStyle: 'medium', timeStyle: 'short' });
}

async function main() {
  const me = await (await fetch('api/me')).json();
  document.getElementById('me').textContent = me.email || '(로컬)';

  const projects = await (await fetch('api/projects')).json();
  const list = document.getElementById('list');
  list.className = '';
  list.innerHTML = projects.map(p => `
    <a class="card" href="p/${p.slug}">
      <span class="when muted" title="${p.updated ? localTime(p.updated) : ''}">
        ${p.updated ? relative(p.updated) : ''}</span>
      <div class="name">${p.category ? `<span class="cat">${p.category}</span>` : ''
        }${p.name}</div>
      ${p.title ? `<div class="title">${p.title}</div>` : ''}
    </a>`).join('');
}
main();
