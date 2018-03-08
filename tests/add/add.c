#include "stdio.h"

int toDigit(char a) {
  return a - '0';
}

int main(int argv, char ** args) {
  if (argv != 3) {
    printf("usage: add.c [a] [b]\n");
    return 2;
  } else {
    printf("%i\n", toDigit(*args[1]) + toDigit(*args[2]));
    return 0;
  }
}
