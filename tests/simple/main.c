#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <signal.h>

#include "objects/header.h"
#include "types.h"


void sigint_handler(int dummy)
{
  PetriNet_Close();
  exit(0);
}

int main()
{
  signal(SIGINT, sigint_handler);
  PetriNet_Init();
  while(true);
}

bool state = false;
uint32_t count = 0;


a_t A_body(void)
{
  a_t ret;
  ret.b.go = state;
  ret.c.id = count++;
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

