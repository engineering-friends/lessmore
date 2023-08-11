# snapshot of [notion page](https://www.notion.so/marklidenberg/git-secret-install-and-basic-usage-993f9d9684bb49e6bcb1a2fead5421d5?pvs=4) from 2023-08-11

- Create gpg keys
    - `gpg --full-generate-key`
        - Passphrase will be asked on every decryption
    - Optional: export keys and store them safely
        - Find ID: `gpg --list-secret-keys`
            
            ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/e3bccaa4-94bf-4d14-ac3f-0d3f5cc0c837/Untitled.png)
            
        - Export
            
            ```jsx
            gpg --export --armor [Key ID] > ~/my_public_key.asc
            gpg --export-secret-keys [Key ID] > ~/my_private_key.gpg
            ```
            
        - Note: `.gpg` is common for the binary format, `.asc` when armored.
        - Copy your keys to secure place for backup
- Initialize the `git-secret` repository by running `git secret init`
- Make sure that `.gitsecret/` has been created
- Make sure that all files in `.gitsecret` are added to git, except random_seed  (due to .gitignore settings)
- Commit `.gitsecret` 
- Commands
    - Register user: `git secret tell marklidenberg@gmail.com`
    - Add file: `git secret add test_git_secret.txt`
    - Remove file: `git secret remove test_git_secret.txt`
    - Enrcypt: `git secret hide`
    - Decrypt: `git secret reveal`

# Misc

- How to remove gpg key
    - Get list of keys, find id: `gpg —list-keys`
        
        ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/e3bccaa4-94bf-4d14-ac3f-0d3f5cc0c837/Untitled.png)
        
    - Remove private key: `gpg —delete-secret-keys <ID>`
    - Remove public key: `gpg —delete-key <ID`
- How to import keys
    - `gpg --import /path/to/your_public_key.asc`
    - `gpg --import /path/to/your_private_key.gpg`
- How to move secret file?
    - You need to remove it and then add it again. Not great, not terrible