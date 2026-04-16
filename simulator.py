import random
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional

class ThreadState(Enum):
    READY = "Ready"
    RUNNING = "Running"
    BLOCKED = "Blocked"
    FINISHED = "Finished"

class TaskType(Enum):
    CPU_BOUND = "CPU-Bound"
    IO_BOUND = "IO-Bound"

@dataclass
class UserThread:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    task_type: TaskType = TaskType.CPU_BOUND
    total_work: int = 100
    remaining_work: int = 100
    state: ThreadState = ThreadState.READY
    wait_time: int = 0
    execution_time: int = 0
    blocked_until: int = 0
    assigned_klt: Optional[str] = None

@dataclass
class KernelThread:
    id: str
    name: str
    current_ult: Optional[str] = None
    utilization_ticks: int = 0
    context_switch_cooldown: int = 0

class ManyToManySimulator:
    def __init__(self, m_ults: int, n_klts: int, io_ratio: float = 0.3):
        self.m_ults_count = m_ults
        self.n_klts_count = n_klts
        self.io_ratio = io_ratio
        
        self.ults: Dict[str, UserThread] = {}
        self.klts: Dict[str, KernelThread] = {}
        self.ready_queue: List[str] = []
        self.tick = 0
        
        # Performance Metrics
        self.total_context_switches = 0
        self.completed_threads = 0
        
        self._initialize()

    def _initialize(self):
        for i in range(self.m_ults_count):
            task_type = TaskType.IO_BOUND if random.random() < self.io_ratio else TaskType.CPU_BOUND
            work = random.randint(50, 150)
            ut = UserThread(name=f"ULT-{i+1}", task_type=task_type, total_work=work, remaining_work=work)
            self.ults[ut.id] = ut
            self.ready_queue.append(ut.id)
            
        for i in range(self.n_klts_count):
            kt = KernelThread(id=f"KLT-{i+1}", name=f"Kernel-Thread-{i+1}")
            self.klts[kt.id] = kt

    def step(self):
        """Simulate one clock tick"""
        self.tick += 1
        
        # 1. Update blocked threads
        for ut in self.ults.values():
            if ut.state == ThreadState.BLOCKED:
                if self.tick >= ut.blocked_until:
                    ut.state = ThreadState.READY
                    self.ready_queue.append(ut.id)
            elif ut.state == ThreadState.READY:
                ut.wait_time += 1

        # 2. Process Kernel Threads (LWPs)
        for kt in self.klts.values():
            # If KLT is in context switch cooldown, decrement and skip
            if kt.context_switch_cooldown > 0:
                kt.context_switch_cooldown -= 1
                continue

            # If KLT has no ULT, try to pick one from ready queue
            if kt.current_ult is None:
                if self.ready_queue:
                    next_ult_id = self.ready_queue.pop(0)
                    kt.current_ult = next_ult_id
                    ut = self.ults[next_ult_id]
                    ut.state = ThreadState.RUNNING
                    ut.assigned_klt = kt.id
                    kt.context_switch_cooldown = 1 # Penalty
                    self.total_context_switches += 1
                continue

            # Execute the current ULT
            ut = self.ults[kt.current_ult]
            kt.utilization_ticks += 1
            ut.execution_time += 1
            ut.remaining_work -= 1
            
            # Check for completion
            if ut.remaining_work <= 0:
                ut.state = ThreadState.FINISHED
                ut.assigned_klt = None
                kt.current_ult = None
                self.completed_threads += 1
                continue

            # Simulate IO Blocking for IO-bound tasks
            if ut.task_type == TaskType.IO_BOUND and random.random() < 0.05:
                ut.state = ThreadState.BLOCKED
                ut.blocked_until = self.tick + random.randint(5, 15)
                ut.assigned_klt = None
                kt.current_ult = None
                continue

            # Simulate preemption/time-slicing (optional, let's keep it simple for now)
            # If we wanted preemption, we'd move ut back to ready_queue here.

    def is_finished(self):
        return all(ut.state == ThreadState.FINISHED for ut in self.ults.values())

    def get_metrics(self):
        if self.tick == 0: return {}
        
        total_wait = sum(ut.wait_time for ut in self.ults.values())
        avg_wait = total_wait / self.m_ults_count
        
        avg_cpu_util = (sum(kt.utilization_ticks for kt in self.klts.values()) / (self.tick * self.n_klts_count)) * 100
        
        return {
            "Tick": self.tick,
            "Completed": self.completed_threads,
            "Context Switches": self.total_context_switches,
            "Avg Wait Time": round(avg_wait, 2),
            "CPU Utilization (%)": round(avg_cpu_util, 2),
            "Throughput": round(self.completed_threads / self.tick, 4)
        }
