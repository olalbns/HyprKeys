# HyprKeys

Explorateur GTK4 de raccourcis Hyprland. HyprKeys lit votre configuration et
les fichiers inclus pour afficher tous vos raccourcis dans une interface
recherchable.

## Fonctions

- Lecture de `hyprland.conf` et des fichiers `source = ...` ;
- recherche par touche, commande ou commentaire ;
- catégories fenêtres, espaces de travail, multimédia et système ;
- détection de raccourcis en doublon ;
- ajout d’un raccourci depuis l’interface ;
- ouverture de la configuration et rechargement de Hyprland.

## Installation sur Arch Linux

```bash
yay -S hyprkeys-git
```

## Utilisation

Lancez HyprKeys avec :

```bash
hyprkeys
```

Raccourci Hyprland conseillé :

```ini
bind = SUPER, K, exec, hyprkeys
```

### Ajouter un raccourci

Cliquez sur **Add shortcut**, remplissez les modificateurs, la touche, le
dispatcher et la commande. HyprKeys ajoute la règle dans votre `hyprland.conf`
et crée automatiquement une sauvegarde horodatée à côté du fichier.

Cliquez ensuite sur **Reload Hyprland** pour appliquer le raccourci.
