#!/usr/bin/env python3
"""
Baixa um arquivo do OneDrive for Business / SharePoint a partir de um link
de compartilhamento "qualquer pessoa com o link pode acessar".

Links modernos desse tipo (formato .../:x:/g/personal/<usuario>/<id>?...)
abrem uma pagina interativa (Office Online) quando acessados direto, em vez
de entregar o arquivo binario. O endpoint _layouts/15/download.aspx, que
existe nativamente em qualquer site do SharePoint/OneDrive, aceita o mesmo
ID de compartilhamento e devolve o conteudo bruto do arquivo, sem precisar
de login nem de credenciais de API, desde que o link seja realmente publico.

Uso:
    python download_xlsx.py <url_de_compartilhamento> <arquivo_de_saida>
"""
import re
import sys
import urllib.parse
import urllib.request
import urllib.error


def montar_url_download(url_compartilhamento: str) -> str:
    partes = urllib.parse.urlsplit(url_compartilhamento)
    dominio = f"{partes.scheme}://{partes.netloc}"
    # remove o prefixo ":x:/g/", ":x:/s/", ":x:/r/" etc.
    caminho = re.sub(r"^/:[a-zA-Z]:/[a-zA-Z]/", "/", partes.path)
    segmentos = [s for s in caminho.strip("/").split("/") if s]
    if len(segmentos) < 2:
        raise ValueError(f"Nao foi possivel interpretar o link: {url_compartilhamento}")
    share_id = segmentos[-1]
    pasta = "/".join(segmentos[:-1])
    return f"{dominio}/{pasta}/_layouts/15/download.aspx?share={share_id}"


def main():
    if len(sys.argv) != 3:
        print("Uso: download_xlsx.py <url_de_compartilhamento> <arquivo_de_saida>")
        sys.exit(1)

    url_origem, destino = sys.argv[1], sys.argv[2]
    download_url = montar_url_download(url_origem)
    print(f"URL de origem (secret): {url_origem}")
    print(f"URL de download convertida: {download_url}")

    req = urllib.request.Request(
        download_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0 Safari/537.36",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "desconhecido")
            corpo = resp.read()
    except urllib.error.HTTPError as e:
        print(f"Erro HTTP {e.code} ao baixar o arquivo: {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Erro de rede ao baixar o arquivo: {e.reason}")
        sys.exit(1)

    print(f"Resposta HTTP {status}, Content-Type: {content_type}, {len(corpo)} bytes recebidos")

    with open(destino, "wb") as f:
        f.write(corpo)

    # Diagnostico extra: se nao for um .xlsx (zip) valido, mostra o inicio
    # do conteudo para ajudar a identificar o problema (ex.: pagina de
    # login HTML em vez do arquivo).
    if corpo[:2] != b"PK":
        trecho = corpo[:300].decode("utf-8", errors="replace")
        print("AVISO: o conteudo baixado nao parece ser um .xlsx (zip) valido.")
        print("Primeiros bytes da resposta, para diagnostico:")
        print(trecho)


if __name__ == "__main__":
    main()
