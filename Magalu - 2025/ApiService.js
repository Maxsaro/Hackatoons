export class ApiService {
    constructor(authToken) {
        this.authToken = authToken;
        this.gerarUrl = 'http://localhost:5000/api/gerar-pergunta';
        this.avaliarUrl = 'http://localhost:5000/api/avaliar-resposta';
    }

    async _fetchApi(url, bodyData) {
        if (!this.authToken) {
            throw new Error("Utilizador não autenticado. Token não encontrado.");
        }

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + this.authToken
            },
            body: JSON.stringify(bodyData)
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.erro || `Erro HTTP ${response.status}`);
        }
        return data;
    }

    async gerarPerguntas(tema, dificuldade, quantidade) {
        const body = { tema, dificuldade, quantidade };
        const result = await this._fetchApi(this.gerarUrl, body);
        return result.perguntas;
    }

    async avaliarResposta(pergunta, respostaUsuario) {
        const body = { pergunta, respostaUsuario };
        return await this._fetchApi(this.avaliarUrl, body);
    }
}
