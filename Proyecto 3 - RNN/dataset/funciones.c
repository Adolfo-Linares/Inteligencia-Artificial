// Dataset personal para entrenamiento RNN
// Estilo: funciones simples, nombres en español y comentarios faciles

#include <stdio.h>

// Funcion 1: aqui sumo dos numeros
// Nombre: sumar
// Entrada esperada: int sumar
// Operacion: numero1 mas numero2
int sumar(int numero1,int numero2){

    int resultado=numero1+numero2;

    return resultado;
}

// Funcion 2: aqui resto dos numeros
// Nombre: restar
// Entrada esperada: int restar
// Operacion: numero1 menos numero2
int restar(int numero1,int numero2){

    int resultado=numero1-numero2;

    return resultado;
}

// Funcion 3: aqui multiplico dos numeros
// Nombre: multiplicar
// Entrada esperada: int multiplicar
// Operacion: numero1 por numero2
int multiplicar(int numero1,int numero2){

    int resultado=numero1*numero2;

    return resultado;
}

// Funcion 4: aqui divido dos numeros
// Nombre: dividir
// Entrada esperada: float dividir
// Operacion: numero1 entre numero2
float dividir(float numero1,float numero2){

    if(numero2==0){
        return 0;
    }

    float resultado=numero1/numero2;

    return resultado;
}

// Funcion 5: aqui saco el residuo
// Nombre: residuo
// Entrada esperada: int residuo
// Operacion: numero1 modulo numero2
int residuo(int numero1,int numero2){

    int resultado=numero1%numero2;

    return resultado;
}

// Funcion 6: aqui saco promedio de dos numeros
// Nombre: promedioDos
// Entrada esperada: float promedioDos
// Operacion: numero1 mas numero2 entre dos
float promedioDos(float numero1,float numero2){

    float resultado=(numero1+numero2)/2;

    return resultado;
}

// Funcion 7: aqui saco promedio de tres numeros
// Nombre: promedioTres
// Entrada esperada: float promedioTres
// Operacion: numero1 mas numero2 mas numero3 entre tres
float promedioTres(float numero1,float numero2,float numero3){

    float resultado=(numero1+numero2+numero3)/3;

    return resultado;
}

// Funcion 8: aqui saco el numero mayor
// Nombre: mayor
// Entrada esperada: int mayor
// Operacion: comparar numero1 y numero2
int mayor(int numero1,int numero2){

    int resultado=numero2;

    if(numero1>numero2){
        resultado=numero1;
    }

    return resultado;
}

// Funcion 9: aqui saco el numero menor
// Nombre: menor
// Entrada esperada: int menor
// Operacion: comparar numero1 y numero2
int menor(int numero1,int numero2){

    int resultado=numero2;

    if(numero1<numero2){
        resultado=numero1;
    }

    return resultado;
}

// Funcion 10: aqui reviso si dos numeros son iguales
// Nombre: sonIguales
// Entrada esperada: int sonIguales
// Operacion: comparar igualdad
int sonIguales(int numero1,int numero2){

    int resultado=0;

    if(numero1==numero2){
        resultado=1;
    }

    return resultado;
}

// Funcion 11: aqui reviso si un numero es par
// Nombre: esPar
// Entrada esperada: int esPar
// Operacion: numero1 modulo dos igual cero
int esPar(int numero1){

    int resultado=0;

    if(numero1%2==0){
        resultado=1;
    }

    return resultado;
}

// Funcion 12: aqui reviso si un numero es impar
// Nombre: esImpar
// Entrada esperada: int esImpar
// Operacion: numero1 modulo dos diferente cero
int esImpar(int numero1){

    int resultado=0;

    if(numero1%2!=0){
        resultado=1;
    }

    return resultado;
}

