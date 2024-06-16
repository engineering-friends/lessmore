# - Go to source

cd ${0%/*}
cd ../source

# - Install clasp

npm install -g @google/clasp

# - Login

clasp login

# - Clone project

clasp clone "<script-id>" # find script-id in google apps script project overview
# you can also create project from clasp, not tested: clasp create --title "Your Project Title"