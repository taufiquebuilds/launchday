# Records docs/demo.gif. Re-record any time with:  vhs docs/demo.tape
# Edit the commands below to show the project's proof moment.

Output docs/demo.gif

Set Shell bash
Set FontSize 15
Set Width 1300
Set Height 760
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 45ms
Set WindowBar Colorful

# Setup the viewer should not see: colours on, tokens and PATH ready, clean prompt.
Hide
Type "unset NO_COLOR FORCE_COLOR; export PS1='$ ' && clear"
Enter
Sleep 500ms
Show

# 1. The shortest command that shows value.
Type "your-tool --help"
Sleep 400ms
Enter
Sleep 3s

# 2. One or two interactions, then quit.
Type "clear && your-tool run"
Sleep 400ms
Enter
Sleep 5s
