#include <stdio.h>

extern int func();

int main()
{
    printf("%d", func());
    return 0;
}
