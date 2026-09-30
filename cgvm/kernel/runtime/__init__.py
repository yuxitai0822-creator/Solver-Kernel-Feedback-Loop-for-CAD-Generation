"""cgvm.kernel.runtime — KQP dispatch + STEP loader (off-line)."""
from cgvm.kernel.runtime.dispatcher import dispatch_query
from cgvm.kernel.runtime.step_loader import load_step

__all__ = ["dispatch_query", "load_step"]