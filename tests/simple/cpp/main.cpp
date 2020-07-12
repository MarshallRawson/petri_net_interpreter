#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <signal.h>

#include "objects/header.hpp"
#include "types.h"


void sigint_handler(int dummy)
{
  header::PetriNet_Close();
  exit(0);
}

int main()
{
  signal(SIGINT, sigint_handler);
  header::PetriNet_Init();
  while(true);
}

bool state = false;
u_int32_t count = 0;

a_t header::A::Body(void)
{
  a_t ret;
  ret.b.go = state;
  ret.c.id = count++;
  printf("\nA here\n");
  state = !state;
  return ret;
}

void header::B::Body(b_t in_data)
{
  printf("A.b.go is %d\n", in_data.go);
}

void header::C::Body(c_t in_data)
{
  printf("A.c.id is %d\n", in_data.id);
}

void header::D::Body(void)
{
  printf("D here\n");
}

