# Many-to-Many Thread Mapping Model

## Overview
In Modern Operating Systems, threads are the fundamental unit of execution. The **Many-to-Many (M:N)** model is a hybrid threading architecture that aims to provide the best of both worlds: the efficiency of user-level threads and the parallelism of kernel-level threads.

## Comparison of Threading Models

| Model | Description | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Many-to-One (M:1)** | Many user threads mapped to 1 kernel thread. | Very fast context switching; no kernel involvement. | No true parallelism; one blocking call stalls everyone. |
| **One-to-One (1:1)** | Each user thread maps to exactly 1 kernel thread. | True parallelism; blocking one thread doesn't affect others. | High overhead; context switching requires kernel mode transitions. |
| **Many-to-Many (M:N)** | M user threads multiplexed onto N kernel threads ($M \ge N$). | Efficient resource use; supports parallelism; handles blocking calls well. | Most complex to implement; requires a two-level scheduler. |

## Key Components in M:N Model

### 1. User-Level Threads (ULTs)
These are managed by a thread library in user space. The kernel is unaware of these threads. Switching between ULTs is extremely fast because it doesn't require a system call or a mode switch (User -> Kernel).

### 2. Kernel-Level Threads (KLTs)
Also known as **Lightweight Processes (LWPs)** in some systems (like Solaris). These are the entities the OS kernel actually schedules onto physical CPU cores.

### 3. The Scheduler
The Many-to-Many model requires a **Two-Level Scheduler**:
1. **User-Space Scheduler**: Decides which ULT should run on an available KLT/LWP.
2. **Kernel Scheduler**: Decides which KLT should run on a physical CPU core.

## The Advantage of M:N in This Simulator
The primary advantage demonstrated in this simulator is how the model handles **I/O blocking**.
- If a ULT performs a synchronous I/O operation, the underlying KLT will block.
- In a Many-to-One model, this would stall all other ULTs.
- In the Many-to-Many model, the kernel can notify the user-level scheduler (via **Scheduler Activations**) or the scheduler can detect the blocked state and assign other ready ULTs to different, available KLTs.

## Performance Metrics
- **Throughput**: Number of ULTs finished per clock tick.
- **Context Switch Overhead**: Even though user-level switches are fast, they still consume time. This simulator models a small penalty for every switch.
- **CPU Utilization**: Percentage of time KLTs were busy executing ULT work.

## References
1. Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating System Concepts*.
2. Tanenbaum, A. S., & Bos, H. (2014). *Modern Operating Systems*.
