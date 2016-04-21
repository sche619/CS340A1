# A1 for COMPSCI340/SOFTENG370 2015
# Prepared by Robert Sheehan
# Modified by Shunying Chen
# UPI: sche619

# You are not allowed to use any sleep calls.

from threading import Lock, Event
from process import State


class Dispatcher():
    """The dispatcher."""

    MAX_PROCESSES = 8

    def __init__(self):
        """Construct the dispatcher."""
        self.run_stack = []
        self.wait_stack = []
        self.event2 = Event()

    def set_io_sys(self, io_sys):
        """Set the io subsystem."""
        self.io_sys = io_sys

    def add_process(self, process):
        """Add and start the process."""
        self.pause_system()        
        self.io_sys.allocate_window_to_process(process,len(self.run_stack))
        self.run_stack.append(process)
        process.start()

    def dispatch_next_process(self):
        """Dispatch the process at the top of the stack."""
        top_stack = self.run_stack[-1]
        top_stack.start()

    def to_top(self, process):
        """Move the process to the top of the stack."""
        self.pause_system()
        self.run_stack.append(self.run_stack.pop(self.run_stack.index(process)))
        for i in range(len(self.run_stack)):
            self.io_sys.move_process(self.run_stack[i],i)
        for i in range(len(self.run_stack)):
            self.io_sys.move_process(self.run_stack[i],i)
        self.resume_system()

    def pause_system(self):
        """Pause the currently running process.
        As long as the dispatcher doesn't dispatch another process this
        effectively pauses the system.
        """
        if self.run_stack:
           self.run_stack[-1].event.clear()

    def resume_system(self):
        """Resume running the system."""
        if self.run_stack:
           self.run_stack[-1].event.set()

    def wait_until_finished(self):
        """Hang around until all runnable processes are finished."""
        if self.run_stack == []:
           return
        else:
           self.event2.wait()
           self.event2.clear()  

    def proc_finished(self, process):
        """Receive notification that "proc" has finished.
        Only called from running processes.
        """
        self.io_sys.remove_window_from_process(process)
        self.run_stack.pop(self.run_stack.index(process))
        if self.run_stack:
           self.resume_system()
        else:
           self.event2.set()

    def proc_waiting(self, process):
        """Receive notification that process is waiting for input."""        
        self.pause_system()
        self.run_stack.remove(process)
        self.wait_stack.append(process)
        process.state = State.waiting
        self.io_sys.move_process(process,self.wait_stack.index(process))
        self.resume_system()

    def proc_resuming(self,process):
        self.pause_system()
        #self.wait_stack.remove(process)
        self.run_stack.append(process)
        process.state = State.runnable
        self.io_sys.move_process(process,self.run_stack.index(process))

    def kill_process(self,process):
        self.pause_system()
        process.state = State.killed
        if process in self.run_stack:
           self.run_stack.remove(process)
        elif process in self.wait_stack:
           self.wait_stack.remove(process)
        self.io_sys.remove_window_from_process(process)

        for i in range(len(self.run_stack)):
            self.io_sys.move_process(self.run_stack[i],i)
        for i in range(len(self.run_stack)):
            self.io_sys.move_process(self.run_stack[i],i)

        #for i in range(len(self.wait_stack)):
            #self.io_sys.move_process(self.wait_stack[i],i)
        #for i in range(len(self.wait_stack)):
            #self.io_sys.move_process(self.wait_stack[i],i)
        self.resume_system()
        
    def process_with_id(self, id):
        """Return the process with the id."""
        for p in self.run_stack:
           if p.id == id:
              return p
        for p in self.wait_stack:
           if p.id == id:
              return p
        return None

