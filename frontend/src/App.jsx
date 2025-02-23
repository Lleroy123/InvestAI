import { useState } from "react";

function App() {
  const [assets, setAssets] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleOptimize = async () => {
    setLoading(true);
    setResult(null);

    const response = await fetch("https://mon-api.railway.app/optimize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ assets: assets.split(",") }),
    });

    const data = await response.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Optimisation de Portefeuille</h1>
      <input
        type="text"
        placeholder="Ex: AAPL, TSLA, BTC-USD"
        value={assets}
        onChange={(e) => setAssets(e.target.value)}
      />
      <button onClick={handleOptimize} disabled={loading}>
        {loading ? "Optimisation en cours..." : "Optimiser"}
      </button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

export default App;
