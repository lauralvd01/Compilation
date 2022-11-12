# Compilation

Compilator that implements Dynamic Typing.
you can freely change type between integers and floats.
It is made to be adaptable to other type such as quaternions.
 
Limits of the compilator :
-initial arguments have to be integers
-it is not possible to make binary operation between an integer and a float
-There are some problems with the while statement when the argument is a float
-There are some problems with the if statement if the argument was changed in a while statement before


Note : 


 possibilities :
 All those possibilities are on the Dynamic Typing compilator

# changing type between int and float
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

 # Adding two floats together. Adding to integers together
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


# Using a while loop and modifying the argument as an integer and as a float
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


# Using an if statement, changing the type of the argument in the statement
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