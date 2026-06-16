# Dashboard SLA DocuSign — MeuChapa

Dashboard estático (GitHub Pages) que exibe o SLA de assinaturas do DocuSign.
Os dados vêm de uma planilha `.xlsx` armazenada no OneDrive/SharePoint e são
atualizados sob demanda, com um clique, via GitHub Actions — sem servidor,
sem custo.

## Como funciona

1. Você clica em "Run workflow" na aba **Actions** do GitHub.
2. O workflow baixa a planilha do link público do OneDrive/SharePoint,
   converte para `dados.json` e comita esse arquivo no repositório.
3. O GitHub Pages serve o `index.html`, que carrega o `dados.json` via
   `fetch()` e renderiza o dashboard.

Se o `dados.json` ainda não existir (antes da primeira execução) ou estiver
indisponível, a tela cai automaticamente no modo de upload manual (arrastar o
`.xlsx` para o navegador), que já funciona 100% local, sem depender de nada.

## Configuração inicial (uma vez só)

1. Crie um repositório no GitHub (pode ser público) e suba todos os arquivos
   desta pasta para a raiz dele (`index.html`, `dados.json`, `scripts/`,
   `.github/`).
2. Em **Settings → Pages**, em "Build and deployment", selecione
   **Deploy from a branch**, branch `main`, pasta `/ (root)`. Salve.
   O GitHub mostrará a URL pública (algo como
   `https://seu-usuario.github.io/seu-repo/`).
3. Em **Settings → Secrets and variables → Actions → New repository
   secret**, crie um secret chamado `ONEDRIVE_FILE_URL` com o link de
   compartilhamento da planilha (o link "qualquer pessoa com o link pode
   acessar").

## Atualizando os dados

O workflow agora roda automaticamente **a cada 15 minutos**, verificando a
planilha no OneDrive/SharePoint. Se algo mudou desde a última verificação,
ele atualiza o `dados.json` sozinho — você não precisa clicar em nada no
dia a dia.

Duas observações importantes sobre esse modo automático:

- O agendamento do GitHub Actions é "melhor esforço": nos horários de pico
  ele pode atrasar alguns minutos em relação ao `*/15` exato. Isso é
  normal e documentado pelo próprio GitHub.
- Se o repositório ficar **60 dias sem nenhum commit**, o GitHub desativa
  os workflows agendados automaticamente (não os manuais). Se isso
  acontecer, basta reativar em Actions → o workflow aparecerá com um aviso
  e um botão para reativar.
- Se o repositório for **privado**, rodar a cada 15 minutos consome
  bastante da cota gratuita de minutos do Actions (2.000 min/mês). Se o
  repositório for **público**, os minutos do Actions são ilimitados e
  gratuitos — recomendo manter público, já que o link da planilha
  compartilhada já não é confidencial por si só.

Você também pode disparar manualmente quando quiser, sem esperar o
agendamento: aba **Actions** → workflow **"Atualizar dashboard SLA"** →
**Run workflow**.

## Estrutura

```
.
├── index.html                          # o dashboard (estático)
├── dados.json                          # gerado automaticamente — não editar manualmente
├── scripts/
│   ├── download_xlsx.py                # baixa o .xlsx do link do OneDrive/SharePoint
│   └── process_excel.py                # converte o .xlsx em dados.json
└── .github/workflows/
    └── atualizar-dashboard.yml         # workflow manual (workflow_dispatch)
```

## Observações sobre o link do OneDrive/SharePoint

Links modernos de compartilhamento do OneDrive for Business/SharePoint
(`.../:x:/g/personal/<usuario>/<id>?...`) abrem uma página interativa
(Office Online) em vez de entregar o arquivo direto. Por isso o workflow
usa o `scripts/download_xlsx.py`, que converte esse link para o endpoint
nativo `_layouts/15/download.aspx?share=<id>` — esse sim devolve o
conteúdo binário do arquivo, sem precisar de login, desde que o
compartilhamento esteja configurado como "qualquer pessoa com o link".

Se mesmo assim o download falhar, o log da etapa "Baixar planilha" mostra
o código HTTP recebido e os primeiros bytes da resposta — geralmente isso
revela o motivo (por exemplo, uma página de login significa que o link na
prática está restrito à organização, não realmente público).

## Sobre a logo

Removi a logo em base64 do HTML original para manter o arquivo leve — hoje
aparece como uma badge de texto "MEUCHAPA". Se quiser a logo de volta, suba
um arquivo `logo.png` na raiz do repositório e troque a badge por
`<img src="logo.png" style="height:34px">`.
