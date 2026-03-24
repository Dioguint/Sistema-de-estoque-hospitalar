// ── Autenticação ──────────────────────────────────────────────────────────────
const usuarioLogado = sessionStorage.getItem('usuario');
if (!usuarioLogado) {
  window.location.replace('login.html');
}

const usuario = JSON.parse(usuarioLogado);
document.getElementById('nomeUsuario').textContent = `Olá, ${usuario.name}`;

document.getElementById('btnLogout').addEventListener('click', () => {
  sessionStorage.removeItem('usuario');
  window.location.replace('login.html');
});

// ── Dados simulados ───────────────────────────────────────────────────────────
const DATA = {
  kpis: [
    { label: 'Total de Itens',     value: 142,   sub: 'produtos cadastrados',  cls: '' },
    { label: 'Itens Críticos',     value: 11,    sub: 'abaixo do mínimo',      cls: 'alert' },
    { label: 'Entradas (7 dias)',  value: 384,   sub: 'unidades recebidas',    cls: '' },
    { label: 'Saídas (7 dias)',    value: 291,   sub: 'unidades distribuídas', cls: '' },
    { label: 'Taxa de Abastecim.',value: '97%', sub: 'pedidos atendidos',     cls: 'ok' },
  ],

  movimentacoes: {
    labels:   ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
    entradas: [68, 45, 72, 51, 83, 38, 27],
    saidas:   [52, 39, 61, 44, 71, 14, 10],
  },

  categorias: {
    labels:  ['Medicamentos', 'Material cirúrgico', 'EPI', 'Higiene', 'Outros'],
    valores: [38, 25, 18, 12, 7],
  },

  criticos: [
    { produto: 'Luva cirúrgica M',       categoria: 'EPI',                atual: 2,  min: 20, status: 'crit' },
    { produto: 'Soro fisiológico 500ml', categoria: 'Medicamentos',       atual: 4,  min: 15, status: 'crit' },
    { produto: 'Esparadrapo 10m',        categoria: 'Material cirúrgico', atual: 3,  min: 10, status: 'crit' },
    { produto: 'Máscara N95',            categoria: 'EPI',                atual: 8,  min: 30, status: 'crit' },
    { produto: 'Gaze estéril',           categoria: 'Material cirúrgico', atual: 6,  min: 10, status: 'alert' },
    { produto: 'Álcool 70% 1L',          categoria: 'Higiene',            atual: 4,  min:  8, status: 'alert' },
    { produto: 'Dipirona 500mg',         categoria: 'Medicamentos',       atual: 9,  min: 12, status: 'alert' },
    { produto: 'Seringa 10ml',           categoria: 'Material cirúrgico', atual: 14, min: 20, status: 'alert' },
  ],
};

// ── Helpers ───────────────────────────────────────────────────────────────────
const BADGE = {
  crit:  { cls: 'badge-crit',  txt: 'CRÍTICO' },
  alert: { cls: 'badge-alert', txt: 'ATENÇÃO' },
};

// ── Timestamp ─────────────────────────────────────────────────────────────────
document.getElementById('updated').textContent =
  'Atualizado: ' + new Date().toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });

// ── KPIs ──────────────────────────────────────────────────────────────────────
const kpisEl = document.getElementById('kpis');
DATA.kpis.forEach(k => {
  const div = document.createElement('div');
  div.className = `kpi ${k.cls}`;
  div.innerHTML = `
    <span class="kpi-label">${k.label}</span>
    <span class="kpi-value">${k.value}</span>
    <span class="kpi-sub">${k.sub}</span>`;
  kpisEl.appendChild(div);
});

// ── Gráfico movimentações ─────────────────────────────────────────────────────
new Chart(document.getElementById('chartMovs'), {
  type: 'bar',
  data: {
    labels: DATA.movimentacoes.labels,
    datasets: [
      { label: 'Entradas', data: DATA.movimentacoes.entradas, backgroundColor: '#2e7d32', borderRadius: 5 },
      { label: 'Saídas',   data: DATA.movimentacoes.saidas,   backgroundColor: '#90caf9', borderRadius: 5 },
    ],
  },
  options: {
    responsive: true,
    plugins: { legend: { position: 'bottom' } },
    scales: {
      y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
      x: { grid: { display: false } },
    },
  },
});

// ── Gráfico categorias ────────────────────────────────────────────────────────
new Chart(document.getElementById('chartCats'), {
  type: 'doughnut',
  data: {
    labels: DATA.categorias.labels,
    datasets: [{
      data: DATA.categorias.valores,
      backgroundColor: ['#1a2c4e', '#2e7d32', '#f59e0b', '#60a5fa', '#94a3b8'],
      borderWidth: 2,
      borderColor: '#fff',
    }],
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'bottom', labels: { padding: 16, font: { size: 12 } } },
    },
  },
});

