// Importa as dependências dos outros ficheiros
import { auth } from './firebaseconfig.js';
import { ApiService } from './ApiService.js';
import { 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    onAuthStateChanged,
    signOut 
} from "https://www.gstatic.com/firebasejs/9.22.1/firebase-auth.js";

document.addEventListener('DOMContentLoaded', () => {

    // --- Elementos do DOM ---
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const telas = {
        login: document.getElementById('tela-login'),
        registo: document.getElementById('tela-registo'),
        inicio: document.getElementById('tela-inicio'),
        pergunta: document.getElementById('tela-pergunta'),
        feedback: document.getElementById('tela-feedback'),
        final: document.getElementById('tela-final')
    };
    const userInfo = document.querySelector('.user-info');
    const userEmailDisplay = document.getElementById('user-email-display');
    
    // Formulários
    const formLogin = document.getElementById('form-login');
    const formRegisto = document.getElementById('form-registo');
    const formGerarQuiz = document.getElementById('form-gerar-quiz');
    const formResposta = document.getElementById('form-resposta');

    // Botões
    const btnLogout = document.getElementById('btn-logout');
    const btnProxima = document.getElementById('btn-proxima');
    const btnReiniciar = document.getElementById('btn-reiniciar');
    
    // Links de navegação
    const showRegisterLink = document.getElementById('show-register');
    const showLoginLink = document.getElementById('show-login');

    // Elementos do Quiz
    const perguntaContador = document.getElementById('pergunta-contador');
    const textoPergunta = document.getElementById('texto-pergunta');
    const inputResposta = document.getElementById('input-resposta');
    const cardFeedback = document.getElementById('card-feedback');
    const feedbackTitulo = document.getElementById('feedback-titulo');
    const feedbackTexto = document.getElementById('feedback-texto');
    const feedbackNota = document.getElementById('feedback-nota');
    
    // --- Variáveis de Estado ---
    let apiService = null;
    let perguntasDoQuiz = [];
    let indicePerguntaAtual = 0;

    // --- Funções Auxiliares ---
    const mostrarTela = (id) => {
        Object.values(telas).forEach(tela => tela.classList.remove('active'));
        if (telas[id]) {
            telas[id].classList.add('active');
        }
    };
    const showLoading = (text) => {
        loadingText.textContent = text;
        loadingOverlay.classList.remove('hidden');
    };
    const hideLoading = () => loadingOverlay.classList.add('hidden');

    // --- Lógica de Autenticação ---
    onAuthStateChanged(auth, async (user) => {
        showLoading('A verificar sessão...');
        if (user) {
            try {
                const token = await user.getIdToken(true); // Força a atualização do token
                apiService = new ApiService(token);
                userEmailDisplay.textContent = user.email;
                userInfo.classList.remove('hidden');
                mostrarTela('inicio');
            } catch (error) {
                console.error("Erro ao obter token:", error);
                alert("Erro ao verificar sessão. Tente fazer login novamente.");
                signOut(auth);
            }
        } else {
            apiService = null;
            userInfo.classList.add('hidden');
            mostrarTela('login');
        }
        hideLoading();
    });

    formLogin.addEventListener('submit', async (e) => {
        e.preventDefault();
        showLoading('A iniciar sessão...');
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        try {
            await signInWithEmailAndPassword(auth, email, password);
        } catch (error) {
            alert(`Erro no login: ${error.message}`);
        } finally {
            hideLoading();
        }
    });

    formRegisto.addEventListener('submit', async (e) => {
        e.preventDefault();
        showLoading('A criar conta...');
        const email = document.getElementById('registo-email').value;
        const password = document.getElementById('registo-password').value;
        try {
            await createUserWithEmailAndPassword(auth, email, password);
        } catch (error) {
            alert(`Erro no registo: ${error.message}`);
        } finally {
            hideLoading();
        }
    });

    btnLogout.addEventListener('click', () => {
        showLoading('A terminar sessão...');
        signOut(auth);
    });
    showRegisterLink.addEventListener('click', (e) => { e.preventDefault(); mostrarTela('registo'); });
    showLoginLink.addEventListener('click', (e) => { e.preventDefault(); mostrarTela('login'); });

    // --- Lógica do Quiz ---
    formGerarQuiz.addEventListener('submit', async (e) => {
        e.preventDefault();
        const tema = document.getElementById('tema').value;
        const dificuldade = document.getElementById('dificuldade').value;
        const quantidade = parseInt(document.getElementById('quantidade').value, 10);
        
        if (!tema) {
            alert("Por favor, digite um tema para o quiz.");
            return;
        }

        showLoading('A IA está a gerar as suas perguntas...');
        try {
            perguntasDoQuiz = await apiService.gerarPerguntas(tema, dificuldade, quantidade);
            iniciarQuiz();
        } catch (error) {
            alert(`Erro ao gerar quiz: ${error.message}`);
        } finally {
            hideLoading();
        }
    });

    function iniciarQuiz() {
        indicePerguntaAtual = 0;
        mostrarProximaPergunta();
    }

    function mostrarProximaPergunta() {
        if (indicePerguntaAtual < perguntasDoQuiz.length) {
            const perguntaAtual = perguntasDoQuiz[indicePerguntaAtual];
            textoPergunta.textContent = perguntaAtual;
            perguntaContador.textContent = `Pergunta ${indicePerguntaAtual + 1} de ${perguntasDoQuiz.length}`;
            inputResposta.value = '';
            mostrarTela('pergunta');
        } else {
            mostrarTela('final');
        }
    }

    formResposta.addEventListener('submit', async (e) => {
        e.preventDefault();
        const respostaUsuario = inputResposta.value;
        const perguntaAtual = perguntasDoQuiz[indicePerguntaAtual];

        if (!respostaUsuario) {
            alert("Por favor, digite uma resposta.");
            return;
        }

        showLoading('A IA está a avaliar a sua resposta...');
        try {
            const avaliacao = await apiService.avaliarResposta(perguntaAtual, respostaUsuario);
            feedbackTitulo.textContent = avaliacao.nota >= 60 ? "Boa Resposta!" : "Pode Melhorar!";
            feedbackTexto.textContent = avaliacao.analise;
            feedbackNota.textContent = avaliacao.nota;
            cardFeedback.className = 'card-feedback ' + (avaliacao.nota >= 60 ? 'correto' : 'incorreto');
            mostrarTela('feedback');
        } catch (error) {
            alert(`Erro ao avaliar resposta: ${error.message}`);
        } finally {
            hideLoading();
        }
    });

    btnProxima.addEventListener('click', () => {
        indicePerguntaAtual++;
        mostrarProximaPergunta();
    });

    btnReiniciar.addEventListener('click', () => mostrarTela('inicio'));
    
    // Estado inicial
    showLoading('A carregar...');
});

