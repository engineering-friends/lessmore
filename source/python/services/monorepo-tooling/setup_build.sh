# Prepare service for building: prepare monorepo, export necessary environment variables

# Arguments: build_config_path

# - Install monorepo-tooling poetry environment

cd $DEEPLAY_MONOREPO_PATH/source/python/services/monorepo-tooling/

poetry install

# - Export environment variables

if [[ $(poetry run python monorepo_tooling/export_config_envs.py --path "$1"|| echo "error") == "error" ]]; then
  exit 1 # error in python code
else
  export $(poetry run python monorepo_tooling/export_config_envs.py --path "$1")
fi


if [[ $(poetry run python monorepo_tooling/export_image_name_envs.py || echo "error") == "error" ]]; then
  exit 1 # error in python code
else
  export $(poetry run python monorepo_tooling/export_image_name_envs.py)
fi

# check what is in exports
#echo $(poetry run python monorepo_tooling/print_environment_file_for_export.py --path ${0%/*}/../config/local.env --is-required False)
#echo $(poetry run python monorepo_tooling/print_environment_file_for_export.py --path ${0%/*}/../config/.env --is-required True)
#echo $(poetry run python monorepo_tooling/print_git_and_docker_environments_for_export.py)

cd $DEEPLAY_MONOREPO_PATH