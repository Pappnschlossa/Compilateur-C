# C Pas Sorcier

Projet de création d'un compilateur C utilisant Python et la bibliothèque `lark`

## Utilisation

Cloner le repo avec `git clone https://github.com/Pappnschlossa/Compilateur-C.git` et exécuter `script.sh`.

## Fonctionnalités implémentées

### Optimisation
Marie s'est chargée de réduire autant que possible les opérations coûteuses. Les fonctionnalités d'optimisation implémentées sont :
- Utilisation du maximum de registres disponibles pour limiter le nombre de `push` et de `pop` lors des évaluations d'expressions ;
- Simplification de l'allocation de registres pour les expression de la forme `x + x`, `x - x` et `x * x` ;
- Simplification des expressions pour les opérations sur les entiers, les flottants, la multiplication par 0 ou par 1 et l'addition avec 0.

### Typage
Thibaut s'est occupé du typage dynamique. Les fonctionnalités implémentées sont :
- Intégration des données de type `float` au projet en utilisant les registres xmm ;
- Intégration de déclarations de variables dans le code (à la Python) ;
- Reconnaissance du type d'une expression permettant de réaliser des calculs entre `int` et `float` ;

### Structures
Jolan a implémenté les structures.

## Utilisation du compilateur

### Mode d'emploi
Pour utiliser le compilateur, il suffit de modifier le fichier `source.c`. Le fichier `main.py` permet de générer un code assembleur correspondant aux lignes de code de ce fichier. La sortie est stockée dans `output.txt`.

### Conventions
Le compilateur suit la syntaxe usuelle du C en introduisant du typage dynamique :
```c
typedef struct Point{
    x;
    y;
    z;
};

main() {
    x = 0;
    y = 1;
    y = 1.3;
    print(x + y);
    return (x * y);
}
```

## Commentaires

Le typage dynamique nécessite pour fonctionner d'implémenter différents types de données, ainsi que les opérations de conversion entre ces types. Nous nous sommes limités aux `int` et aux `float` dans le cadre de ce projet.
