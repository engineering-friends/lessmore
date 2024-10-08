
# - Go to monorepo root

cd ${0%/*}

# - Install Homebrew if not installed

if [[ $(brew --version) == *"Homebrew"* ]]; then
  echo "Homebrew already installed"
else
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# - Install uv

if [[ $(uv --version) == *"uv"* ]]; then
  echo "uv already installed"
else
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source $HOME/.cargo/env
fi

# - Install and configure poetry (deprecated and soon will be removed)

if [[ $(poetry --version) == *"Poetry"* ]]; then
  echo "Poetry already installed"
else
  echo "Installing Poetry..."
  curl -sSL https://install.python-poetry.org | python -
  export PATH="$HOME/.poetry/bin:$PATH"
  echo export PATH=\"\$HOME/.poetry/bin:\$PATH\" >> ~/.bashrc
  echo export PATH=\"\$HOME/.poetry/bin:\$PATH\" >> ~/.zshrc
fi

# - Install Git LFS if not installed

brew list git-lfs || brew install git-lfs
git lfs pull # pull git lfs files

# - Install and configure pre-commit as a tool

uv tool install pre-commit
pre-commit install

# - Install detect-secrets as a tool

uv tool install detect-secrets

# - Configure git secret

brew list gpg || brew install gpg
brew list git-secret || brew install git-secret

bash ./git_secret/gpg_keys_import.sh
bash ./git_secret/decrypt_secrets.sh