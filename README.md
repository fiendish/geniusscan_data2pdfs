# geniusscan_data2pdfs
Recovers image compilation PDFs from the internal data storage of Genius Scan by The Grizzly Labs on Android phones

# System setup

## Install Android Debug Bridge (ADB) and Python 3

### macOS

 1. Go to https://brew.sh and install HomeBrew first.
 2. Type `brew install python3` in Terminal.app
 3. Type `brew cask install android-platform-tools` in Terminal.app
 
## Add Python3 library dependencies

 1. `pip3 install img2pdf`
 2. `pip3 install opencv-python`

# Usage
1. Enable USB debugging (https://web.archive.org/web/20170624042115/http://www.phonearena.com/news/How-to-enable-USB-debugging-on-Android_id53909) on your Android phone. 
2. Plug the phone into your computer.
3. Download `https://raw.githubusercontent.com/fiendish/geniusscan_data2pdfs/master/geniusscan_data2pdfs.py`
4. In your terminal, `cd` to where you downloaded that file and then type the following commands:

```adb pull /data/data/com.thegrizzlylabs.geniusscan.free/databases/database.db```

```adb pull /sdcard/Android/data/com.thegrizzlylabs.geniusscan.free/files/.image images```

```python3 geniusscan_data2pdfs.py database.db images```
