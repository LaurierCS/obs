#!/usr/bin/env python3
"""Builds the LCS OBS scene collection with the right file paths for your computer.

  python3 make_scenes.py                 # auto-detects OS, uses this folder's location
  python3 make_scenes.py --os win --dir "C:/LCS-OBS"

Then in OBS: Scene Collection > Import > pick the generated "LCS Stream (<os>).json".
"""
import argparse, json, os, platform, uuid

PLATFORM = {
    "win":   dict(display="monitor_capture", display_settings={"capture_cursor": True},
                  cam="dshow_input", mic="wasapi_input_capture", desk="wasapi_output_capture"),
    "mac":   dict(display="screen_capture", display_settings={"type": 0, "show_cursor": True},
                  cam="av_capture_input_v2", mic="coreaudio_input_capture", desk=None),
    "linux": dict(display="xshm_input", display_settings={"show_cursor": True},
                  cam="v4l2_input", mic="pulse_input_capture", desk="pulse_output_capture"),
}
W, H = 1920, 1080

def uid(name): return str(uuid.uuid5(uuid.NAMESPACE_URL, "lcs-obs/" + name))

def source(name, sid, settings=None, filters=None, volume=1.0, mixers=255):
    unversioned = sid[:-3] if sid.endswith(("_v2", "_v3")) else sid
    return {"name": name, "uuid": uid(name), "id": unversioned, "versioned_id": sid,
            "settings": settings or {}, "mixers": mixers, "sync": 0, "flags": 0, "volume": volume,
            "balance": 0.5, "enabled": True, "muted": False, "push-to-mute": False, "push-to-mute-delay": 0,
            "push-to-talk": False, "push-to-talk-delay": 0, "hotkeys": {}, "deinterlace_mode": 0,
            "deinterlace_field_order": 0, "monitoring_type": 0, "private_settings": {},
            "filters": filters or []}

def item(name, i, x=0, y=0, w=W, h=H, fit=2, visible=True, locked=False):
    # fit: 2 = scale to inner bounds (no cropping), 3 = scale to outer bounds (fill)
    return {"name": name, "source_uuid": uid(name), "visible": visible, "locked": locked, "rot": 0.0,
            "pos": {"x": float(x), "y": float(y)}, "scale": {"x": 1.0, "y": 1.0}, "align": 5,
            "bounds_type": fit, "bounds_align": 0, "bounds": {"x": float(w), "y": float(h)},
            "crop_left": 0, "crop_top": 0, "crop_right": 0, "crop_bottom": 0, "id": i,
            "group_item_backup": False, "scale_filter": "disable", "blend_method": "default",
            "blend_type": "normal", "show_transition": {"duration": 0}, "hide_transition": {"duration": 0},
            "private_settings": {}}

def scene(name, items):
    s = source(name, "scene", {"id_counter": len(items), "custom_size": False,
                               "items": [item(*a[:1], n + 1, *a[1:]) if not isinstance(a, dict) else a for n, a in enumerate(items)]}, mixers=0)
    return s

def build(os_key, base):
    p = PLATFORM[os_key]
    base = base.replace("\\", "/").rstrip("/")
    ov = lambda f: f"{base}/overlays/{f}"
    def browser(name, f, restart=False):
        return source(name, "browser_source", {"is_local_file": True, "local_file": ov(f), "width": W, "height": H,
                      "fps_custom": False, "reroute_audio": False, "restart_when_active": restart,
                      "shutdown": False, "css": "body{background-color:rgba(0,0,0,0);margin:0;overflow:hidden}"}, mixers=0)
    noise = {"name": "Noise Suppression", "uuid": uid("mic-ns"), "id": "noise_suppress_filter",
             "versioned_id": "noise_suppress_filter_v2", "settings": {"method": "rnnoise"}, "enabled": True,
             "mixers": 0, "sync": 0, "flags": 0, "volume": 1.0, "balance": 0.5, "muted": False,
             "private_settings": {}, "hotkeys": {}}
    limiter = {"name": "Limiter", "uuid": uid("mic-lim"), "id": "limiter_filter", "versioned_id": "limiter_filter",
               "settings": {"threshold": -3.0, "release_time": 60}, "enabled": True, "mixers": 0, "sync": 0,
               "flags": 0, "volume": 1.0, "balance": 0.5, "muted": False, "private_settings": {}, "hotkeys": {}}
    inputs = [
        browser("LCS | Starting Soon", "starting.html", restart=True),
        browser("LCS | Be Right Back", "brb.html"),
        browser("LCS | Thanks for Watching", "ending.html"),
        source("Screen", p["display"], p["display_settings"], mixers=255),
        source("Camera", p["cam"], {}, mixers=255),
    ]
    camx, camy, camw, camh = 1504, 812, 384, 216
    scenes = [
        scene("1. Starting Soon", [("LCS | Starting Soon",)]),
        scene("2. Screen + Cam", [("Screen", 0, 0, W, H, 2), ("Camera", camx, camy, camw, camh, 2)]),
        scene("3. Speaker (Cam Full)", [("Camera", 0, 0, W, H, 3)]),
        scene("4. Screen Only", [("Screen", 0, 0, W, H, 2)]),
        scene("5. Be Right Back", [("LCS | Be Right Back",)]),
        scene("6. Thanks for Watching", [("LCS | Thanks for Watching",)]),
    ]
    mic = source("Mic/Aux", p["mic"], {"device_id": "default"}, filters=[noise, limiter])
    mic["hotkeys"] = {}
    coll = {"name": f"LCS Stream", "current_scene": scenes[0]["name"], "current_program_scene": scenes[0]["name"],
            "scene_order": [{"name": s["name"]} for s in scenes], "sources": inputs + scenes, "groups": [],
            "quick_transitions": [], "transitions": [], "saved_projectors": [], "current_transition": "Fade",
            "transition_duration": 300, "preview_locked": False, "scaling_enabled": False, "scaling_level": 0,
            "scaling_off_x": 0.0, "scaling_off_y": 0.0, "modules": {}, "AuxAudioDevice1": mic}
    if p["desk"]:
        coll["DesktopAudioDevice1"] = source("Desktop Audio", p["desk"], {"device_id": "default"})
    return coll

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    auto = {"Windows": "win", "Darwin": "mac"}.get(platform.system(), "linux")
    ap = argparse.ArgumentParser()
    ap.add_argument("--os", choices=PLATFORM, default=auto)
    ap.add_argument("--dir", default=here, help="where the LCS-OBS folder lives on the streaming laptop")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(here, "scenes", f"LCS Stream ({a.os}).json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(build(a.os, a.dir), open(out, "w"), indent=2)
    print("wrote", out)
