### vial-gui

# Docs and getting started

### Please visit [vial-kb.github.io](https://vial-kb.github.io/) to get started with Vial

Vial is an open-source cross-platform (Windows, Linux and Mac) GUI and a QMK fork for configuring your keyboard in real time, similar to VIA.


![](https://vial-kb.github.io/img/vial-win-1.png)


---


#### Releases

Currently, no releases are provided. You can download a precompiled binary from latest GitHub Action: https://github.com/vial-kb/vial-gui/actions (need to log into a github account).

#### Development

Python 3.6 is recommended (3.6 is the latest version that is officially supported by `fbs`).

Install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To launch the application afterwards:

```
source venv/bin/activate
fbs run
```
