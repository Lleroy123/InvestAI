from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import uvicorn

app = FastAPI()

class PortfolioRequest(BaseModel):
    assets: list

@app.get("/")
def home():
    return {"message": "Bienvenue sur l'API d'optimisation de portefeuille"}

@app.post("/optimize")
def optimize(request: PortfolioRequest):
    try:
        assets = request.assets
        if not assets:
            raise HTTPException(status_code=400, detail="Aucun actif fourni")

        data = yf.download(assets, period="3mo")["Adj Close"]
        returns = data.pct_change().dropna()
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252

        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        def portfolio_return(weights):
            return np.dot(weights, mean_returns)

        def negative_sharpe(weights):
            return -portfolio_return(weights) / portfolio_volatility(weights)

        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(len(assets)))
        initial_weights = np.array([1./len(assets)] * len(assets))

        optimized_result = minimize(negative_sharpe, initial_weights, bounds=bounds, constraints=constraints)
        optimized_weights = optimized_result.x

        allocations = dict(zip(assets, np.round(optimized_weights * 100, 2)))

        return {"optimized_allocations": allocations}
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
