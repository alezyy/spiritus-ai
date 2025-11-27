# Documentation du Système d'Abonnement (Membership)

Ce document explique le fonctionnement du système d'abonnement personnalisé intégré à cette instance d'Open WebUI et la procédure à suivre lors des mises à jour de l'application.

## 1. Vue d'ensemble

Le système permet aux utilisateurs de souscrire à un abonnement "Plus" (20$/mois) via Stripe pour accéder à des fonctionnalités premium.

### Comment ça marche ?

1.  **Souscription** : L'utilisateur paie via Stripe (page `/subscription`).
2.  **Activation** :
    *   Une fois le paiement validé, Stripe envoie une notification (Webhook) à votre serveur.
    *   Le serveur ajoute automatiquement l'utilisateur au groupe **`group_premium`**.
3.  **Permissions** :
    *   C'est ce groupe `group_premium` qui donne les droits.
    *   Vous configurez les modèles auxquels ce groupe a accès directement dans l'interface d'administration d'Open WebUI (**Admin Panel -> Groups -> group_premium -> Edit -> Model Access**).
4.  **Renouvellement / Annulation** :
    *   Si l'abonnement expire ou est annulé, Stripe prévient le serveur.
    *   L'utilisateur est automatiquement retiré du groupe `group_premium`.

## 2. Mise à jour d'Open WebUI

Comme nous avons modifié le code source d'Open WebUI pour ajouter cette fonctionnalité, une mise à jour standard (ex: `git pull`) risque d'écraser nos modifications.

Nous avons créé un script spécial pour réappliquer automatiquement nos changements après une mise à jour.

### Procédure de mise à jour (Pas à pas)

1.  **Récupérer la dernière version d'Open WebUI** :
    ```bash
    git pull origin main
    ```
    *(Ou la commande que vous utilisez habituellement pour mettre à jour)*

2.  **Réinstaller le module d'abonnement** :
    Exécutez simplement le script d'installation inclus à la racine :
    ```bash
    python3 install_subscription.py
    ```
    *Ce script va vérifier les fichiers et réinjecter le code nécessaire pour Stripe et la gestion des groupes.*

3.  **Reconstruire et Redémarrer** :
    Pour que les changements prennent effet, il faut reconstruire le conteneur Docker :
    ```bash
    docker-compose up -d --build
    ```

### En cas de conflit
Si le script `install_subscription.py` signale une erreur (par exemple si la structure d'Open WebUI a radicalement changé), il faudra vérifier manuellement les fichiers modifiés (`backend/open_webui/routers/payments.py`, etc.) ou faire appel à un développeur.

## 3. Dépannage

*   **L'utilisateur a payé mais reste en "Free"** :
    *   Vérifiez que votre tunnel (Ngrok ou autre) est actif si vous êtes en local.
    *   Vérifiez les logs pour voir si le Webhook Stripe a été reçu : `docker logs open-webui | grep webhook`.
    *   Vérifiez dans le Dashboard Stripe que le webhook n'est pas en erreur.

*   **La date de renouvellement ne s'affiche pas** :
    *   Cela peut arriver juste après le paiement. Rafraîchissez la page après quelques secondes.

## 4. Fichiers Clés

*   `install_subscription.py` : Le script magique pour réinstaller.
*   `backend/open_webui/routers/payments.py` : Toute la logique de paiement et de gestion de groupe.
*   `src/routes/(app)/subscription/+page.svelte` : La page d'abonnement (Frontend).

## The url git : https://github.com/falezy/openwebui-stripe
