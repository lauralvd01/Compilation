# Compilation

Compilation de float et quaternions

Synthaxe pour afficher des opérations sur des entiers, des float et des quaternions :

Affichage simple avec print
print(17)
print(1.7)
print(1.7 + 2.2 i + 2.3 j + 7.0 k)

Opérations sur des entiers : + - *
(ordre de priorité particulier à grammaire.parse, il faut rajouter des paranthèses pour obtenir l'ordre voulu)
print(3 + 5 - 9 * 2 )
print(3 + 5 - (9 * 2) )

Opérations sur des float : + - *
(ordre de priorité particulier à grammaire.parse, il faut rajouter des paranthèses pour obtenir l'ordre voulu)
print(1.3 + 4.5 - 8.9 * 1.2 )
print(1.3 + 4.5 - (8.9 * 1.2))

Opérations sur des quaternions : + - *
(ordre de priorité particulier à grammaire.parse, il faut rajouter des paranthèses pour obtenir l'ordre voulu)
print(1.7 + 2.2 i + 2.3 j + 7.0 k + 1.7 + 2.2 i + 2.3 j + 7.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k - 1.0 + 1.0 i + 1.0 j + 1.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k - 1.7 + 2.2 i + 2.3 j + 7.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k * 0.0 + 0.0 i + 0.0 j + 0.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k * 2.0 + 0.0 i + 0.0 j + 0.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k * 1.7 + 2.2 i + 2.3 j + 7.0 k)

Affichage de la partie réelle d'un quaternion
print(re(1.7 + 2.2 i + 2.3 j + 7.0 k))

Calcul de la partie imaginaire d'un quaternion
print(im(1.7 + 2.2 i + 2.3 j + 7.0 k))

Affichage des coordonnées i, j et k d'un quaternion
print(1.7 + 2.2 i + 2.3 j + 7.0 k .i)
print(1.7 + 2.2 i + 2.3 j + 7.0 k .j)
print(1.7 + 2.2 i + 2.3 j + 7.0 k .k)


Synthaxe pour créer des variables, leur assigner une valeur, les afficher et effectuer des opérations dessus :

x = 3;
y = 4.6;
z = 1.7 + 2.2 i + 2.3 j + 7.0 k .k;
x = x + 4;
x = 6 * x;
print(x)
print(y)
print(z)


Synthaxe pour créer une boucle while ou un if
(la condition est la valeur d'un entier : true = 1 et le reste signifie false)

x = 1;
y = 8;
while(x){
    y = y + 1;
    if(x){
        x = 0;
    }
}
print(x)
print(y)


Utiliser des arguments dans main() : 
Les seuls arguments acceptés sont des entiers
Ils s'utilisent comme des variables