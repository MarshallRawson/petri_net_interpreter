#pragma once
#include <stdint.h>

class c_t
{
  public:
    u_int32_t id;
};

class b_t
{
  public:
    bool go;
    char str[17];
};

class a_t
{
  public:
    b_t b;
    c_t c;
};


