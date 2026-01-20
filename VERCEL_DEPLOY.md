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
Une fois que vous avez vérifié que tout fonctionne, vous pouvez utiliser votre propre nom de domaine (comme `luxfakia.ma`).

1.  **Achetez votre domaine** chez un registrar (GoDaddy, Namecheap, hostinger, etc.).
2.  **Ajoutez le domaine sur Vercel :**
    *   Allez sur votre projet dans Vercel.
    *   Allez dans **Settings** -> **Domains**.
    *   Entrez votre nom de domaine (ex: `luxfakia.ma`) et cliquez sur **Add**.
    *   Choisissez "Add `luxfakia.ma` and `www.luxfakia.ma`" (recommandé).

3.  **Configurez les DNS chez votre registrar :**
    Connectez-vous au site où vous avez acheté votre domaine et cherchez la gestion des **DNS** ou **Zone DNS**. Ajoutez les enregistrements suivants :

    | Type  | Nom (Host) | Valeur (Target)       |
    | :---: | :--------: | :-------------------- |
    | **A** | `@`        | `76.76.21.21`         |
    | **CNAME**| `www`   | `cname.vercel-dns.com`|

    *Note : Supprimez les anciens enregistrements de type A ou CNAME s'ils existent déjà pour éviter les conflits.*

4.  **Attendez la propagation :**
    Cela peut prendre de quelques minutes à 24 heures. Vercel affichera une coche verte ✅ à côté de votre domaine une fois que tout est prêt.

## Est-ce que c'est payant ?
Pour votre usage (boutique locale, < 100 clients/mois), **NON**, vous n'avez pas besoin de payer Vercel ou Supabase.
*   Consultez le fichier `PRICING_GUIDE.md` pour tous les détails sur les quotas gratuits.
*   Le seul frais sera votre nom de domaine (~100-150 DH/an) que vous payez à votre registrar (pas à Vercel).
