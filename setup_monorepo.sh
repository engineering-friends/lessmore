# - Install Homebrew if needed

if [[ $(brew --version) == *"Homebrew"* ]]; then
  echo "Homebrew already installed"
else
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# - Install Poetry if needed

if [[ $(poetry --version) == *"Poetry"* ]]; then
  echo "Poetry already installed"
else
  echo "Installing Poetry..."
  curl -sSL https://install.python-poetry.org | python -
  export PATH="$HOME/.poetry/bin:$PATH"
  echo export PATH=\"\$HOME/.poetry/bin:\$PATH\" >> ~/.bashrc
  echo export PATH=\"\$HOME/.poetry/bin:\$PATH\" >> ~/.zshrc
fi

# make poetry create environment locally (see https://github.com/python-poetry/poetry/issues/108)
poetry config virtualenvs.in-project true

# - Install Git LFS if needed

brew list git-lfs || brew install git-lfs

# - Install pre-commit if needed

brew list pre-commit || brew install pre-commit
pre-commit install