// Funcion 13: aqui reviso si un numero es positivo
// Nombre: esPositivo
// Entrada esperada: int esPositivo
// Operacion: numero1 mayor que cero
int esPositivo(int numero1){

    int resultado=0;

    if(numero1>0){
        resultado=1;
    }

    return resultado;
}

// Funcion 14: aqui reviso si un numero es negativo
// Nombre: esNegativo
// Entrada esperada: int esNegativo
// Operacion: numero1 menor que cero
int esNegativo(int numero1){

    int resultado=0;

    if(numero1<0){
        resultado=1;
    }

    return resultado;
}

// Funcion 15: aqui saco valor absoluto
// Nombre: valorAbsoluto
// Entrada esperada: int valorAbsoluto
// Operacion: convertir negativo a positivo
int valorAbsoluto(int numero1){

    int resultado=numero1;

    if(numero1<0){
        resultado=numero1*-1;
    }

    return resultado;
}

// Funcion 16: aqui invierto el signo
// Nombre: invertirSigno
// Entrada esperada: int invertirSigno
// Operacion: numero1 por menos uno
int invertirSigno(int numero1){

    int resultado=numero1*-1;

    return resultado;
}

// Funcion 17: aqui aumento uno
// Nombre: aumentarUno
// Entrada esperada: int aumentarUno
// Operacion: numero1 mas uno
int aumentarUno(int numero1){

    int resultado=numero1+1;

    return resultado;
}

// Funcion 18: aqui disminuyo uno
// Nombre: disminuirUno
// Entrada esperada: int disminuirUno
// Operacion: numero1 menos uno
int disminuirUno(int numero1){

    int resultado=numero1-1;

    return resultado;
}

// Funcion 19: aqui calculo porcentaje
// Nombre: calcularPorcentaje
// Entrada esperada: int calcularPorcentaje
// Operacion: numero1 por numero2 entre cien
int calcularPorcentaje(int numero1,int numero2){

    int resultado=(numero1*numero2)/100;

    return resultado;
}

// Funcion 20: aqui calculo descuento
// Nombre: calcularDescuento
// Entrada esperada: float calcularDescuento
// Operacion: precio menos descuento
float calcularDescuento(float precio,float descuento){

    float resultado=precio-(precio*descuento/100);

    return resultado;
}

// Funcion 21: aqui calculo aumento
// Nombre: calcularAumento
// Entrada esperada: float calcularAumento
// Operacion: precio mas aumento
float calcularAumento(float precio,float aumento){

    float resultado=precio+(precio*aumento/100);

    return resultado;
}

// Funcion 22: aqui saco area de cuadrado
// Nombre: areaCuadrado
// Entrada esperada: float areaCuadrado
// Operacion: lado por lado
float areaCuadrado(float lado){

    float resultado=lado*lado;

    return resultado;
}

// Funcion 23: aqui saco area de rectangulo
// Nombre: areaRectangulo
// Entrada esperada: float areaRectangulo
// Operacion: base por altura
float areaRectangulo(float base,float altura){

    float resultado=base*altura;

    return resultado;
}

// Funcion 24: aqui saco area de triangulo
// Nombre: areaTriangulo
// Entrada esperada: float areaTriangulo
// Operacion: base por altura entre dos
float areaTriangulo(float base,float altura){

    float resultado=(base*altura)/2;

    return resultado;
}

// Funcion 25: aqui saco perimetro de cuadrado
// Nombre: perimetroCuadrado
// Entrada esperada: float perimetroCuadrado
// Operacion: lado por cuatro
float perimetroCuadrado(float lado){

    float resultado=lado*4;

    return resultado;
}

// Funcion 26: aqui saco perimetro de rectangulo
// Nombre: perimetroRectangulo
// Entrada esperada: float perimetroRectangulo
// Operacion: base doble mas altura doble
float perimetroRectangulo(float base,float altura){

    float resultado=(base*2)+(altura*2);

    return resultado;
}

