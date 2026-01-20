# Guide des Coûts : Vercel & Supabase

Bonne nouvelle ! Pour votre utilisation (**environ 100 clients par mois**, avec la majorité des transactions finalisées sur WhatsApp), vous pouvez héberger votre site **gratuitement** sans problème.

Voici le détail pour vous rassurer :

## 1. Vercel (Hébergement du Site) - Plan "Hobby" (Gratuit)

Vercel est très généreux pour les petits projets.

| Ressource | Limite Gratuite | Votre estimation (100 clients) | Verdict |
| :--- | :--- | :--- | :--- |
| **Bande passante** | 100 Go / mois | ~0.5 Go (si images optimisées) | ✅ **Large** |
| **Visites** | Illimité (fair usage) | ~1,000 - 5,000 visites | ✅ **Large** |
| **Fonctions (Serverless)** | 1 Million d'appels / mois | ~10,000 appels (pages dynamiques) | ✅ **Large** |
| **Coût** | **0$** | **0$** | **Gratuit** |

**Note :** Le plan gratuit de Vercel est destiné à un usage "personnel" ou "non-commercial" strict sur le papier, mais pour une petite boutique artisanale qui démarre, c'est généralement toléré tant que le trafic reste faible. Si vous grossissez beaucoup, ils vous demanderont de passer au plan Pro (20$/mois).

## 2. Supabase (Base de Données) - Plan "Free"

Supabase stocke vos produits, catégories et commandes.

| Ressource | Limite Gratuite | Votre estimation | Verdict |
| :--- | :--- | :--- | :--- |
| **Taille Base de Données** | 500 Mo | ~10-20 Mo (pour ~1000 produits/commandes) | ✅ **Large** |
| **Utilisateurs (Auth)** | 50,000 actifs / mois | 100 - 200 | ✅ **Large** |
| **Stockage Fichiers (Images)**| 1 Go | Suffisant pour ~200-500 photos produits HD | ✅ **OK** |
| **Bande passante DB** | 5 Go / mois | < 1 Go | ✅ **Large** |
| **Coût** | **0$** | **0$** | **Gratuit** |

### ⚠️ Point Important : La "Pause" Supabase
Sur le plan gratuit, Supabase **met en pause** les projets après **1 semaine d'inactivité** (si personne ne visite le site ou n'utilise l'admin).
*   **Conséquence :** Le premier client après une pause devra attendre quelques secondes de plus que le site "réveille" la base de données.
*   **Solution :** Tant que vous avez quelques visiteurs par semaine, cela n'arrivera pas. Si cela devient gênant, le plan payant commence à 25$/mois.

## Résumé
*   **Coût mensuel actuel :** **0 DH (Gratuit)**.
*   **Seul coût obligatoire :** Le nom de domaine (environ 100-150 DH **par an** chez Namecheap/GoDaddy).

Vous pouvez grandir sereinement jusqu'à plusieurs milliers de clients avant de devoir payer l'hébergement !
