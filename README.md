=======
# Compilation : Arrays

compiloArray.py 
  
  Compilateur permettant la manipulation de tableaux d'entiers.

  Commandes liées à la manipulation de tableaux :
  
    - tab = [n] : pour créer un tableau de taille n et de nom tab
    - tab[i]  : pour accéder à la i-ème valeur du tableau
    - tab[i] = val;  : pour affecter la valeur val au i-ème élément du tableau
    - tab[-1] : pour accéder à la taille du tableau


=======
# Compilation : Dynamic Typing

CompiloDynamicTyping.py

Compilator that implements Dynamic Typing.
you can freely change type between integers and floats.
It is made to be adaptable to other type such as quaternions.
 
Limits of the compilator :
-initial arguments have to be integers
-it is not possible to make binary operation between an integer and a float
-There are some problems with the while statement when the argument is a float
-There are some problems with the if statement if the argument was changed in a while statement before

 possibilities :
 All those possibilities are on the Dynamic Typing compilator for you to test

-changing type between int and float
ast1 = grammaire.parse(""" main(y){

        x = 5;
        print(x)
        x = 2.5;
        print(x)
        x = 3;
        print(x)
 return (y);
 }
""")

-Adding two floats together. Adding to integers together
ast2 = grammaire.parse(""" main(y){

        x = 4.3;
        y = 2.5;
        z = x + y;
        print(z)
        x = 4;
        y = 2;
        z = x + y;
        print(z)
 return (y);
 }
""")


-Using a while loop and modifying the argument as an integer and as a float
ast3 = grammaire.parse(""" main(y){

        x = 5;
        y = 2.5;
        while(x){
            x = x - 1;
            print(x)
            y = y - 0.5;
        }
        print(x)
        print(y)
        x = 0.5;
        y = 2.5;
        while(x){
            x = x - 0.5;
            y = y + 0.5;
        }
        print(x)
        print(y)
 return (y);
 }


-Using an if statement, changing the type of the argument in the statement
ast4 = grammaire.parse(""" main(y){

        x = 5;
        if(x){
           x = 0.4;
        }
        print(x)
       x = 6.4;
       if(x){
           x = 4;
       }
       print(x)
 return (y);
 }


=======
# Compilation : Quaternions

compiloQuat.py

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
