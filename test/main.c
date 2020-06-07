#include <string.h>
#include <stdio.h>
#include "objects/header.h"
#include "types.h"
#include "stdbool.h"

int main()
{
  PetriNet_Init();
  while(true);
}

bool state = false;

a_t A_body(void)
{
  a_t ret;
  ret.b.go = state;
  ret.c.id = 37;
  printf("\nA here\n");
  state = !state;
  return ret;
}

void B_body(b_t in_data)
{
  printf("A.b.go is %d\n", in_data.go);
}

void C_body(c_t in_data)
{
  printf("A.c.id is %d\n", in_data.id);
}

void D_body(void)
{
  printf("D here\n");
}

