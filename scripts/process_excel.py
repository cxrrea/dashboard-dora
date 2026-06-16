#!/usr/bin/env python3
"""
Le o relatorio Envelope Report do DocuSign (.xlsx) e gera dados.json
no formato consumido pelo dashboard estatico (index.html).

Uso:
    python process_excel.py caminho/para/relatorio.xlsx caminho/para/dados.json
"""
import sys
import json
import math
from datetime import datetime, timezone

import pandas as pd


def parse_dd_hh_mm(valor):
    """Converte 'DD:HH:MM' em dias (float). Replica parseDDHHMM do dashboard."""
    if valor is None:
        return None
    texto = str(valor).strip()
    if texto == "" or texto.lower() == "nan":
        return None
    partes = texto.split(":")
    if len(partes) != 3:
        return None
    try:
        dd, hh, mm = (int(p) for p in partes)
    except ValueError:
        return None
    return dd + hh / 24 + mm / 1440


def combinar_data_hora(data, horario):
    """Combina a coluna de data (datetime, hora=00:00) com a coluna de horario ('HH:MM:SS')."""
    if data is None or pd.isna(data):
        return None
    if horario is None or (isinstance(horario, float) and math.isnan(horario)):
        return data.to_pydatetime()
    try:
        h, m, s = (int(p) for p in str(horario).split(":"))
        return data.replace(hour=h, minute=m, second=s).to_pydatetime()
    except (ValueError, AttributeError):
        return data.to_pydatetime()


def main():
    if len(sys.argv) != 3:
        print("Uso: process_excel.py <entrada.xlsx> <saida.json>")
        sys.exit(1)

    entrada, saida = sys.argv[1], sys.argv[2]
    df = pd.read_excel(entrada)

    registros = []
    for _, linha in df.iterrows():
        enviado = combinar_data_hora(linha.get("Enviado em (Data)"), linha.get("Enviado em (Horário)"))
        if enviado is None:
            continue  # mesma regra do dashboard: descarta linhas sem data de envio

        concluido = combinar_data_hora(linha.get("Concluído em (Data)"), linha.get("Concluído em (Horário)"))
        dias = parse_dd_hh_mm(linha.get("Hora de conclusão (DD:HH:MM)"))

        registros.append({
            "assunto": str(linha.get("Assunto") or "").strip(),
            "categoria": str(linha.get("Categoria") or "").strip(),
            "status": str(linha.get("Status") or "").strip(),
            "enviado": enviado.isoformat(),
            "concluido": concluido.isoformat() if concluido else None,
            "dias": dias,
            "dentro48": bool(dias is not None and dias <= 2),
        })

    saida_json = {
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
        "total_registros": len(registros),
        "dados": registros,
    }

    with open(saida, "w", encoding="utf-8") as f:
        json.dump(saida_json, f, ensure_ascii=False, indent=2)

    print(f"OK: {len(registros)} registros escritos em {saida}")


if __name__ == "__main__":
    main()
