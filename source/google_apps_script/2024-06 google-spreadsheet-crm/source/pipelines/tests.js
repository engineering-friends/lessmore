function inflate_groups_test() {
  inflate_groups({ sheet_name: "GroupsTest" });
}

function update_missing_invites_test() {
  update_missing_invites({
    started_at: get_current_timestamp(),
    sheet_name: "GroupsTest",
  });
}

function join_groups_test() {
  join_groups({
    started_at: get_current_timestamp(),
    sheet_name: "GroupsTest",
  });
}

function clear_old_posts_test() {
  clear_old_posts({ sheet_name: "GroupsTest", ttl_seconds: 60 });
}

function prepare_course_test() {
  prepare_course({ prefix: "CourseTest" });
}

function send_messages_to_groups_test() {
  send_messages_to_groups({
    started_at: get_current_timestamp(),
    posts_sheet_name: "PostsTest",
  });
}

function post_event_test() {
  post_event({
    text: "Text",
    image_url: "",
    channel_id: DebugGroup,
  });
  post_event({
    text: "Text",
    image_url:
      "https://drive.google.com/file/d/1a2kWw90MbKjYy207-DcRrarL1_V2j_Eu/view?usp=drive_link",
    channel_id: DebugGroup,
  });
}
