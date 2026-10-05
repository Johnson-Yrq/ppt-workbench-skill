const slides = [...document.querySelectorAll('main > .slide')];
let index = 0, editing = false;
const jump = document.getElementById('jump');
const dialog = document.getElementById('overview-dialog');
function fit() {
  const scale = Math.max(.1, Math.min((innerWidth - 40) / 1600, (innerHeight - 88) / 900));
  document.querySelector('main').style.transform = `scale(${scale})`;
  const frame = document.querySelector('.frame');
  frame.style.width = 1600 * scale + 'px'; frame.style.height = 900 * scale + 'px';
  dialog.querySelectorAll('.thumb').forEach(t => t.firstElementChild.style.transform = `scale(${t.clientWidth / 1600})`);
}
function show(n) {
  index = (n + slides.length) % slides.length;
  slides.forEach((s, i) => s.classList.toggle('active', i === index));
  document.getElementById('count').textContent = `${index + 1} / ${slides.length}`;
  jump.value = String(index);
  history.replaceState(null, '', '#' + (index + 1));
}
jump.replaceChildren(...slides.map((s, i) => { const o = document.createElement('option'); o.value = i; o.textContent = `${String(i + 1).padStart(2, '0')} · ${s.getAttribute('aria-label')}`; return o; }));
jump.onchange = () => show(Number(jump.value));
document.getElementById('prev').onclick = () => show(index - 1);
document.getElementById('next').onclick = () => show(index + 1);
document.getElementById('edit').onclick = () => {
  editing = !editing;
  document.querySelectorAll('main [data-edit]').forEach(e => e.contentEditable = editing);
  document.getElementById('edit').textContent = editing ? '完成编辑' : '编辑文字';
};
document.getElementById('overview').onclick = () => {
  const grid = dialog.querySelector('.overview-grid'); grid.replaceChildren();
  slides.forEach((s, i) => {
    const card = document.createElement('button'); card.className = 'overview-card';
    const thumb = document.createElement('div'); thumb.className = 'thumb';
    const clone = s.cloneNode(true); clone.querySelectorAll('[contenteditable]').forEach(e => e.removeAttribute('contenteditable'));
    clone.style.width = '1600px'; clone.style.height = '900px'; clone.removeAttribute('aria-label'); clone.setAttribute('aria-hidden', 'true');
    clone.querySelectorAll('a').forEach(a => a.tabIndex = -1); thumb.append(clone);
    const label = document.createElement('span'); label.className = 'overview-label'; label.textContent = `${String(i + 1).padStart(2, '0')} / ${s.getAttribute('aria-label')}`;
    card.append(thumb, label); card.onclick = () => { dialog.close(); show(i); }; grid.append(card);
  });
  dialog.showModal(); fit();
};
document.getElementById('close-overview').onclick = () => dialog.close();
document.getElementById('save').onclick = () => {
  const copy = document.documentElement.cloneNode(true);
  copy.querySelectorAll('[contenteditable]').forEach(e => e.removeAttribute('contenteditable'));
  copy.querySelector('#edit').textContent = '编辑文字';
  copy.querySelector('#overview-dialog').removeAttribute('open');
  copy.querySelector('.overview-grid').replaceChildren();
  const blob = new Blob(['<!doctype html>\n' + copy.outerHTML], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob), a = document.createElement('a');
  a.href = url; a.download = '墨蓝雾灰-AI协作工作台.html'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
};
document.getElementById('fullscreen').onclick = () => document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
document.querySelectorAll('.contents a').forEach(a => a.onclick = e => { e.preventDefault(); show(Number(a.hash.slice(1)) - 1); });
document.addEventListener('keydown', e => {
  if (editing || dialog.open || e.target.closest('select,input,textarea,[contenteditable=true]')) return;
  if (['ArrowRight', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); show(index + 1); }
  if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); show(index - 1); }
  if (e.key === 'Home') show(0); if (e.key === 'End') show(slides.length - 1);
});
addEventListener('resize', fit);
const savedActive = slides.findIndex(s => s.classList.contains('active'));
show(Math.max(0, Math.min(slides.length - 1, location.hash ? (parseInt(location.hash.slice(1)) || 1) - 1 : Math.max(0, savedActive))));
fit();
