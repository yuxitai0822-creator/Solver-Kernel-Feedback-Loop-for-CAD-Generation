# False-Pass / Target-Miss Cases in Task5

Task 5 defines a **false pass** as any negative where the perturbation was
successfully constructed (rec_ok + signature_different) but the KQP either
didn't fail any query (Type A: `all_pass`) or failed queries of a
*different* intent from the perturbation's target (Type B: `targeted_miss`).

## Summary counts

* Total negatives: **138**
* Reconstruction failures (excluded): **6**
* Eligible negatives (rec_ok + sig_diff + at least 1 fail): **132**
* Type A (all_pass): **11**
* Type B (targeted_miss): **25**
* Detected (any fail): **121**
* Targeted (intent match): **107**

## Type A: KQP all-pass (perturbation not detected at all)

| sample_id | negative_id | operator | target_intent | error_category |
|---|---|---|---|---|
| 100243_9fb796fe_0005 | neg_02 | E1_envelope_u | bbox_size | E1_envelope_dim |
| 100243_9fb796fe_0005 | neg_03 | E1_envelope_v_shrink | bbox_size | E1_envelope_dim |
| 100243_9fb796fe_0006 | neg_02 | E1_envelope_u | bbox_size | E1_envelope_dim |
| 100243_9fb796fe_0006 | neg_03 | E1_envelope_v_shrink | bbox_size | E1_envelope_dim |
| 102410_f9877a7b_0012 | neg_01 | E2_extrude_deep | bbox_size | E2_extrude_depth |
| 103481_b27a1cdf_0010 | neg_02 | E1_envelope_u | bbox_size | E1_envelope_dim |
| 103481_b27a1cdf_0010 | neg_03 | E1_envelope_v_shrink | bbox_size | E1_envelope_dim |
| 104283_e5646f96_0001 | neg_02 | E1_envelope_u | bbox_size | E1_envelope_dim |
| 104283_e5646f96_0001 | neg_03 | E1_envelope_v_shrink | bbox_size | E1_envelope_dim |
| 104453_aba0f2d1_0002 | neg_01 | E2_extrude_deep | bbox_size | E2_extrude_depth |
| 104453_aba0f2d1_0006 | neg_01 | E2_extrude_deep | bbox_size | E2_extrude_depth |

## Type B: KQP detected, but target intent did not match

| sample_id | negative_id | operator | target_intent | failed_query_ids | observed_intents |
|---|---|---|---|---|---|
| 102295_86f842dd_0000 | neg_02 | E3_radius_up | cylinder_radius | q_bbox_u,q_bbox_v,q_occt_valid | bbox_size,occt_valid |
| 102760_26430589_0037 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 103284_e25015aa_0003 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 103284_e25015aa_0004 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 104283_e5646f96_0000 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 104453_aba0f2d1_0002 | neg_02 | E3_radius_up | cylinder_radius | q_bbox_u,q_occt_valid | bbox_size,occt_valid |
| 104453_aba0f2d1_0002 | neg_03 | E1_envelope_v_shrink | bbox_size | q_occt_valid | occt_valid |
| 104524_f829aab2_0001 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 106323_77f22d29_0004 | neg_01 | E5_extent_type_change | symmetric_about_plane | q_bbox_w | bbox_size |
| 106817_bb28b7aa_0002 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 106817_bb28b7aa_0003 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 107467_a8afc51d_0000 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 107467_a8afc51d_0002 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |
| 108852_fed54702_0004 | neg_03 | E4_void_add | through_void_count | q_radius | cylinder_radius |

## Reconstruction failures (rec_fails, excluded from NDR/TQDR)

| sample_id | negative_id | operator | error_category |
|---|---|---|---|
| 102314_91648bfc_0000 | neg_03 | E6_inner_gt_outer | E6_validity |
| 102410_f9877a7b_0000 | neg_03 | E6_inner_gt_outer | E6_validity |
| 102410_f9877a7b_0012 | neg_03 | E6_inner_gt_outer | E6_validity |
| 106817_bb28b7aa_0004 | neg_03 | E6_inner_gt_outer | E6_validity |
| 107055_0500fdd1_0027 | neg_03 | E6_inner_gt_outer | E6_validity |
| 107668_cf76b132_0001 | neg_03 | E6_inner_gt_outer | E6_validity |
