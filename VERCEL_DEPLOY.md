# Guide de Déploiement Gratuit (Vercel + Supabase)

Ce guide vous explique comment héberger votre site **gratuitement** en utilisant Vercel (pour le site) et Supabase (pour la base de données).

## Étape 1 : Créer la Base de Données (Supabase)
Comme Vercel ne permet pas de stocker des fichiers (comme votre base de données SQLite locale), vous devez utiliser une base de données externe.

1.  Allez sur [Supabase.com](https://supabase.com/) et cliquez sur "Start your project".
2.  Inscrivez-vous (vous pouvez utiliser votre compte GitHub).
3.  Créez un **Nouveau Projet** :
    *   **Name:** `luxfakia-db`
    *   **Password:** Générez un mot de passe fort et **copiez-le** (vous en aurez besoin).
    *   **Region:** Choisissez une région proche (ex: London ou Frankfurt).
4.  Une fois le projet créé (cela prend quelques minutes), cliquez sur le bouton **Connect** en haut à droite.
5.  Sélectionnez l'onglet **Transaction Pooler** (ou assurez-vous de choisir le mode "Transaction" et le port **6543**).
    *   **Important pour Vercel :** Vercel ne supporte pas la connexion directe (IPv6). Vous **devez** utiliser le Transaction Pooler (Port 6543) qui est compatible IPv4.
6.  Copiez la chaîne de connexion (URI). Elle ressemblera à ceci (notez le port **6543** et le domaine `pooler`) :
    `postgresql://postgres.[REFERENCE-PROJET]:[VOTRE-MOT-DE-PASSE]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
    *   *Remplacer `[VOTRE-MOT-DE-PASSE]` par le vrai mot de passe.*

## Étape 2 : Déployer sur Vercel
1.  Allez sur [Vercel.com](https://vercel.com/) et inscrivez-vous avec **GitHub**.
2.  Cliquez sur **"Add New..."** -> **"Project"**.
3.  Sélectionnez le dépôt GitHub `luxfakia` et cliquez sur **Import**.
4.  Dans la configuration du projet :
    *   **Framework Preset:** Laissez sur "Other" ou sélectionnez "Flask" si détecté.
    *   **Root Directory:** `./` (par défaut).
    *   **Environment Variables:** Cliquez sur cette section pour l'ouvrir.
        *   **Name:** `DATABASE_URL`
        *   **Value:** Collez l'URI du **Transaction Pooler** (port 6543) copié à l'étape 1.
        *   *(Optionnel)* Ajoutez `SECRET_KEY` avec une valeur aléatoire longue pour la sécurité.
5.  Cliquez sur **Deploy**.

## Étape 3 : Vérification
1.  Attendez que le déploiement soit terminé.
2.  Vercel vous donnera une URL (ex: `luxfakia.vercel.app`).
3.  Cliquez dessus.
    *   *Note :* Le site mettra quelques secondes à charger la première fois (c'est normal pour l'offre gratuite).
4.  La base de données sera vide au début. L'application est configurée pour créer les tables automatiquement.

## Étape 4 : (Plus Tard) Connecter votre Nom de Domaine
Une fois que vous avez vérifié que tout fonctionne :
1.  Achetez votre nom de domaine (ex: `luxfakia.ma`).
2.  Dans Vercel, allez dans **Settings** -> **Domains**.
3.  Ajoutez votre domaine.
4.  Vercel vous donnera les instructions DNS (des records `A` ou `CNAME`) à entrer là où vous avez acheté votre domaine.
