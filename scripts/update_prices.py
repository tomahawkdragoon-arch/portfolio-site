"""Fetch the latest closing prices, recalculate portfolio weights, and write site/data/live.json.

Runs on a schedule in GitHub Actions. Share counts and cash come from the PORTFOLIO_JSON secret
(or a local portfolio.json when testing), so only prices and percentage weights are ever made public.
"""
import json
import os
import pathlib
from datetime import datetime, timezone

import yfinance as yf

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "portfolio.json"
OUT = ROOT / "site" / "data" / "live.json"


def last_close(symbol, digits=2):
    """Return (price, date) of the most recent daily close for a Yahoo Finance symbol."""
    hist = yf.Ticker(symbol).history(period="7d", interval="1d", auto_adjust=False)
    hist = hist.dropna(subset=["Close"])
    if hist.empty:
        raise RuntimeError(f"No price data returned for {symbol}")
    return round(float(hist["Close"].iloc[-1]), digits), hist.index[-1].date().isoformat()


def main():
    raw = os.environ.get("PORTFOLIO_JSON") or (CONFIG.read_text() if CONFIG.exists() else "")
    if not raw.strip():
        raise RuntimeError("Add your holdings as the PORTFOLIO_JSON repository secret")
    cfg = json.loads(raw)
    usdcad, _ = last_close("CAD=X", digits=4)  # Canadian dollars per US dollar

    prices, values, dates = {}, {}, []
    for h in cfg["holdings"]:
        price, day = last_close(h["symbol"])
        fx = usdcad if h.get("currency", "CAD") == "USD" else 1.0
        prices[h["id"]] = (price, h.get("currency", "CAD"))
        values[h["id"]] = h["shares"] * price * fx
        dates.append(day)

    cash = cfg.get("cash", {})
    cash_cad = cash.get("CAD", 0) + cash.get("USD", 0) * usdcad
    total = sum(values.values()) + cash_cad
    if total <= 0:
        raise RuntimeError("Portfolio total is zero; check portfolio.json")

    out = {
        "asOf": max(dates) if dates else datetime.now(timezone.utc).date().isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fx": {"USDCAD": round(usdcad, 4)},
        "holdings": {
            hid: {"price": p, "currency": cur, "weight": round(values[hid] / total * 100, 1)}
            for hid, (p, cur) in prices.items()
        },
    }
    out["holdings"]["cash"] = {"weight": round(cash_cad / total * 100, 1)}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
