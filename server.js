import express from "express";
import path from "path";

const app = express();
const __dirname = path.resolve();

// Servir a pasta public (CSS, JS, imagens)
app.use(express.static(path.join(__dirname, "public")));

// Rota principal
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
  });

  // Porta do Render
  const port = process.env.PORT || 3000;
  app.listen(port, () => {
    console.log(`Servidor rodando na porta ${port}`);
    });
    