// Funcion 27: aqui convierto horas a minutos
// Nombre: horasAMinutos
// Entrada esperada: int horasAMinutos
// Operacion: horas por sesenta
int horasAMinutos(int horas){

    int resultado=horas*60;

    return resultado;
}

// Funcion 28: aqui convierto minutos a segundos
// Nombre: minutosASegundos
// Entrada esperada: int minutosASegundos
// Operacion: minutos por sesenta
int minutosASegundos(int minutos){

    int resultado=minutos*60;

    return resultado;
}

// Funcion 29: aqui convierto dias a horas
// Nombre: diasAHoras
// Entrada esperada: int diasAHoras
// Operacion: dias por veinticuatro
int diasAHoras(int dias){

    int resultado=dias*24;

    return resultado;
}

// Funcion 30: aqui convierto semanas a dias
// Nombre: semanasADias
// Entrada esperada: int semanasADias
// Operacion: semanas por siete
int semanasADias(int semanas){

    int resultado=semanas*7;

    return resultado;
}

// Funcion 31: aqui convierto metros a centimetros
// Nombre: metrosACentimetros
// Entrada esperada: int metrosACentimetros
// Operacion: metros por cien
int metrosACentimetros(int metros){

    int resultado=metros*100;

    return resultado;
}

// Funcion 32: aqui convierto kilometros a metros
// Nombre: kilometrosAMetros
// Entrada esperada: int kilometrosAMetros
// Operacion: kilometros por mil
int kilometrosAMetros(int kilometros){

    int resultado=kilometros*1000;

    return resultado;
}

// Funcion 33: aqui reviso si es mayor de edad
// Nombre: esMayorEdad
// Entrada esperada: int esMayorEdad
// Operacion: edad mayor o igual a dieciocho
int esMayorEdad(int edad){

    int resultado=0;

    if(edad>=18){
        resultado=1;
    }

    return resultado;
}

// Funcion 34: aqui reviso si esta aprobado
// Nombre: estaAprobado
// Entrada esperada: int estaAprobado
// Operacion: calificacion mayor o igual a setenta
int estaAprobado(int calificacion){

    int resultado=0;

    if(calificacion>=70){
        resultado=1;
    }

    return resultado;
}

// Funcion 35: aqui reviso si esta reprobado
// Nombre: estaReprobado
// Entrada esperada: int estaReprobado
// Operacion: calificacion menor a setenta
int estaReprobado(int calificacion){

    int resultado=0;

    if(calificacion<70){
        resultado=1;
    }

    return resultado;
}

// Funcion 36: aqui saco calificacion final
// Nombre: calificacionFinal
// Entrada esperada: float calificacionFinal
// Operacion: promedio de tres parciales
float calificacionFinal(float parcial1,float parcial2,float parcial3){

    float resultado=(parcial1+parcial2+parcial3)/3;

    return resultado;
}

// Funcion 37: aqui sumo un arreglo
// Nombre: sumarArreglo
// Entrada esperada: int sumarArreglo
// Operacion: sumar todos los numeros del arreglo
int sumarArreglo(int numeros[],int cantidad){

    int resultado=0;

    for(int i=0;i<cantidad;i++){
        resultado=resultado+numeros[i];
    }

    return resultado;
}

// Funcion 38: aqui saco promedio de arreglo
// Nombre: promedioArreglo
// Entrada esperada: float promedioArreglo
// Operacion: suma del arreglo entre cantidad
float promedioArreglo(int numeros[],int cantidad){

    int suma=0;

    for(int i=0;i<cantidad;i++){
        suma=suma+numeros[i];
    }

    float resultado=suma/cantidad;

    return resultado;
}

// Funcion 39: aqui busco el mayor de arreglo
// Nombre: mayorArreglo
// Entrada esperada: int mayorArreglo
// Operacion: comparar numeros del arreglo
int mayorArreglo(int numeros[],int cantidad){

    int resultado=numeros[0];

    for(int i=0;i<cantidad;i++){

        if(numeros[i]>resultado){
            resultado=numeros[i];
        }

    }

    return resultado;
}

