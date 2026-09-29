"""plan2kqp.core.dispatch — KQP instance + STEP → KQP result."""
from plan2kqp.core.dispatch.dispatcher import dispatch_query
from plan2kqp.core.dispatch.step_loader import load_step

__all__ = ["dispatch_query", "load_step"]