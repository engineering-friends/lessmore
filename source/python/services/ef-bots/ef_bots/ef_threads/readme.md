# About

EF Threads: forwards messages from EF Channel discussion group to the users that are subscribed to the corresponding thread.

To subscribe to a thread, user can either: 
- be the creator of the post, provided he has a filled whois with telegram username
- write anything in the thread 
- be tagged in the thread

To unsubscribe, simply react with emoji to any message, this will delete the thread forwarded messages and unsubscribe the user from the thread.

# Configs

Set test/prod configs in `deps/config/config.test.yaml` and `deps/config/config.prod.yaml`

# How to run

`./run_test.sh` or `./run_prod.sh`. Should work out of the box on Linux and MacOS, if configs are set up correctly. 
