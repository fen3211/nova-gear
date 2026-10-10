import os
import shutil
import math
import subprocess
import time
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "file:///" + os.path.join(BASE_DIR, "index.html").replace("\\", "/")
REVIEW_DIR = os.path.join(BASE_DIR, "review")
KWORK_DIR = os.path.join(BASE_DIR, "kwork_portfolio", "work_1_hero_3d")
TMP_FRAMES_DIR = os.path.join(BASE_DIR, "review", "temp_scroll_frames")

TARGET_W = 1920
TARGET_H = 1280
FPS = 60
TOTAL_FRAMES = 360  # 6.0 seconds @ 60 FPS

def ease_out_quart(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 4

def ease_in_out_sine(t):
    t = max(0.0, min(1.0, t))
    return 0.5 * (1.0 - math.cos(math.pi * t))

def main():
    print("=" * 64, flush=True)
    print("NOVA GEAR — 60 FPS CINEMATIC SCROLL DEMO RENDERER", flush=True)
    print(f"Viewport: {TARGET_W}x{TARGET_H} @ {FPS} FPS | {TOTAL_FRAMES} frames ({TOTAL_FRAMES/FPS:.1f}s)", flush=True)
    print("=" * 64, flush=True)

    os.makedirs(TMP_FRAMES_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)
    os.makedirs(KWORK_DIR, exist_ok=True)

    # Clean old temp frames
    for f in os.listdir(TMP_FRAMES_DIR):
        if f.endswith(".jpg") or f.endswith(".png"):
            os.remove(os.path.join(TMP_FRAMES_DIR, f))

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--font-render-hinting=none"
            ]
        )
        page = browser.new_page(
            viewport={"width": TARGET_W, "height": TARGET_H},
            device_scale_factor=1
        )
        page.add_init_script("sessionStorage.setItem('nova_promo_dismissed', 'true')")
        print("Navigating to site...", flush=True)
        page.goto(SITE_URL)
        page.wait_for_load_state("networkidle")
        page.locator("body.hero-intro-ready").wait_for(timeout=4000)
        page.wait_for_timeout(300)

        track = page.locator("#heroScrollTrack")
        track_box = track.bounding_box()
        max_scroll = (track_box["height"] - TARGET_H) if track_box else 1920
        # Scroll distance down the hero track to reach beauty exploded angle
        target_scroll_dist = max_scroll * 0.85
        print(f"Hero track total travel: {max_scroll:.1f}px (target scroll: {target_scroll_dist:.1f}px)", flush=True)

        # Enable manual mode to silence any background physics loops
        page.evaluate("""() => {
            window.__novaHeroManualMode = true;
            if (window.__novaHero) {
                window.__novaHero.setFrame(0);
            }
        }""")

        print(f"\nCapturing {TOTAL_FRAMES} deterministic 60 FPS scroll frames...", flush=True)
        t_start = time.time()

        for i in range(TOTAL_FRAMES):
            # Choreography timeline (total 360 frames = 6.00s):
            # Phase 1: [0..45] (0.00s - 0.75s): Intro arrival from frame 0 -> 14 at scroll = 0
            if i < 45:
                prog = i / 45.0
                eased = ease_out_quart(prog)
                target_frame = eased * 14.0
                scroll_y = 0.0

            # Phase 2: [45..65] (0.75s - 1.08s): Brief resting register at frame 14 (0.33s)
            elif i < 65:
                target_frame = 14.0
                scroll_y = 0.0

            # Phase 3: [65..225] (1.08s - 3.75s): Smooth Scroll Down (2.67s = 160 frames)
            # Both scroll position and 3D angle advance in perfect synchrony!
            elif i < 225:
                prog = (i - 65) / 160.0
                eased = ease_in_out_sine(prog)
                target_frame = 14.0 + eased * 41.0
                scroll_y = eased * target_scroll_dist

            # Phase 4: [225..245] (3.75s - 4.08s): Apex hold at frame 55 (0.33s)
            elif i < 245:
                target_frame = 55.0
                scroll_y = target_scroll_dist

            # Phase 5: [245..360] (4.08s - 6.00s): Smooth Scroll Back Up to top (1.92s = 115 frames)
            else:
                prog = (i - 245) / 115.0
                eased = ease_in_out_sine(prog)
                target_frame = 55.0 - eased * 41.0
                scroll_y = (1.0 - eased) * target_scroll_dist

            # Execute scroll and frame update in lockstep
            page.evaluate(f"""() => {{
                window.scrollTo(0, {scroll_y});
                window.__novaHero.setFrame({target_frame});
            }}""")

            frame_filename = os.path.join(TMP_FRAMES_DIR, f"frame_{i:04d}.jpg")
            page.screenshot(path=frame_filename, type="jpeg", quality=92)

            if i % 60 == 0 or i == TOTAL_FRAMES - 1:
                elapsed = time.time() - t_start
                rate = (i + 1) / max(0.01, elapsed)
                print(f"  Frame {i:3d}/{TOTAL_FRAMES} | scroll={scroll_y:6.1f}px | target_frame={target_frame:4.1f} | {rate:.1f} fps", flush=True)

        browser.close()
        t_capture = time.time() - t_start
        print(f"\nCaptured {TOTAL_FRAMES} frames in {t_capture:.1f}s ({TOTAL_FRAMES/t_capture:.1f} fps)!", flush=True)

    # Encode with cinematic temporal smoothing (tmix 1 2 1) to eliminate all discrete stepping
    output_mp4_review = os.path.join(REVIEW_DIR, "hero_cinematic_demonstration.mp4")
    output_mp4_kwork = os.path.join(KWORK_DIR, "video.mp4")

    print("\nEncoding 60 FPS MP4 with temporal motion smoothing (tmix)...", flush=True)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(TMP_FRAMES_DIR, "frame_%04d.jpg"),
        "-filter:v", "tmix=frames=3:weights='1 2 1'",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_mp4_review
    ]

    res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if res.returncode == 0:
        file_sz_mb = os.path.getsize(output_mp4_review) / (1024 * 1024)
        print(f"  [SUCCESS] Created {output_mp4_review}: {file_sz_mb:.2f} MB", flush=True)
        shutil.copy2(output_mp4_review, output_mp4_kwork)
        print(f"  [COPIED] {output_mp4_kwork}: {file_sz_mb:.2f} MB", flush=True)
    else:
        print("FFmpeg Error:", res.stderr, flush=True)

    # Clean up temp frames
    print("\nCleaning up temp frames...", flush=True)
    try:
        shutil.rmtree(TMP_FRAMES_DIR)
        print("Temp frames directory cleaned.", flush=True)
    except Exception as e:
        print("Cleanup error:", e, flush=True)

    print("\n" + "=" * 64, flush=True)
    print("CINEMATIC SCROLL VIDEO GENERATION COMPLETE!", flush=True)
    print("=" * 64, flush=True)

if __name__ == "__main__":
    main()