// Funcion 40: aqui busco el menor de arreglo
// Nombre: menorArreglo
// Entrada esperada: int menorArreglo
// Operacion: comparar numeros del arreglo
int menorArreglo(int numeros[],int cantidad){

    int resultado=numeros[0];

    for(int i=0;i<cantidad;i++){

        if(numeros[i]<resultado){
            resultado=numeros[i];
        }

    }

    return resultado;
}

// Funcion 41: aqui busco un numero en arreglo
// Nombre: buscarNumero
// Entrada esperada: int buscarNumero
// Operacion: encontrar posicion del numero buscado
int buscarNumero(int numeros[],int cantidad,int buscado){

    int resultado=-1;

    for(int i=0;i<cantidad;i++){

        if(numeros[i]==buscado){
            resultado=i;
        }

    }

    return resultado;
}

// Funcion 42: aqui cuento pares en arreglo
// Nombre: contarPares
// Entrada esperada: int contarPares
// Operacion: contar numeros pares
int contarPares(int numeros[],int cantidad){

    int resultado=0;

    for(int i=0;i<cantidad;i++){

        if(numeros[i]%2==0){
            resultado=resultado+1;
        }

    }

    return resultado;
}

// Funcion 43: aqui cuento impares en arreglo
// Nombre: contarImpares
// Entrada esperada: int contarImpares
// Operacion: contar numeros impares
int contarImpares(int numeros[],int cantidad){

    int resultado=0;

    for(int i=0;i<cantidad;i++){

        if(numeros[i]%2!=0){
            resultado=resultado+1;
        }

    }

    return resultado;
}

// Funcion 44: aqui cuento positivos en arreglo
// Nombre: contarPositivos
// Entrada esperada: int contarPositivos
// Operacion: contar numeros mayores a cero
int contarPositivos(int numeros[],int cantidad){

    int resultado=0;

    for(int i=0;i<cantidad;i++){

        if(numeros[i]>0){
            resultado=resultado+1;
        }

    }

    return resultado;
}

// Funcion 45: aqui cuento negativos en arreglo
// Nombre: contarNegativos
// Entrada esperada: int contarNegativos
// Operacion: contar numeros menores a cero
int contarNegativos(int numeros[],int cantidad){

    int resultado=0;

    for(int i=0;i<cantidad;i++){

        if(numeros[i]<0){
            resultado=resultado+1;
        }

    }

    return resultado;
}

// Funcion 46: aqui saco factorial
// Nombre: factorial
// Entrada esperada: int factorial
// Operacion: multiplicar desde uno hasta numero1
int factorial(int numero1){

    int resultado=1;

    for(int i=1;i<=numero1;i++){
        resultado=resultado*i;
    }

    return resultado;
}

// Funcion 47: aqui saco potencia
// Nombre: potencia
// Entrada esperada: int potencia
// Operacion: base multiplicada por si misma
int potencia(int base,int exponente){

    int resultado=1;

    for(int i=1;i<=exponente;i++){
        resultado=resultado*base;
    }

    return resultado;
}

// Funcion 48: aqui reviso si es primo
// Nombre: esPrimo
// Entrada esperada: int esPrimo
// Operacion: contar divisores del numero
int esPrimo(int numero1){

    int divisores=0;

    for(int i=1;i<=numero1;i++){

        if(numero1%i==0){
            divisores=divisores+1;
        }

    }

    int resultado=0;

    if(divisores==2){
        resultado=1;
    }

    return resultado;
}

// Funcion 49: aqui cuento letras de texto
// Nombre: contarLetras
// Entrada esperada: int contarLetras
// Operacion: recorrer texto hasta fin
int contarLetras(char texto[]){

    int resultado=0;

    while(texto[resultado]!='\0'){
        resultado=resultado+1;
    }

    return resultado;
}

