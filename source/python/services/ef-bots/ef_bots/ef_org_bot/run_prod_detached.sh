# - Go to the service directory

cd ${0%/*}
screen -X -S ef_bot_org quit
screen -dmS ef_bot_org -L -Logfile logs/prod.log run_prod.sh
#screen -dmS ef_bot_org ./run_prod.sh # maco