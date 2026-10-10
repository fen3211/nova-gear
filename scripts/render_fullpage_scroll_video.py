import os
import shutil
import subprocess
import time
import numpy as np
from scipy.interpolate import PchipInterpolator
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "file:///" + os.path.join(BASE_DIR, "index.html").replace("\\", "/")
TMP_DIR = os.path.join(BASE_DIR, "review", "temp_fullpage_frames")
OUT_MP4_REVIEW = os.path.join(BASE_DIR, "review", "nova_gear_fullpage_scroll.mp4")
OUT_MP4_KWORK = os.path.join(BASE_DIR, "kwork_portfolio", "work_4_editorial_catalog", "video.mp4")

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUT_MP4_KWORK), exist_ok=True)

# Keyframe waypoints for smooth monotonic scroll across the whole page (781 frames = 26.0s @ 30 FPS)
# Max scroll on 1920x1280 is 12062 px
keyframes = [
    (0, 0),          # Start at hero
    (40, 0),         # Hold hero beauty arrival (1.33s)
    (140, 2009),     # Hero 3D scrub finishes (4.67s)
    (170, 2400),     # Curated releases catalog header
    (250, 3600),     # K75 & Pulse Pro cards view
    (330, 4600),     # Orbit ANC & Flux 100W cards view
    (410, 5600),     # NovaDesk XL & Beam RGB cards view
    (480, 6800),     # Brand statement & Engineering features
    (560, 8600),     # Obsessive By Design / 3D exploded breakdown story
    (640, 10400),    # Reviews & Journal
    (720, 12062),    # Care & Support, Newsletter, reaching Footer
    (780, 12062)     # Hold footer at the bottom (2.0s)
]

kf_frames, kf_ys = zip(*keyframes)
interp = PchipInterpolator(kf_frames, kf_ys)

t = np.arange(781)
y_curve = interp(t)

print("=" * 64)
print(f"NOVA GEAR — FULL PAGE SCROLL CINEMATIC RENDERER")
print(f"Total timeline frames: {len(y_curve)} ({len(y_curve)/30:.2f}s @ 30 FPS)")
print(f"Resolution: 1920x1280 (3:2) | Max Scroll: {y_curve[-1]:.0f} px")
print("=" * 64)

t_start = time.time()

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
    
    print("Navigating to NOVA GEAR site...")
    page.goto(SITE_URL)
    page.wait_for_load_state("networkidle")
    page.locator("body.hero-intro-ready").wait_for(timeout=4000)
    
    # Initialize deterministic rendering environment
    page.evaluate("""() => {
        window.__novaHeroManualMode = true;
        if (window.__lenis) {
            window.__lenis.stop();
        }
        // Pre-reveal cards to prevent any late transition jumps
        document.querySelectorAll('.product-card').forEach(c => c.classList.add('card-revealed'));
        
        // Pre-decode all 3D assets
        if (window.__novaHero) {
            for (let i = 0; i < 56; i++) window.__novaHero.drawFrame(i);
        }
        if (window.__novaStoryBreakdown) {
            for (let i = 0; i < 57; i++) window.__novaStoryBreakdown.renderFrame(i);
        }
    }""")
    page.wait_for_timeout(300)

    print("\nCapturing 781 deterministic scroll frames...")
    for i, raw_y in enumerate(y_curve):
        target_y = int(round(raw_y))
        
        page.evaluate(f"""() => {{
            window.scrollTo(0, {target_y});
            
            // Synchronize Hero 3D camera
            if (window.__novaHero) {{
                if ({target_y} <= 0) {{
                    window.__novaHero.setFrame(14);
                }} else if ({target_y} <= 2009) {{
                    const p = {target_y} / 2009.0;
                    const f = Math.round(14 + p * (55 - 14));
                    window.__novaHero.setFrame(f);
                }} else {{
                    window.__novaHero.setFrame(55);
                }}
            }}
            
            // Synchronize Story Exploded 3D breakdown
            if (window.__novaStoryBreakdown) {{
                const storyTop = 7495;
                const storyTravel = 1800;
                if ({target_y} < storyTop) {{
                    window.__novaStoryBreakdown.setProgress(0.0);
                }} else if ({target_y} <= storyTop + storyTravel) {{
                    const p = ({target_y} - storyTop) / storyTravel;
                    window.__novaStoryBreakdown.setProgress(p);
                }} else {{
                    window.__novaStoryBreakdown.setProgress(1.0);
                }}
            }}
        }}""")
        
        frame_path = os.path.join(TMP_DIR, f"frame_{i:04d}.jpg")
        page.screenshot(path=frame_path, type="jpeg", quality=95)
        
        if i % 60 == 0 or i == len(y_curve) - 1:
            elapsed = time.time() - t_start
            rate = (i + 1) / max(0.01, elapsed)
            print(f"  Frame {i:3d}/{len(y_curve)} | y = {target_y:5d} px | {rate:.1f} fps")

    browser.close()
    t_capture = time.time() - t_start
    print(f"\nAll {len(y_curve)} frames captured in {t_capture:.1f}s ({len(y_curve)/t_capture:.1f} fps)!")

# Encode with FFmpeg (CRF 17, 30 FPS, yuv420p, faststart)
print("\nEncoding broadcast-grade MP4 video...")
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", "30",
    "-i", os.path.join(TMP_DIR, "frame_%04d.jpg"),
    "-c:v", "libx264",
    "-crf", "17",
    "-preset", "slow",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    OUT_MP4_REVIEW
], check=True)

# Copy to work_4_editorial_catalog as well
shutil.copy2(OUT_MP4_REVIEW, OUT_MP4_KWORK)

# Clean up temp frames
print("Cleaning up temporary frame cache...")
shutil.rmtree(TMP_DIR)

review_sz_mb = os.path.getsize(OUT_MP4_REVIEW) / (1024 * 1024)
kwork_sz_mb = os.path.getsize(OUT_MP4_KWORK) / (1024 * 1024)

print("\n" + "=" * 64)
print("FULL PAGE SCROLL VIDEO COMPLETE!")
print(f"  Review: {OUT_MP4_REVIEW} ({review_sz_mb:.2f} MB)")
print(f"  Kwork:  {OUT_MP4_KWORK} ({kwork_sz_mb:.2f} MB)")
print("=" * 64)
