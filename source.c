typedef struct testStruct{
    a;
    b;
};

typedef struct tastaStrict{
    x;
    y;
};

main(){
    s = testStruct();
    s.a = 1;
    x = s.a + 2;
    s.b = tastaStrict();
    s.b.x = 1.1;
    z = 42;
    print(s.b.x + z);
    return(0);
}