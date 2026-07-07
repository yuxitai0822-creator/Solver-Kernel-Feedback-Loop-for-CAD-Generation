"""sampler.py — Choose 3 perturbations per clean sample.

Strategy (intent-stratified + importance-weighted + eligibility-constrained):

  Perturbation #1 — universal bbox perturbation:
    * For non-symmetric samples: E2_extrude_depth (scale=1.5)
        - target_intent = bbox_size (extrude w-axis)
    * For symmetric samples: E2_extrude_depth (since symmetric extent changes bbox_w
      interpretation, we still use scale_extrude; alternatively use E5 to test
      symmetric_about_plane intent)
        - on the first sample that is 'symmetric', switch slot #1 to E5_extent_type
          so we test the relation intent

  Perturbation #2 — profile-specific (samples the dominant profile-class intent):
    * annulus       -> E3_radius_up (test cylinder_radius)
    * circle        -> E3_radius_up
    * stadium       -> E3_radius_up (target=arc)
    * rectangular_frame -> E4_void_remove_one (test through_void_count)
    * rectangle     -> E1_envelope_u (test bbox_size)
    * arbitrary_closed / polygon_with_fillets -> E1_envelope_u

  Perturbation #3 — intent-balancing (covers low-frequency intents):
    * If profile is 'circle' or 'annulus' AND n_inner > 0 -> E4_void_remove_one
    * Else if profile is annulus   -> E6_inner_gt_outer (test is_solid/occt_valid)
    * Else if n_inner > 0        -> E4_void_remove_one
    * Else if symmetric         -> use slot #3 here only; if first slot was E2 then slot #3 is E5
    * Else                       -> E6_zero_extrude (test is_solid/occt_valid)

  This guarantees:
    - Every sample gets at least one E2-style bbox_w perturbation  (46 cases)
    - Most samples get a profile-specific perturbation  (radius OR void OR bbox_u)
    - ~8-10 samples get an E6 validity-perturbation
    - ~8-10 samples get an E4 void perturbation
    - 1 sample (the symmetric one) gets an E5 extent_type perturbation
"""
from __future__ import annotations

from typing import Any

from operators import detect_profile_type, detect_extent_type

# Important: The order is significant: #1 must be on EVERY clean sample.
# #2 must be profile-specific.  #3 should cover relation/secondary intent.