// Funcion 50: aqui saco primera letra
// Nombre: primeraLetra
// Entrada esperada: char primeraLetra
// Operacion: tomar posicion cero del texto
char primeraLetra(char texto[]){

    char resultado=texto[0];

    return resultado;
}

// Funcion 51: aqui saco ultima letra
// Nombre: ultimaLetra
// Entrada esperada: char ultimaLetra
// Operacion: buscar ultima posicion del texto
char ultimaLetra(char texto[]){

    int posicion=0;

    while(texto[posicion]!='\0'){
        posicion=posicion+1;
    }

    char resultado=texto[posicion-1];

    return resultado;
}

// Funcion 52: aqui cuento letra a
// Nombre: contarLetraA
// Entrada esperada: int contarLetraA
// Operacion: contar caracteres iguales a a
int contarLetraA(char texto[]){

    int resultado=0;

    for(int i=0;texto[i]!='\0';i++){

        if(texto[i]=='a'){
            resultado=resultado+1;
        }

    }

    return resultado;
}

// Funcion 53: aqui cuento vocales
// Nombre: contarVocales
// Entrada esperada: int contarVocales
// Operacion: contar letras a e i o u
int contarVocales(char texto[]){

    int resultado=0;

    for(int i=0;texto[i]!='\0';i++){

        if(texto[i]=='a'){
            resultado=resultado+1;
        }

        if(texto[i]=='e'){
            resultado=resultado+1;
        }

        if(texto[i]=='i'){
            resultado=resultado+1;
        }

        if(texto[i]=='o'){
            resultado=resultado+1;
        }

        if(texto[i]=='u'){
            resultado=resultado+1;
        }

    }

    return resultado;
}

// Funcion 54: aqui reviso si empieza con a
// Nombre: empiezaConA
// Entrada esperada: int empiezaConA
// Operacion: revisar primera letra
int empiezaConA(char texto[]){

    int resultado=0;

    if(texto[0]=='a'){
        resultado=1;
    }

    return resultado;
}

// Funcion 55: aqui calculo precio con iva
// Nombre: precioConIva
// Entrada esperada: float precioConIva
// Operacion: precio mas dieciseis por ciento
float precioConIva(float precio){

    float resultado=precio+(precio*0.16);

    return resultado;
}

// Funcion 56: aqui calculo salario semanal
// Nombre: salarioSemanal
// Entrada esperada: float salarioSemanal
// Operacion: pago por dia por dias
float salarioSemanal(float pagoDia,int dias){

    float resultado=pagoDia*dias;

    return resultado;
}

// Funcion 57: aqui calculo distancia
// Nombre: calcularDistancia
// Entrada esperada: float calcularDistancia
// Operacion: velocidad por tiempo
float calcularDistancia(float velocidad,float tiempo){

    float resultado=velocidad*tiempo;

    return resultado;
}

// Funcion 58: aqui calculo velocidad
// Nombre: calcularVelocidad
// Entrada esperada: float calcularVelocidad
// Operacion: distancia entre tiempo
float calcularVelocidad(float distancia,float tiempo){

    if(tiempo==0){
        return 0;
    }

    float resultado=distancia/tiempo;

    return resultado;
}

// Funcion 59: aqui calculo energia simple
// Nombre: calcularEnergia
// Entrada esperada: float calcularEnergia
// Operacion: masa por velocidad   por velocidad
float calcularEnergia(float masa,float velocidad){

    float resultado=masa*velocidad*velocidad;

    return resultado;
}

// Funcion 60: aqui calculo promedio general
// Nombre: promedioGeneral
// Entrada esperada: float promedioGeneral
// Operacion: promedio de cuatro numeros
float promedioGeneral(float numero1,float numero2,float numero3,float numero4){

    float resultado=(numero1+numero2+numero3+numero4)/4;

    return resultado;
}