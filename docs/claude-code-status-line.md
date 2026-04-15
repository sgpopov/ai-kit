# Setup Claude Code status line

1. Install `jq` - `brew install jq`
2. Enter claude code
3. Install statusline

```
/statusline install statusline globally on this Mac. Create a separate SH file for this script
```

4. Once installed, exit claude code and address the permissions:

```
chmod +x ~/.claude/statusline.sh
```

5. Enter claude code again and configure the status line:

```
/statusline build custom status line - model | context: 42% remaining | session: % remaining | git-branch
```

