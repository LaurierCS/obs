# LCS OBS Kit (YouTube streaming)

The settings, scenes and branded overlays for streaming LCS events to YouTube. Anyone on any laptop can import these.

## Setup (once per laptop, about 5 minutes)

0. **Install the official OBS Studio (version 30 or newer).** The branded scenes need OBS's **Browser Source**, which the official builds include.
   - **Windows:** [OBS for Windows](https://obsproject.com/download#windows) (the installer).
   - **Mac:** [OBS for macOS](https://obsproject.com/download#mac). Pick **Apple Silicon** for M-series Macs and **Intel** for older ones.
   - **Linux (Ubuntu or Debian):** use the official PPA, not the stock `apt` package. Ubuntu's own `obs-studio` package leaves out Browser Source, so the scenes come up blank. This upgrades OBS in place and keeps your settings.
     ```
     sudo add-apt-repository ppa:obsproject/obs-studio
     sudo apt update && sudo apt install obs-studio
     ```
   - **Other Linux:** [OBS on Flathub](https://flathub.org/apps/com.obsproject.Studio).
   - All versions are listed on [OBS releases on GitHub](https://github.com/obsproject/obs-studio/releases/latest).
1. **Unzip this folder to a fixed place**
   - Windows: `C:\LCS-OBS`
   - Mac: `/Users/Shared/LCS-OBS`
   - Anywhere else: run `python3 make_scenes.py` inside the folder. It writes a scene file with the right paths into `scenes/`.
2. **Profile (the stream settings):** in OBS, go to **Profile > Import** and pick `profiles/LCS_Stream_1080p`. Then choose it from **Profile**.
   - If the laptop struggles (you'll see "Encoding overloaded" or dropped frames in the bottom bar), import and switch to `LCS_Stream_720p_Lite` instead.
3. **Scenes:** go to **Scene Collection > Import** and pick `scenes/LCS Stream (Windows).json` or `(Mac).json`. Then choose **LCS Stream** from **Scene Collection**.
4. **Point the sources at this laptop's hardware:**
   - Double-click **Screen** and pick the display.
   - Double-click **Camera** and pick the webcam.
   - In the audio mixer, open the gear on **Mic/Aux**, go to Properties and pick the mic.
   - On Mac, give OBS Screen Recording and Camera permission in System Settings.
5. **YouTube:** go to **Settings > Stream**. The service is already YouTube (RTMPS), so paste the stream key from YouTube Studio > Go Live > Stream. You can also click "Connect Account".

## Troubleshooting

- **The scenes are blank or the LCS sources are missing:** your OBS has no Browser Source. Install the official build from step 0.
- **The camera is black:** double-click **Camera** and select your webcam.

## Before each stream

- Edit `overlays/config.js` to set the event title, start time, room and the next event.
- In OBS, right-click each **LCS |** source and pick **Refresh**, or restart OBS.
- The countdown counts to `start`, for example `"19:30"`. If `start` is empty, it uses `minutes`. If both are empty, it counts to the next :00 or :30.

## Scenes

| Scene | What it's for |
|---|---|
| 1. Starting Soon | Countdown with branding and mascots. Put it up about 10 minutes before. |
| 2. Screen + Cam | Full-screen share with the camera in the bottom-right corner, no frame, so you can drag and resize it to fit any webcam. This is the default for talks and reviews. |
| 3. Speaker (Cam Full) | Full-screen camera with no overlay. Use it for intros, panels and Q&A. |
| 4. Screen Only | The screen share with no camera or branding. |
| 5. Be Right Back | Breaks. |
| 6. Thanks for Watching | Outro with the next event and links. |

The mic has noise suppression (RNNoise) and a limiter already applied.

## The settings and why

- **Video:** 1920x1080 at 30 fps. That's plenty for slides and code, and 30 fps is easy on the CPU.
- **Encoder:** x264 on the CPU, so no GPU is needed.
  - The preset is `veryfast`, which is light enough for a normal 16 GB laptop running the slides too.
  - Rate control is CBR with 2-second keyframes, which YouTube requires.
- **Bitrate:** 6000 kbps video and 160 kbps audio. That's in YouTube's range for 1080p30 and tiny next to the campus upload speed (100+ Mbps). Dynamic bitrate is on, so OBS backs off instead of dropping frames if the network dips.
  - The Lite profile is 720p30 at 3500 kbps.
- **Reconnect:** auto-reconnect is on (25 tries, 2 s apart).
- **Recording:** reuses the stream encoder, so there's no extra CPU cost. It records to MKV, which is crash-safe, and remuxes to MP4 automatically when you stop.
- **If the laptop has an NVIDIA, AMD or Apple GPU:** you can switch the encoder (Settings > Output) to NVENC, AMF or Apple VT at the same bitrate. That takes the load off the CPU.

## Editing the look

The overlays are plain HTML and CSS in `overlays/`. They use the LCS site assets and colours, with local fonts so they work offline. Previews are in `previews/`. To rebuild the scene files, run `python3 make_scenes.py`.
