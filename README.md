# KubeDay Japan 2024

Below are the steps to setup and execute the CDK project

```sh
python -m venv .venv

.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

cdk bootstrap aws://ACCOUNT_ID/REGION

```
In case you get a Warning Message:

```sh

git config --global core.autocrlf input
git add --renormalize .
git commit -m "Normalize all line endings to LF"

```

Add a .gitattributes file

```sh
# Ensure consistent line endings
* text=auto
*.bat text eol=crlf
*.sh text eol=lf
*.py text eol=lf
*.md text eol=lf
*.json text eol=lf

```
Finally deploy the application

```sh
cdk deploy
```