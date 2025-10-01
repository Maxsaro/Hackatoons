// Importa a função de inicialização
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
// Importa as funções dos serviços que vamos usar
import { getAuth } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-auth.js";

// A sua configuração do Firebase (copiada do seu ficheiro)
const firebaseConfig = {
  apiKey: "AIzaSyAfUR8ifEPaUxkK2rQMKRe7HCr9yxZiCSk",
  authDomain: "magalu-382f4.firebaseapp.com",
  projectId: "magalu-382f4",
  storageBucket: "magalu-382f4.appspot.com",
  messagingSenderId: "568101607955",
  appId: "1:568101607955:web:6ce378af3d86b71e53fde6",
};

// Inicializa o Firebase
const app = initializeApp(firebaseConfig);

// Exporta as instâncias dos serviços para serem usadas em outros ficheiros
export const auth = getAuth(app);
