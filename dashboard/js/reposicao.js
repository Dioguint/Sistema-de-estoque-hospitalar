const API_BASE = 'http://localhost:5000/api';

// ── Autenticação ──────────────────────────────────────────────────────────────
const usuarioLogado = sessionStorage.getItem('usuario');
if (!usuarioLogado) window.location.replace('login.html');
const usuario = JSON.parse(usuarioLogado);
document.getElementById('nomeUsuario').textContent = `Olá, ${usuario.name}`;
document.getElementById('btnLogout').addEventListener('click', () => {
  sessionStorage.removeItem('usuario');
  window.location.replace('login.html');
});

// ── Helpers ───────────────────────────────────────────────────────────────────
let apiOnline = false;

async function apiFetch(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, options);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

function showBanner(online) {
  apiOnline = online;
  const banner = document.getElementById('apiBanner');
  banner.className = online ? 'api-banner api-online' : 'api-banner api-offline';
  banner.textContent = online
    ? '🟢 Conectado ao banco de dados'
    : '🟡 API offline — reposições não serão salvas no banco';
}

function showToast(msg, tipo = 'ok') {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.className = `toast toast-${tipo} show`;
  setTimeout(() => toast.classList.remove('show'), 3500);
}

function showError(msg) {
  document.getElementById('formError').textContent = msg;
}

// ── Timestamp ─────────────────────────────────────────────────────────────────
document.getElementById('updated').textContent =
  'Atualizado: ' + new Date().toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });

// ── Produtos ──────────────────────────────────────────────────────────────────
let produtos = [];

const selectProduto = document.getElementById('selectProduto');
const produtoInfo   = document.getElementById('produtoInfo');

// Verificar se veio por query string (clique no modal do dashboard)
const params     = new URLSearchParams(window.location.search);
const preselId   = params.get('id');
const preselNome = params.get('nome');

async function carregarProdutos() {
  try {
    produtos = await apiFetch('/produtos');
    showBanner(true);
  } catch {
    showBanner(false);
    // Fallback mock
    produtos = [
      { id: 1, nome: 'Luva cirúrgica M',       categoria: 'EPI',                quantidade: 2,  estoque_min: 20 },
      { id: 2, nome: 'Soro fisiológico 500ml', categoria: 'Medicamentos',       quantidade: 4,  estoque_min: 15 },
      { id: 3, nome: 'Esparadrapo 10m',        categoria: 'Material cirúrgico', quantidade: 3,  estoque_min: 10 },
      { id: 4, nome: 'Máscara N95',            categoria: 'EPI',                quantidade: 8,  estoque_min: 30 },
      { id: 5, nome: 'Gaze estéril',           categoria: 'Material cirúrgico', quantidade: 6,  estoque_min: 10 },
      { id: 6, nome: 'Álcool 70% 1L',          categoria: 'Higiene',            quantidade: 4,  estoque_min:  8 },
      { id: 7, nome: 'Dipirona 500mg',         categoria: 'Medicamentos',       quantidade: 9,  estoque_min: 12 },
      { id: 8, nome: 'Seringa 10ml',           categoria: 'Material cirúrgico', quantidade: 14, estoque_min: 20 },
    ];
  }

  selectProduto.innerHTML = '<option value="">Selecione um produto...</option>';
  produtos.forEach(p => {
    const opt   = document.createElement('option');
    opt.value   = p.id;
    opt.textContent = `${p.nome} (${p.categoria}) — estoque: ${p.quantidade}`;
    selectProduto.appendChild(opt);
  });

  // Pré-selecionar se veio via query string
  if (preselId) {
    selectProduto.value = preselId;
    atualizarInfo();
  }
}

function atualizarInfo() {
  const id      = parseInt(selectProduto.value);
  const produto = produtos.find(p => p.id === id);
  showError('');

  if (!produto) {
    produtoInfo.hidden = true;
    document.getElementById('cardHistorico').hidden = true;
    return;
  }

  const sugestao = Math.max(0, produto.estoque_min - produto.quantidade);
  document.getElementById('infoCat').textContent      = produto.categoria;
  document.getElementById('infoQtd').textContent      = `${produto.quantidade} unidades`;
  document.getElementById('infoMin').textContent      = `${produto.estoque_min} unidades`;
  document.getElementById('infoSugestao').textContent = `${sugestao} unidades`;
  document.getElementById('inputQtd').value           = sugestao > 0 ? sugestao : '';

  produtoInfo.hidden = false;
  carregarHistorico(produto);
}

selectProduto.addEventListener('change', atualizarInfo);

// ── Histórico ─────────────────────────────────────────────────────────────────
async function carregarHistorico(produto) {
  const card = document.getElementById('cardHistorico');
  const tbody = document.getElementById('tbodyHistorico');
  document.getElementById('historicoNome').textContent = produto.nome;

  try {
    const hist = await apiFetch(`/historico/${produto.id}`);
    tbody.innerHTML = '';

    if (hist.length === 0) {
      tbody.innerHTML = '<tr class="empty-row"><td colspan="4">Sem movimentações registradas.</td></tr>';
    } else {
      hist.forEach(h => {
        const tr = document.createElement('tr');
        const tipo = h.tipo === 'entrada'
          ? '<span class="badge badge-ok">ENTRADA</span>'
          : '<span class="badge badge-crit">SAÍDA</span>';
        const data = new Date(h.data).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
        tr.innerHTML = `<td>${tipo}</td><td>${h.quantidade}</td><td>${h.observacao || '—'}</td><td>${data}</td>`;
        tbody.appendChild(tr);
      });
    }
    card.hidden = false;
  } catch {
    card.hidden = true;
  }
}

// ── Confirmar reposição ───────────────────────────────────────────────────────
document.getElementById('btnConfirmar').addEventListener('click', async () => {
  showError('');
  const id         = parseInt(selectProduto.value);
  const quantidade = parseInt(document.getElementById('inputQtd').value);
  const observacao = document.getElementById('inputObs').value.trim() || 'Reposição via dashboard';

  if (!id)                 return showError('Selecione um produto.');
  if (!quantidade || quantidade <= 0) return showError('Informe uma quantidade válida.');

  const produto = produtos.find(p => p.id === id);

  if (!apiOnline) {
    // Simula localmente
    produto.quantidade += quantidade;
    atualizarInfo();
    showToast(`✔ ${produto.nome}: +${quantidade} unidades (simulado — API offline)`, 'ok');
    return;
  }

  try {
    const result = await apiFetch('/entrada', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ produto_id: id, quantidade, observacao }),
    });

    // Atualiza quantidade local
    produto.quantidade = result.qtd_depois;

    // Atualiza select
    const opt = selectProduto.querySelector(`option[value="${id}"]`);
    if (opt) opt.textContent = `${produto.nome} (${produto.categoria}) — estoque: ${produto.quantidade}`;

    atualizarInfo();
    showToast(`✔ ${result.produto}: ${result.qtd_antes} → ${result.qtd_depois} (+${quantidade})`, 'ok');
    document.getElementById('inputQtd').value = '';
    document.getElementById('inputObs').value = '';

  } catch (err) {
    showError('Erro ao registrar entrada. Verifique se a API está rodando.');
  }
});

// ── Init ──────────────────────────────────────────────────────────────────────
carregarProdutos();
