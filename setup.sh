
# - Go to monorepo root

cd ${0%/*}

# - Install Homebrew if not installed

if [[ $(brew --version) == *"Homebrew"* ]]; then
  echo "Homebrew already installed"
else
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# - Install and configure poetry

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

# - Install and configure pre-commit

pip install pre-commit
pre-commit install

# - Install detect-secrets

pip install detect-secrets

# - Install git secret

brew list gpg || brew install gpg
brew list git-secret || brew install git-secret