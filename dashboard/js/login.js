// Credenciais de demonstração (substituir por API real futuramente)
const USERS = [
  { username: 'admin', password: '123', name: 'Administrador' },
  { username: 'estoque', password: '123', name: 'Operador de Estoque' },
];

const form        = document.getElementById('loginForm');
const inputUser   = document.getElementById('username');
const inputPass   = document.getElementById('password');
const errorMsg    = document.getElementById('loginError');

// Se já está logado, redireciona direto
if (sessionStorage.getItem('usuario')) {
  window.location.replace('index.html');
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  errorMsg.textContent = '';

  const username = inputUser.value.trim();
  const password = inputPass.value;

  const user = USERS.find(u => u.username === username && u.password === password);

  if (user) {
    sessionStorage.setItem('usuario', JSON.stringify({ username: user.username, name: user.name }));
    window.location.replace('index.html');
  } else {
    errorMsg.textContent = 'Usuário ou senha inválidos.';
    inputPass.value = '';
    inputPass.focus();
  }
});
