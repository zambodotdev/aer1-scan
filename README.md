# aer1-scan

Check every Zambo receipt in the work you were handed, from your terminal.

Someone gives you AI work full of receipt links: a pull request, a report, a chat log. Instead of clicking each one, run one command. aer1-scan finds every Zambo receipt in a file, a web page, or piped text, checks each one live, and prints one line per receipt. It sends only the receipt ids, nothing else from the document.

A Zambo receipt proves the saved result of an AI job was not changed after the fact. It does not prove the answer was right. It proves the record you are checking is the record that was saved at the time.

## Install

Node:
```
npx aer1-scan FILE
```
or `npm install -g aer1-scan`

Python:
```
pipx run aer1-scan FILE
```
or `pip install aer1-scan`

Same tool, same output, both published from this repo.

## Use

```
aer1-scan report.md
aer1-scan https://gist.github.com/zambodotdev/777872582b8dd2feefa43bf1d4fa1acf
cat chat-log.txt | aer1-scan
```

Output, one line per receipt:
```
verified 5420f6f0-a635-4010-a7d4-311f7cd6b0ab https://zambo.dev/verify/?id=5420f6f0-a635-4010-a7d4-311f7cd6b0ab
not found 00000000-0000-4000-8000-000000000000 https://zambo.dev/verify/?id=00000000-0000-4000-8000-000000000000
```

Exit code is 0 when every receipt verifies, 1 when any does not, so it drops straight into CI and pre-commit hooks.

Prefer clicking? The same check runs in your browser at https://zambodotdev.github.io/receipt-scan/

Want receipts on your own AI work: add Zambo in one URL, no key, at https://zambo.dev/add/?ref=aer1-scan

Founder: Brennan Zambo (https://zambo.dev/founder/). Support: https://zambo.dev/add/?ref=aer1-scan
