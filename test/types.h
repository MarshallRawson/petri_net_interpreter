#include <stdint.h>

#ifndef __TYPES_H__
#define __TYPES_H__


typedef struct c
{
  uint32_t id;
} c_t;

typedef struct b
{
  bool go;
  char str[17];
} b_t;

typedef struct a
{
  b_t b;
  c_t c;
} a_t;

#endif
