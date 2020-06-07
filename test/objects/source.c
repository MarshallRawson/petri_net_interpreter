#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <stdio.h>
#include <semaphore.h>
#include <unistd.h>

#include "header.h"
// Places:
// A

void* A_wrapper(void* parg)
{
struct ret_buf
{
  long type;
  a_t data;
} ret;
ret.type = 1;
ret.data = A_body();
{
if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == msgsnd(A_OUT_IPC, &ret,
sizeof(a_t) + sizeof(long), 0))
{
  perror("A_OUT_IPC sending ret failed\n");
  pthread_exit(NULL);
}
// Get Debug state
char debug_state[28];
int A;
if (-1 == msgctl(A_OUT_IPC, IPC_STAT, &A_OUT_IPC_buf))
{
  perror("A_OUT_IPC getting stats failed\n");
  pthread_exit(NULL);
}
A = A_OUT_IPC_buf.msg_qnum;
int B;
if (-1 == sem_getvalue(&B_OUT_SEMAPHORE, &B))
{
  perror("B_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int C;
if (-1 == sem_getvalue(&C_OUT_SEMAPHORE, &C))
{
  perror("C_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int D;
if (-1 == sem_getvalue(&D_OUT_SEMAPHORE, &D))
{
  perror("D_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
snprintf(debug_state, 28, "A: %d\nB: %d\nC: %d\nD: %d\n\n", A, B, C, D );
printf("%s", debug_state);
if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}
bool called_transition = false;
a_t* A = &ret.data;
if ( A->b.go)
{
  called_transition = true;
  transition_1();
}
if (!A->b.go)
{
  called_transition = true;
  transition_3();
}
if (!called_transition)
{
  perror("A failed to call any transitions and therfore the program is in a blocked state it will not recover from\n");
}
pthread_exit(NULL);
return NULL;
}

// B

void* B_wrapper(void* parg)
{
b_t in_data;
memcpy(&in_data, parg, sizeof(b_t));
if (-1 == sem_post(&B_IN_DATA_COPY_SEMAPHORE))
{
  perror("signaling B_IN_DATA_COPY_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
B_body(in_data);
{
if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_post(&B_OUT_SEMAPHORE))
{
  perror("signaling B_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
// Get Debug state
char debug_state[28];
int A;
if (-1 == msgctl(A_OUT_IPC, IPC_STAT, &A_OUT_IPC_buf))
{
  perror("A_OUT_IPC getting stats failed\n");
  pthread_exit(NULL);
}
A = A_OUT_IPC_buf.msg_qnum;
int B;
if (-1 == sem_getvalue(&B_OUT_SEMAPHORE, &B))
{
  perror("B_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int C;
if (-1 == sem_getvalue(&C_OUT_SEMAPHORE, &C))
{
  perror("C_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int D;
if (-1 == sem_getvalue(&D_OUT_SEMAPHORE, &D))
{
  perror("D_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
snprintf(debug_state, 28, "A: %d\nB: %d\nC: %d\nD: %d\n\n", A, B, C, D );
printf("%s", debug_state);
if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}
bool called_transition = false;
if (true)
{
  called_transition = true;
  transition_2();
}
if (!called_transition)
{
  perror("B failed to call any transitions and therfore the program is in a blocked state it will not recover from\n");
}
pthread_exit(NULL);
return NULL;
}

// C

void* C_wrapper(void* parg)
{
c_t in_data;
memcpy(&in_data, parg, sizeof(c_t));
if (-1 == sem_post(&C_IN_DATA_COPY_SEMAPHORE))
{
  perror("signaling C_IN_DATA_COPY_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
C_body(in_data);
{
if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_post(&C_OUT_SEMAPHORE))
{
  perror("signaling C_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
// Get Debug state
char debug_state[28];
int A;
if (-1 == msgctl(A_OUT_IPC, IPC_STAT, &A_OUT_IPC_buf))
{
  perror("A_OUT_IPC getting stats failed\n");
  pthread_exit(NULL);
}
A = A_OUT_IPC_buf.msg_qnum;
int B;
if (-1 == sem_getvalue(&B_OUT_SEMAPHORE, &B))
{
  perror("B_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int C;
if (-1 == sem_getvalue(&C_OUT_SEMAPHORE, &C))
{
  perror("C_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int D;
if (-1 == sem_getvalue(&D_OUT_SEMAPHORE, &D))
{
  perror("D_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
snprintf(debug_state, 28, "A: %d\nB: %d\nC: %d\nD: %d\n\n", A, B, C, D );
printf("%s", debug_state);
if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}
bool called_transition = false;
if (true)
{
  called_transition = true;
  transition_4();
}
if (true)
{
  called_transition = true;
  transition_2();
}
if (!called_transition)
{
  perror("C failed to call any transitions and therfore the program is in a blocked state it will not recover from\n");
}
pthread_exit(NULL);
return NULL;
}

// D

void* D_wrapper(void* parg)
{
D_body();
{
if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_post(&D_OUT_SEMAPHORE))
{
  perror("signaling D_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
// Get Debug state
char debug_state[28];
int A;
if (-1 == msgctl(A_OUT_IPC, IPC_STAT, &A_OUT_IPC_buf))
{
  perror("A_OUT_IPC getting stats failed\n");
  pthread_exit(NULL);
}
A = A_OUT_IPC_buf.msg_qnum;
int B;
if (-1 == sem_getvalue(&B_OUT_SEMAPHORE, &B))
{
  perror("B_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int C;
if (-1 == sem_getvalue(&C_OUT_SEMAPHORE, &C))
{
  perror("C_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int D;
if (-1 == sem_getvalue(&D_OUT_SEMAPHORE, &D))
{
  perror("D_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
snprintf(debug_state, 28, "A: %d\nB: %d\nC: %d\nD: %d\n\n", A, B, C, D );
printf("%s", debug_state);
if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}
bool called_transition = false;
if (true)
{
  called_transition = true;
  transition_4();
}
if (!called_transition)
{
  perror("D failed to call any transitions and therfore the program is in a blocked state it will not recover from\n");
}
pthread_exit(NULL);
return NULL;
}

// Transitions:
// transition_0
void transition_0()
{
  if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
  if(  true)
  {
    {
pthread_t A_wrapper_pthread;
pthread_create(&A_wrapper_pthread, NULL, &A_wrapper, NULL);
}
  }
  if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}

// transition_1
void transition_1()
{
  if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == msgctl(A_OUT_IPC, IPC_STAT, &A_OUT_IPC_buf))
{
  perror("A_OUT_IPC getting stats failed\n");
  pthread_exit(NULL);
}
bool A_is_ready = (A_OUT_IPC_buf.msg_qnum > 0);
  if((A_is_ready > 0) &&
  true)
  {
    a_t* A;
struct A_struct
{
  long type;
  a_t data;
} A_buf;
if(-1 == msgrcv(A_OUT_IPC, &A_buf,
sizeof(a_t) + sizeof(long), 1,
0))
{
  perror("A_OUT_IPC reciving A failed\n");
  pthread_exit(NULL);
}
A = &(A_buf.data);
    {
pthread_t B_wrapper_pthread;
pthread_create(&B_wrapper_pthread, NULL, &B_wrapper, &A->b);
}
    {
pthread_t C_wrapper_pthread;
pthread_create(&C_wrapper_pthread, NULL, &C_wrapper, &A->c);
}
  }
  if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_wait(&B_IN_DATA_COPY_SEMAPHORE))
{
  perror("waiting on B_IN_DATA_COPY_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_wait(&C_IN_DATA_COPY_SEMAPHORE))
{
  perror("waiting on C_IN_DATA_COPY_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}

// transition_3
void transition_3()
{
  if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == msgctl(A_OUT_IPC, IPC_STAT, &A_OUT_IPC_buf))
{
  perror("A_OUT_IPC getting stats failed\n");
  pthread_exit(NULL);
}
bool A_is_ready = (A_OUT_IPC_buf.msg_qnum > 0);
  if((A_is_ready > 0) &&
  true)
  {
    a_t* A;
struct A_struct
{
  long type;
  a_t data;
} A_buf;
if(-1 == msgrcv(A_OUT_IPC, &A_buf,
sizeof(a_t) + sizeof(long), 1,
0))
{
  perror("A_OUT_IPC reciving A failed\n");
  pthread_exit(NULL);
}
A = &(A_buf.data);
    {
pthread_t C_wrapper_pthread;
pthread_create(&C_wrapper_pthread, NULL, &C_wrapper, &A->c);
}
    {
pthread_t D_wrapper_pthread;
pthread_create(&D_wrapper_pthread, NULL, &D_wrapper, NULL);
}
  }
  if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_wait(&C_IN_DATA_COPY_SEMAPHORE))
{
  perror("waiting on C_IN_DATA_COPY_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}

// transition_2
void transition_2()
{
  if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
int B_is_ready;
if (-1 == sem_getvalue(&B_OUT_SEMAPHORE, &B_is_ready))
{
  perror("B_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int C_is_ready;
if (-1 == sem_getvalue(&C_OUT_SEMAPHORE, &C_is_ready))
{
  perror("C_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
  if((B_is_ready > 0) &&
(C_is_ready > 0) &&
  true)
  {
    if (-1 == sem_wait(&B_OUT_SEMAPHORE))
{
  perror("waiting on B_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
    if (-1 == sem_wait(&C_OUT_SEMAPHORE))
{
  perror("waiting on C_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
    {
pthread_t A_wrapper_pthread;
pthread_create(&A_wrapper_pthread, NULL, &A_wrapper, NULL);
}
  }
  if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}

// transition_4
void transition_4()
{
  if (-1 == sem_wait(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("waiting on PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
int C_is_ready;
if (-1 == sem_getvalue(&C_OUT_SEMAPHORE, &C_is_ready))
{
  perror("C_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
int D_is_ready;
if (-1 == sem_getvalue(&D_OUT_SEMAPHORE, &D_is_ready))
{
  perror("D_OUT_SEMAPHORE semaphore get value failed\n");
  pthread_exit(NULL);
}
  if((C_is_ready > 0) &&
(D_is_ready > 0) &&
  true)
  {
    if (-1 == sem_wait(&C_OUT_SEMAPHORE))
{
  perror("waiting on C_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
    if (-1 == sem_wait(&D_OUT_SEMAPHORE))
{
  perror("waiting on D_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
    {
pthread_t A_wrapper_pthread;
pthread_create(&A_wrapper_pthread, NULL, &A_wrapper, NULL);
}
  }
  if (-1 == sem_post(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE))
{
  perror("signaling PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE failed\n");
  pthread_exit(NULL);
}
}

// Start Thread
void* start_thread()
{
transition_0();
pthread_exit(NULL);
return NULL;
return 0;
}

//Petri Net Init:
void PetriNet_Init()
{
int proj_id = 0;
if (-1 == sem_init(&PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE, 0, 1))
{
  perror("PETRI_TRANSITION_SEMAPHORE_OUT_SEMAPHORE semaphore initialization failed\n");
  pthread_exit(NULL);
}
{
key_t A_OUT_IPC_key = ftok("./objects/source.c", proj_id++);
A_OUT_IPC = msgget(A_OUT_IPC_key, 0600 | IPC_CREAT);
if (A_OUT_IPC == -1)
{
  perror("A_OUT_IPC message queue creation failed\n");
  pthread_exit(NULL);
}
if (-1 == msgctl(A_OUT_IPC, IPC_STAT, &A_OUT_IPC_buf))
{
  perror("A_OUT_IPC getting stats failed\n");
  pthread_exit(NULL);
}
A_OUT_IPC_buf.msg_qbytes = sizeof(a_t) * 32;
if (-1 == msgctl(A_OUT_IPC, IPC_SET, &A_OUT_IPC_buf))
{
  perror("A_OUT_IPC setting stats failed\n");
  pthread_exit(NULL);
}
}
if (-1 == sem_init(&B_OUT_SEMAPHORE, 0, 0))
{
  perror("B_OUT_SEMAPHORE semaphore initialization failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_init(&B_IN_DATA_COPY_SEMAPHORE, 0, 0))
{
  perror("B_IN_DATA_COPY_SEMAPHORE semaphore initialization failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_init(&C_OUT_SEMAPHORE, 0, 0))
{
  perror("C_OUT_SEMAPHORE semaphore initialization failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_init(&C_IN_DATA_COPY_SEMAPHORE, 0, 0))
{
  perror("C_IN_DATA_COPY_SEMAPHORE semaphore initialization failed\n");
  pthread_exit(NULL);
}
if (-1 == sem_init(&D_OUT_SEMAPHORE, 0, 0))
{
  perror("D_OUT_SEMAPHORE semaphore initialization failed\n");
  pthread_exit(NULL);
}
{
pthread_t start_thread_pthread;
pthread_create(&start_thread_pthread, NULL, &start_thread, NULL);
}
}
