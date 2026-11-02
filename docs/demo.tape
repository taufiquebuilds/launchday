# Records docs/demo.gif. Re-record with:  vhs docs/demo.tape
# Run from the repo root. Needs python3 and the gh CLI (for the token).

Output docs/demo.gif

Set Shell bash
Set FontSize 15
Set Width 1300
Set Height 800
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set WindowBar Colorful

Hide
Type "unset NO_COLOR FORCE_COLOR; export GITHUB_TOKEN=$(gh auth token) PS1='$ ' && clear"
Enter
Sleep 1s
Show

Type "python3 scripts/audit.py examples/unlaunched-cli | head -13"
Sleep 400ms
Enter
Sleep 5s

Type "clear && python3 scripts/name_check.py csvpeek | head -9"
Sleep 400ms
Enter
Sleep 6s

Type "clear && python3 scripts/launch_time.py --tz Asia/Kolkata"
Sleep 400ms
Enter
Sleep 6s
