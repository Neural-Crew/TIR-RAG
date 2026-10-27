@.claude/CLAUDE-commun.md

# CLAUDE.md — TIR-RAG

Chatbot RAG (projet TIR) qui répond sur les tendances technologiques à partir de rapports PDF (Banque mondiale, WEF, McKinsey, Deloitte, OCDE). Dépôt partagé avec : Guillermo (auteur du code d'origine), Eliot, Damien.
Config du socle : `_dev/projet.json`. Règles communes : `.claude/CLAUDE-commun.md` (ne pas dupliquer ici).

## Stack

- Backend `backend/` : Python 3.11+, FastAPI, Poetry, Redis Stack (RedisJSON + RediSearch) comme base vectorielle, API OpenAI (`gpt-4.1-mini`, embeddings `text-embedding-3-large`).
- Frontend `frontend/` : React 19 + Vite 6 + Tailwind 4, port 3000 ; l'API écoute sur 8000 (`VITE_API_URL`).
- Générés (ne pas éditer à la main) : `backend/poetry.lock`, `frontend/package-lock.json`.

## Commandes

```bash
(command -v poetry >/dev/null || pipx install poetry) && poetry -C backend install --no-interaction && npm --prefix frontend ci --no-audit --no-fund   # cf. commandes.installer
cd backend && poetry run fastapi dev app/main.py   # API (Redis + backend/.env requis)
npm --prefix frontend run dev                      # front, http://localhost:3000
npm --prefix frontend run build                    # cf. commandes.construire
```

## Gros risques du projet

En plus de `CLAUDE-commun.md` § 3 :
- ⛔ `poetry run load` réindexe les PDF dans Redis et consomme l'API d'embeddings OpenAI (payant) : pas sans GO.
- ⛔ Ne commite ni `.venv/` ni un `.env` ; ne pousse pas sur `main` ni `master`.

## Pièges

- `master` versionne un `.venv/` Windows à la racine (12 700 fichiers, venv d'Eliot). Il est retiré du suivi et ignoré sur `dev/socle-claude` depuis le 27/10/2026 : à la fusion, git le supprimera des clones, ce qui est voulu. Le vrai venv Poetry vit hors dépôt (`~/.cache/pypoetry/virtualenvs`).
- `main` et `master` n'ont aucun ancêtre commun : `main` (défaut GitHub) porte une vieille version Streamlit, le code FastAPI/React est sur `master`.
- `poetry.lock` est dans `backend/`, pas à la racine : la CI du socle ne détecte pas Poetry, d'où le `pipx install poetry` de repli dans `installer`.
- Il n'y a aucun test ; `npm --prefix frontend run lint` échoue aujourd'hui.
- `app/config.py` exige `OPENAI_API_KEY` à l'import : sans `backend/.env`, rien ne démarre (ne lis jamais ce fichier).
