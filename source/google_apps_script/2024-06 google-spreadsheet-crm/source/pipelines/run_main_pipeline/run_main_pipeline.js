function run_main_pipeline() {
  let started_at = get_current_timestamp();
  clear_old_posts();
  prepare_course();
  send_messages_to_groups({
    started_at: started_at,
  });
}
