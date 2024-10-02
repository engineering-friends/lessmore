# About

EF Org Bot

Run it to see what it does.

# Configs 

Set test/prod configs in `deps/config/config.test.yaml` and `deps/config/config.prod.yaml`

# How to run

`./run_test.sh` or `./run_prod.sh`. Should work out of the box on Linux and MacOS, if configs are set up correctly. 

# Ideas 

- Send reminders for the user to check if the member has filled the form
- Send messages to the member?
- Send messages to Matvey?
- Need a convenient scheduler with the state. State should run a function
- Do not update message inline keyboard if there hasn't been any changes
- Think about on_response pipeline. Should it delete the supressed messages?
- Default ask kwargs bot-wise?
- Make buttons work with main menu (including start and cancel buttons)
- Async state
- Make compatible with other aiogram bots, make separate start_polling function, like register_dispatcher. Where to start initial_starters?
- Think better about the inplace mode. What are use cases?
- Think about windows: current open pages, where we have an active page. We should be able to switch between them
- clean_up function to run before new asks
