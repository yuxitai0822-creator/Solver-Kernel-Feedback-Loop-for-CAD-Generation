"""_unit_test_parser.py — quick unit-test for the new IR-schema parser."""
import sys, importlib.util as iu
spec = iu.spec_from_file_location('rb', 'experiments/run_benchmark_v0.2.py')
rb = iu.module_from_spec(spec); spec.loader.exec_module(rb)

print('=== parser truth table ===')

# Case 1: full IR object (the right protocol)
ok_ir = '''{
  "schema_version": "cad_ir_v0.1",
  "sample_id": "X",
  "unit": "mm",
  "coordinate_system": {"up_axis":"z","front_axis":"y","right_axis":"x"},
  "operations": [
    {"op_id":"op_001","op_type":"sketch_rectangle","plane":"XY",
     "params":{"width":19.0,"height":19.0,"center":[0,0]}},
    {"op_id":"op_002","op_type":"extrude","input":"op_001",
     "params":{"distance":100,"extent_type":"one_side","operation":"new_body","direction":"+normal"}}
  ]
}'''
a, p, s = rb._parse_agent_response(ok_ir)
n = len(p.get("operations", [])) if isinstance(p, dict) else 0
print(f'full IR        -> action={a}, parse_status={s}, ops={n}')

# Case 2: NO_CHANGE
a, p, s = rb._parse_agent_response('NO_CHANGE')
print(f'NO_CHANGE      -> action={a}, parse_status={s}')

# Case 3: legacy operation list — MUST be rejected
legacy = '{"action":"repair","repair_operations":[{"op":"MODIFY","target":"x"}]}'
a, p, s = rb._parse_agent_response(legacy)
reason = p.get("reason") if isinstance(p, dict) else p
print(f'legacy op-list -> action={a}, parse_status={s}')
print(f'                 reason: {reason}')

# Case 4: missing schema_version
no_ver = '{"operations":[{}]}'
a, p, s = rb._parse_agent_response(no_ver)
reason = p.get("reason") if isinstance(p, dict) else p
print(f'no version     -> action={a}, parse_status={s}, reason={reason[:80]}')

# Case 5: empty operations
empty_ops = '{"schema_version":"cad_ir_v0.1","sample_id":"X","unit":"mm","operations":[]}'
a, p, s = rb._parse_agent_response(empty_ops)
reason = p.get("reason") if isinstance(p, dict) else p
print(f'empty ops      -> action={a}, parse_status={s}, reason={reason[:80]}')

# Case 6: wrapped in ```json ... ```
wrapped = '```json\n{"schema_version":"cad_ir_v0.1","sample_id":"X","unit":"mm","operations":[{"op_id":"op_001","op_type":"sketch_rectangle"}]}\n```'
a, p, s = rb._parse_agent_response(wrapped)
print(f'wrapped fence  -> action={a}, parse_status={s}')

# Case 7: random prose
prose = "I think the best fix is to use a wider extrude."
a, p, s = rb._parse_agent_response(prose)
reason = p.get("reason") if isinstance(p, dict) else p
print(f'random prose   -> action={a}, parse_status={s}, reason={reason[:80]}')
