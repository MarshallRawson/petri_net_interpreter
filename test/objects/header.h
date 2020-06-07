#pragma once
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <stdio.h>
#include <semaphore.h>
#include <unistd.h>

#include "../types.h"
// Places:
// A
int A_OUT_IPC;
struct msqid_ds A_OUT_IPC_buf;
void* A_wrapper(void* parg);
a_t A_body(void);

// B
sem_t B_OUT_SEMAPHORE;
sem_t B_IN_DATA_COPY_SEMAPHORE;
void* B_wrapper(void* parg);
void B_body(b_t);

// C
sem_t C_OUT_SEMAPHORE;
sem_t C_IN_DATA_COPY_SEMAPHORE;
void* C_wrapper(void* parg);
void C_body(c_t);

// D
sem_t D_OUT_SEMAPHORE;
void* D_wrapper(void* parg);
void D_body(void);

// Transitions:
sem_t PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE;
// transition_0
void transition_0();

// transition_1
void transition_1();

// transition_3
void transition_3();

// transition_2
void transition_2();

// transition_4
void transition_4();

// Start Thread
void* start_thread();

// Petri Net Init:
void PetriNet_Init();

