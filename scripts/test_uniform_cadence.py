import os
import shutil
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "file:///" + os.path.join(BASE_DIR, "index.html").replace("\\", "/")
TMP_DIR = os.path.join(BASE_DIR, "review", "temp_cadence_frames")
os.makedirs(TMP_DIR, exist_ok=True)

# Build a strictly 1-frame-per-angle timeline at 30 FPS:
# 1. Intro arrival: angles 0 to 14 (15 frames = 0.5s)
# 2. Resting beauty pose: 15 frames at angle 14 (0.5s)
# 3. 3D Rotation: angles 14 to 55 (42 frames = 1.4s) -> strictly 1 angle per frame!
# 4. Apex hold: 15 frames at angle 55 (0.5s)
# 5. Reverse orbit: angles 55 down to 14 (42 frames = 1.4s) -> strictly 1 angle per frame!
# 6. Ending beauty pose: 15 frames at angle 14 (0.5s)

timeline = []
# Intro
for a in range(15):
    timeline.append(a)
# Hold
for _ in range(15):
    timeline.append(14)
# Orbit 14 -> 55
for a in range(14, 56):
    timeline.append(a)
# Hold
for _ in range(15):
    timeline.append(55)
# Return 55 -> 14
for a in range(55, 13, -1):
    timeline.append(a)
# Hold
for _ in range(15):
    timeline.append(14)

print(f"Total timeline frames: {len(timeline)} ({len(timeline)/30:.2f}s @ 30 FPS)")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1280})
    page.add_init_script("sessionStorage.setItem('nova_promo_dismissed', 'true')")
    page.goto(SITE_URL)
    page.wait_for_load_state("networkidle")
    page.locator("body.hero-intro-ready").wait_for(timeout=4000)
    
    page.evaluate("() => { window.__novaHeroManualMode = true; }")
    
    for i, angle in enumerate(timeline):
        page.evaluate(f"window.__novaHero.setFrame({angle});")
        page.screenshot(path=os.path.join(TMP_DIR, f"f_{i:04d}.jpg"), type="jpeg", quality=95)
    
    browser.close()

# Encode at 30 FPS WITHOUT ANY tmix (pure raw crisp frames)
out_mp4 = os.path.join(BASE_DIR, "review", "hero_cinematic_demonstration.mp4")
out_kwork = os.path.join(BASE_DIR, "kwork_portfolio", "work_1_hero_3d", "video.mp4")

subprocess.run([
    "ffmpeg", "-y",
    "-framerate", "30",
    "-i", os.path.join(TMP_DIR, "f_%04d.jpg"),
    "-c:v", "libx264",
    "-crf", "17",
    "-preset", "slow",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    out_mp4
], check=True)

shutil.copy2(out_mp4, out_kwork)
shutil.rmtree(TMP_DIR)

print(f"Encoded {out_mp4} successfully! Size: {os.path.getsize(out_mp4)/1024/1024:.2f} MB")
