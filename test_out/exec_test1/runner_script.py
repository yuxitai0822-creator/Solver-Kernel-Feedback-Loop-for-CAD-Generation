import os
import sys
import traceback
import json

try:
    
import os, cadquery as cq
result = cq.Workplane('XY').rect(80, 50).extrude(20)
cq.exporters.export(result, os.environ['OUT_STEP_PATH'])

    # After the user script runs, it must have written a STEP to the
    # env-supplied path.  Otherwise mark the run as failed.
    out_path = os.environ.get("OUT_STEP_PATH", "")
    if out_path and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(json.dumps({"status": "ok", "out_step": out_path}))
    else:
        print(json.dumps({"status": "no_step_written", "out_step": out_path}))
except Exception as e:
    print(json.dumps({"status": "exception",
                       "error": str(e),
                       "traceback": traceback.format_exc()[-500:]}))
