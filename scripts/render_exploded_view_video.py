import os
import shutil
import subprocess
import numpy as np
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "file:///" + os.path.join(BASE_DIR, "index.html").replace("\\", "/")
TMP_DIR = os.path.join(BASE_DIR, "review", "temp_exploded_frames")
OUT_MP4_KWORK = os.path.join(BASE_DIR, "kwork_portfolio", "work_3_exploded_view", "video.mp4")
OUT_MP4_REVIEW = os.path.join(BASE_DIR, "review", "k75_exploded_view_demonstration.mp4")

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUT_MP4_KWORK), exist_ok=True)

# Smoothstep easing helper
def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

# Build timeline for 3D Exploded View:
# 1. Hold assembled state: 20 frames (0.67s)
# 2. Smooth explosion 0 -> 1: 75 frames (2.50s)
# 3. Hold exploded state: 30 frames (1.00s)
# 4. Smooth reassembly 1 -> 0: 75 frames (2.50s)
# 5. Final assembled hold: 20 frames (0.67s)
# Total: 220 frames = 7.33s @ 30 FPS

timeline = []

# Phase 1: Assembled hold (0.0)
for _ in range(20):
    timeline.append(0.0)

# Phase 2: Explode 0.0 -> 1.0
for i in range(75):
    prog = smoothstep(i / 74.0)
    timeline.append(prog)

# Phase 3: Apex exploded hold (1.0)
for _ in range(30):
    timeline.append(1.0)

# Phase 4: Reassemble 1.0 -> 0.0
for i in range(75):
    prog = smoothstep(1.0 - (i / 74.0))
    timeline.append(prog)

# Phase 5: Final assembled hold (0.0)
for _ in range(20):
    timeline.append(0.0)

print(f"Total Exploded View frames: {len(timeline)} ({len(timeline)/30:.2f}s @ 30 FPS)")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--font-render-hinting=none"
        ]
    )
    page = browser.new_page(viewport={"width": 1920, "height": 1280})
    page.add_init_script("sessionStorage.setItem('nova_promo_dismissed', 'true')")
    page.goto(SITE_URL)
    page.wait_for_load_state("networkidle")
    page.locator("body.hero-intro-ready").wait_for(timeout=4000)
    
    # Disable Lenis and background physics
    page.evaluate("""() => {
        window.__novaHeroManualMode = true;
        if (window.__lenis) {
            window.__lenis.stop();
        }
    }""")
    
    # Pre-warm all 57 exploded scrub frames so decoding is instantaneous
    page.evaluate("""() => {
        for (let i = 0; i < 57; i++) {
            if (window.__novaStoryBreakdown) {
                window.__novaStoryBreakdown.renderFrame(i);
            }
        }
    }""")
    page.wait_for_timeout(300)
    
    # Pin scroll directly to #story section
    story_top = page.locator("#story").evaluate("el => el.offsetTop")
    page.evaluate(f"window.scrollTo(0, {story_top});")
    page.wait_for_timeout(200)
    
    print("Capturing deterministic exploded frames...")
    for i, prog in enumerate(timeline):
        page.evaluate(f"window.__novaStoryBreakdown.setProgress({prog:.4f});")
        page.screenshot(
            path=os.path.join(TMP_DIR, f"frame_{i:04d}.jpg"),
            type="jpeg",
            quality=95
        )
        if i % 40 == 0 or i == len(timeline) - 1:
            print(f"  Frame {i:3d}/{len(timeline)} | progress = {prog*100:5.1f}%")

    browser.close()

# Encode with FFmpeg (CRF 17, 30 FPS, yuv420p, faststart)
print("\nEncoding MP4 video...")
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", "30",
    "-i", os.path.join(TMP_DIR, "frame_%04d.jpg"),
    "-c:v", "libx264",
    "-crf", "17",
    "-preset", "slow",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    OUT_MP4_KWORK
], check=True)

# Copy to review folder as well
shutil.copy2(OUT_MP4_KWORK, OUT_MP4_REVIEW)

# Cleanup temp frames
shutil.rmtree(TMP_DIR)

print(f"\n[SUCCESS] Generated Exploded View Video:")
print(f"  Kwork:  {OUT_MP4_KWORK} ({os.path.getsize(OUT_MP4_KWORK)/1024/1024:.2f} MB)")
print(f"  Review: {OUT_MP4_REVIEW} ({os.path.getsize(OUT_MP4_REVIEW)/1024/1024:.2f} MB)")