def sample_perturbations_for(history: dict, is_symmetric_sample: bool = False,
                              symmetric_seen: list[bool] | None = None
                              ) -> list[dict[str, Any]]:
    """Return a list of 3 perturbation specs.

    Each spec is a dict: {type: str, params: dict, intent: str, ...}.
    The `intent` here is the *target* intent that the operator primarily targets,
    not the KQP emitted intent; we'll resolve to query_id(s) at sampler-bound time.
    """
    ptype = detect_profile_type(history)
    extent = detect_extent_type(history)

    specs: list[dict] = []

    # ---- Slot 1: universal bbox perturbation ----
    # Default: scale extrude depth (w-axis).  target = bbox_size.
    # If this sample IS the symmetric one and we haven't yet covered it via
    # the slot #3 fallback, swap slot #1 to E5.
    use_e5_in_slot1 = is_symmetric_sample and (
        symmetric_seen is None or sum(symmetric_seen) == 0)

    if use_e5_in_slot1:
        specs.append({
            "perturbation_id": 1,
            "operator": "E5_extent_type_change",
            "params": {},
            "target_intent": "symmetric_about_plane",
            "error_category": "E5_extent_type",
            "priority": "relation",
        })
    else:
        specs.append({
            "perturbation_id": 1,
            "operator": "E2_extrude_deep",
            "params": {},
            "target_intent": "bbox_size",
            "error_category": "E2_extrude_depth",
            "priority": "core_dim",
        })

    # ---- Slot 2: profile-specific ----
    if ptype == "annulus":
        specs.append({
            "perturbation_id": 2,
            "operator": "E3_radius_up",
            "params": {},
            "target_intent": "cylinder_radius",
            "error_category": "E3_radius",
            "priority": "core_dim",
        })
    elif ptype == "circle":
        specs.append({
            "perturbation_id": 2,
            "operator": "E3_radius_up",
            "params": {},
            "target_intent": "cylinder_radius",
            "error_category": "E3_radius",
            "priority": "core_dim",
        })
    elif ptype == "stadium":
        specs.append({
            "perturbation_id": 2,
            "operator": "E3_radius_up",
            "params": {},
            "target_intent": "cylinder_radius",
            "error_category": "E3_radius",
            "priority": "core_dim",
        })
    elif ptype == "rectangular_frame":
        specs.append({
            "perturbation_id": 2,
            "operator": "E4_void_remove_one",
            "params": {},
            "target_intent": "through_void_count",
            "error_category": "E4_void",
            "priority": "topology",
        })
    elif ptype == "polygon_with_fillets":
        specs.append({
            "perturbation_id": 2,
            "operator": "E1_envelope_u",
            "params": {},
            "target_intent": "bbox_size",
            "error_category": "E1_envelope_dim",
            "priority": "core_dim",
        })
    else:  # rectangle or arbitrary_closed
        specs.append({
            "perturbation_id": 2,
            "operator": "E1_envelope_u",
            "params": {},
            "target_intent": "bbox_size",
            "error_category": "E1_envelope_dim",
            "priority": "core_dim",
        })

    # ---- Slot 3: intent-balancing ----
    # Goal: cover body_count, is_solid, occt_valid, through_void_count, symmetric
    # preferentially.  We balance two things:
    #   - produce a successfully-constructible negative whose actual step
    #     differs from original (so NDR / TQDR are computable);
    #   - occasionally produce a reconstruct-FAILED negative (E6 validity)
    #     so we also test the is_solid / occt_valid intent path.
    #   The reconstruction-failure rate is the expected cost of E6; the
    #   NDR / TQDR stats already EXCLUDE reconstruction failures.
    n_inner = _count_inner_loops(history)
    if ptype in ("annulus",) and n_inner > 0 and not use_e5_in_slot1:
        # E6_inner_gt_outer: from annulus we test validity intent.
        specs.append({
            "perturbation_id": 3,
            "operator": "E6_inner_gt_outer",
            "params": {},
            "target_intent": "is_solid",
            "error_category": "E6_validity",
            "priority": "health",
        })
    elif ptype == "circle" and not use_e5_in_slot1:
        # For circle samples, add an extra inner hole that wasn't declared.
        specs.append({
            "perturbation_id": 3,
            "operator": "E4_void_add",
            "params": {},
            "target_intent": "through_void_count",
            "error_category": "E4_void",
            "priority": "topology",
        })
    elif n_inner > 0 and not use_e5_in_slot1:
        # frame / polygon → remove an inner loop that was declared.
        specs.append({
            "perturbation_id": 3,
            "operator": "E4_void_remove_one",
            "params": {},
            "target_intent": "through_void_count",
            "error_category": "E4_void",
            "priority": "topology",
        })
    elif use_e5_in_slot1:
        # Slot 1 already used E5 — slot 3 falls back to bbox shrink.
        specs.append({
            "perturbation_id": 3,
            "operator": "E2_extrude_shallow",
            "params": {},
            "target_intent": "bbox_size",
            "error_category": "E2_extrude_depth",
            "priority": "core_dim",
        })
    elif ptype == "rectangle":
        # Plain rectangle without inner loops → avoid E6_zero_extrude (fail).
        # Use E1 envelope_v shrink instead to ensure successful reconstruction.
        specs.append({
            "perturbation_id": 3,
            "operator": "E1_envelope_v_shrink",
            "params": {},
            "target_intent": "bbox_size",
            "error_category": "E1_envelope_dim",
            "priority": "core_dim",
        })
    elif ptype == "stadium":
        specs.append({
            "perturbation_id": 3,
            "operator": "E1_envelope_v_shrink",
            "params": {},
            "target_intent": "bbox_size",
            "error_category": "E1_envelope_dim",
            "priority": "core_dim",
        })
    else:
        # arbitrary_closed or other — use bbox shrink.
        specs.append({
            "perturbation_id": 3,
            "operator": "E1_envelope_v_shrink",
            "params": {},
            "target_intent": "bbox_size",
            "error_category": "E1_envelope_dim",
            "priority": "core_dim",
        })

    return specs


def _count_inner_loops(history: dict) -> int:
    from operators import parse_history
    sketch, _, refs = parse_history(history)
    if sketch is None:
        return 0
    pid = refs.get("consumed_profile_id")
    profile = sketch.get("profiles", {}).get(pid)
    if profile is None:
        return 0
    return sum(1 for l in profile.get("loops", []) if not l.get("is_outer"))


def kqp_query_ids_for_intent(kqp_instance: dict, intent: str,
                                axis: str | None = None) -> list[str]:
    """Find KQP query ids that match an intent (and optionally an axis)."""
    out = []
    for q in kqp_instance.get("queries", []):
        if q.get("intent") != intent:
            continue
        if axis and q.get("axis") and q.get("axis") != axis:
            continue
        out.append(q.get("id"))
    return out


def resolve_expected_queries(spec: dict, kqp_instance: dict) -> list[str]:
    """Map a spec.target_intent to KQP query ids present in this sample's instance."""
    return kqp_query_ids_for_intent(kqp_instance, spec["target_intent"])
