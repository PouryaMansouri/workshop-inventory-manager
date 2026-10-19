[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 1505
unverified_code_nodes: 0
raw_edges: 2572
valid_candidate_edges: 2311
missing_endpoint_edges: 0
dangling_endpoint_edges: 261
external_reference_edges: 0
self_loop_edges: 10
exact_duplicate_edges: 0
directed_unique_endpoint_pairs: 2293
directed_same_endpoint_collapsed_edges: 18
undirected_unique_endpoint_pairs: 2293
undirected_same_endpoint_collapsed_edges: 18
same_endpoint_group_count: 18
relation_variant_groups: 18
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 0
post_build_graph_type: Graph
post_build_edges: 2554
producer_suppression_sites: 12
producer_suppression_examples:
  - L1646 seen_ids arity=unknown
  - L2179 seen_ids arity=unknown
  - L2181 seen_doc_refs arity=unknown
  - L2551 seen_ids arity=unknown
  - L2698 seen_ids arity=unknown
  - L3424 seen_keys arity=unknown
  - L3593 seen_keys arity=unknown
  - L5669 seen_ids arity=unknown
examples:
  - apps_dashboard_admin_init -> apps_dashboard_widgets edges=2 relations=['imports_from', 're_exports'] locations=['L6'] contexts=['export', 'import']
  - apps_inventory_admin_init -> apps_inventory_models_init edges=2 relations=['imports_from', 're_exports'] locations=['L5'] contexts=['export', 'import']
  - apps_inventory_admin_init -> apps_inventory_admin_item_instance_admin edges=2 relations=['imports_from', 're_exports'] locations=['L13'] contexts=['export', 'import']
  - apps_inventory_admin_item_instance_admin_iteminstanceadmin -> apps_inventory_admin_actions_inventoryactionsmixin edges=2 relations=['inherits', 'uses'] locations=['L30'] contexts=['']
  - apps_inventory_models_init -> apps_inventory_models_category edges=2 relations=['imports_from', 're_exports'] locations=['L4'] contexts=['export', 'import']
note: normal graph.json is post-build; raw producer loss must be measured earlier.
