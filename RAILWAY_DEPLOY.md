# Deploying to Railway

This guide outlines the steps to deploy the application to Railway.app.

## Prerequisites

*   A [GitHub](https://github.com/) account.
*   A [Railway](https://railway.app/) account.
*   The [Railway CLI](https://docs.railway.app/guides/cli) (optional, but useful for seeding).

## Deployment Steps

1.  **Push to GitHub**: Ensure your code is pushed to a GitHub repository.

2.  **Create a New Project on Railway**:
    *   Go to your Railway dashboard.
    *   Click "New Project".
    *   Select "Deploy from GitHub repo".
    *   Select your repository.

3.  **Ajouter la Base de Données (PostgreSQL)** :
    *   Dans votre projet Railway, cliquez sur le bouton **+ New** (ou faites un clic droit sur la zone vide).
    *   Sélectionnez **Database** -> **PostgreSQL**.
    *   Une fois la base créée, Railway ajoute automatiquement une variable `DATABASE_URL` aux services qui en ont besoin (ou vous devrez lier les services).
    *   *Astuce :* Vérifiez dans l'onglet "Variables" de votre site web que `DATABASE_URL` est bien présent et rempli (`postgresql://...`).

4.  **Configurer les Variables** :
    *   Cliquez sur votre service web (celui avec le logo GitHub).
    *   Allez dans l'onglet **Variables**.
    *   Ajoutez `SECRET_KEY` avec une longue chaîne aléatoire.

5.  **Configurer le Nom de Domaine (Custom Domain)** :
    *   Allez dans l'onglet **Settings** de votre service web.
    *   Descendez à la section **Networking** -> **Public Networking**.
    *   Cliquez sur **Custom Domain**.
    *   Entrez votre domaine (ex: `luxfakia.ma`).
    *   Railway va vous donner les enregistrements DNS à configurer chez votre registrar (là où vous avez acheté le domaine) :
        *   **Type :** `CNAME`
        *   **Nom (Host) :** `www` (ou `@` si supporté par votre registrar via CNAME flattening/Alias)
        *   **Valeur :** `votre-projet.up.railway.app` (l'adresse fournie par Railway).
    *   *Note :* La propagation peut prendre quelques heures.

## Initialisation de la Base de Données

Pas besoin de commande compliquée !
L'application est configurée pour **détecter automatiquement** si la base est vide au démarrage. Elle créera les tables et ajoutera les données par défaut (Admin, Catégories, Produits) toute seule lors du premier déploiement.

Vous n'avez rien à faire d'autre que d'attendre que le déploiement soit "Active".

## Troubleshooting

*   **Logs**: Check the "Deploy Logs" and "App Logs" in the Railway dashboard.
*   **Database Connection**: Ensure the PostgreSQL service is in the same project and environment.
