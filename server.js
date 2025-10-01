import express from "express";
import path from "path";

const app = express();
const __dirname = path.resolve();

// --- Serve arquivos estáticos da pasta "public" ---
app.use(express.static(path.join(__dirname, "public")));

// --- Rota principal para o index.html ---
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
  });

  // --- Qualquer outra rota redireciona para o index (opcional, útil para SPA) ---
  app.get("*", (req, res) => {
    res.sendFile(path.join(__dirname, "index.html"));
    });

    // --- Porta do Render ---
    const port = process.env.PORT || 3000;
    app.listen(port, () => {
      console.log(`Servidor rodando na porta ${port}`);
      });