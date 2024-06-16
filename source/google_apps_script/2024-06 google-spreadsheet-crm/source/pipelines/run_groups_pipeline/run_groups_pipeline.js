function run_groups_pipeline() {
  let started_at = get_current_timestamp();
  inflate_groups();
  update_missing_invites({
    started_at: started_at,
  });
  join_groups({
    started_at: started_at,
  });
}
