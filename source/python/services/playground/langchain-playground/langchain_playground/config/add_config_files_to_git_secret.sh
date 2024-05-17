# - Add all yaml files to git secret

find . -name "*.yaml" -exec git secret add {} \;