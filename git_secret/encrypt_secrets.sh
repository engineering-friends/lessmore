# Encrypt all secrets in the repository. This will create encrypted files with the .secret suffix.
cd ${0%/*}/.. && git secret hide