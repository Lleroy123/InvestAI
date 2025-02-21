import React, { useState } from "react";
import axios from "axios";

function App() {
  const [assets, setAssets] = useState("");
  const [result, setResult] = useState(null);

  const handleOptimize = async () => {
    try {
      const response = await axios.post(
        "https://mon-api.railway.app/optimize",
        {
          assets: assets.split(","),
        }
      );
      setResult(response.data.optimized_allocations);
    } catch (error) {
      console.error("Erreur:", error);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>Optimisation de Portefeuille</h1>
      <input
        type="text"
        placeholder="Ex: AAPL, TSLA, BTC-USD"
        value={assets}
        onChange={(e) => setAssets(e.target.value)}
      />
      <button onClick={handleOptimize}>Optimiser</button>

      {result && (
        <div>
          <h2>Résultats :</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