// ── Filtros ───────────────────────────────────────────────────────────────────
const inputBusca      = document.getElementById('inputBusca');
const selectCategoria = document.getElementById('selectCategoria');
const filterCount     = document.getElementById('filterCount');

// Popular select de categorias dinamicamente
const categorias = [...new Set(DATA.criticos.map(r => r.categoria))].sort();
categorias.forEach(cat => {
  const opt = document.createElement('option');
  opt.value = cat;
  opt.textContent = cat;
  selectCategoria.appendChild(opt);
});

function getFiltered() {
  const busca = inputBusca.value.trim().toLowerCase();
  const cat   = selectCategoria.value;
  return DATA.criticos.filter(r => {
    const matchBusca = r.produto.toLowerCase().includes(busca);
    const matchCat   = cat === '' || r.categoria === cat;
    return matchBusca && matchCat;
  });
}

function renderTabela() {
  const tbody    = document.getElementById('tabelaCriticos');
  const filtered = getFiltered();
  tbody.innerHTML = '';

  filterCount.textContent = `${filtered.length} item(s) encontrado(s)`;

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="5">Nenhum item encontrado para os filtros aplicados.</td></tr>';
    return;
  }

  filtered.forEach(r => {
    const { cls, txt } = BADGE[r.status];
    const pct = Math.round((r.atual / r.min) * 100);
    const tr  = document.createElement('tr');
    tr.setAttribute('tabindex', '0');
    tr.setAttribute('role', 'button');
    tr.setAttribute('aria-label', `Ver detalhes de ${r.produto} — status ${txt}`);
    tr.innerHTML = `
      <td><span class="product-name">${r.produto}</span></td>
      <td>${r.categoria}</td>
      <td><strong>${r.atual}</strong></td>
      <td>${r.min}</td>
      <td><span class="badge ${cls}">${txt}</span></td>`;
    tr.addEventListener('click', () => openModal(r, cls, txt, pct));
    tr.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openModal(r, cls, txt, pct); }
    });
    tbody.appendChild(tr);
  });
}

inputBusca.addEventListener('input', renderTabela);
selectCategoria.addEventListener('change', renderTabela);

renderTabela();

// ── Modal ─────────────────────────────────────────────────────────────────────
const overlay    = document.getElementById('modalOverlay');
const modalClose = document.getElementById('modalClose');

let _lastFocused = null;

function openModal(r, cls, txt, pct) {
  _lastFocused = document.activeElement;
  document.getElementById('modalTitle').textContent = r.produto;
  document.getElementById('modalBody').innerHTML = `
    <div class="modal-row"><span class="modal-label">Categoria</span><span>${r.categoria}</span></div>
    <div class="modal-row"><span class="modal-label">Qtd. Atual</span><span><strong>${r.atual}</strong></span></div>
    <div class="modal-row"><span class="modal-label">Qtd. Mínima</span><span>${r.min}</span></div>
    <div class="modal-row"><span class="modal-label">Nível do estoque</span><span>${pct}% do mínimo</span></div>
    <div class="modal-row"><span class="modal-label">Status</span><span class="badge ${cls}">${txt}</span></div>
    <div class="modal-row"><span class="modal-label">Ação recomendada</span><span>Solicitar reposição de ${r.min - r.atual} unidades</span></div>`;
  overlay.removeAttribute('hidden');
  overlay.classList.add('open');
  modalClose.focus();
}

function closeModal() {
  overlay.classList.remove('open');
  overlay.setAttribute('hidden', '');
  if (_lastFocused) _lastFocused.focus();
}

modalClose.addEventListener('click', closeModal);
overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && overlay.classList.contains('open')) closeModal(); });

// ── Export CSV ────────────────────────────────────────────────────────────────
document.getElementById('btnExport').addEventListener('click', () => {
  const filtered = getFiltered();
  const header   = ['Produto', 'Categoria', 'Qtd. Atual', 'Qtd. Mínima', 'Status'];
  const rows     = filtered.map(r => [
    r.produto, r.categoria, r.atual, r.min,
    r.status === 'crit' ? 'CRÍTICO' : 'ATENÇÃO',
  ]);
  const csv  = [header, ...rows].map(r => r.join(';')).join('\n');
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const a    = document.createElement('a');
  a.href     = URL.createObjectURL(blob);
  a.download = 'estoque-critico.csv';
  a.click();
});
