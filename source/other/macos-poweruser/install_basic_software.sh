
# - Homebrew

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# - Z

wget -O $HOME/z.sh https://raw.githubusercontent.com/rupa/z/master/z.sh
printf "\n\n#initialize Z (https://github.com/rupa/z) \n. ~/z.sh \n\n" >> ~/.zshrc
source $HOME/.zshrc

# - Screen
homebrew install screen

# - Apps

brew install --cask hammerspoon
brew install --cask anaconda
brew install --cask atom
brew install --cask docker
brew install --cask iterm2
brew install --cask bitwarden
brew install --cask ace-link
brew install --cask alfred
brew install --cask appcleaner
brew install --cask hiddenbar
brew install --cask maccy
brew install --cask notion
brew install --cask numi
brew install --cask qbittorrent
brew install --cask rectangle
brew install --cask spotify
brew install --cask teamviewer
brew install --cask termius
brew install --cask telegram
brew install --cask whatsapp
brew install --cask vlc
brew install --cask zoom
brew install --cask karabiner-elements