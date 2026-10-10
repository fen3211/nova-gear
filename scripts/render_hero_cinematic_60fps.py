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
TMP_FRAMES_DIR = os.path.join(BASE_DIR, "review", "temp_60fps_frames")

TARGET_W = 1920
TARGET_H = 1280
FPS = 60
TOTAL_FRAMES = 480  # 8.0 seconds at 60 FPS

def ease_out_quart(t):
    """Quartic ease-out for natural deceleration: 1 - (1-t)^4"""
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 4

def ease_in_out_sine(t):
    """Sinusoidal ease-in-out for fluid mechanical rotation"""
    t = max(0.0, min(1.0, t))
    return 0.5 * (1.0 - math.cos(math.pi * t))

def main():
    print("=" * 64, flush=True)
    print("NOVA GEAR — 60 FPS CINEMATIC HERO VIDEO RENDERER", flush=True)
    print(f"Target: {TARGET_W}x{TARGET_H} @ {FPS} FPS | {TOTAL_FRAMES} frames ({TOTAL_FRAMES/FPS:.1f}s)", flush=True)
    print("=" * 64, flush=True)

    os.makedirs(TMP_FRAMES_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)
    os.makedirs(KWORK_DIR, exist_ok=True)

    # 1. Clean previous temp frames
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

        # Ensure all 56 hero frames are fully cached in browser
        page.evaluate("""() => new Promise((resolve) => {
            let loaded = 0;
            const total = 56;
            for (let i = 0; i < total; i++) {
                const img = new Image();
                img.onload = img.onerror = () => {
                    loaded++;
                    if (loaded >= total) resolve();
                };
                img.src = `./assets/frames_hero/k75_hero_${String(i).padStart(2, '0')}.webp`;
            }
        })""")

        # Get track travel
        track = page.locator("#heroScrollTrack")
        track_box = track.bounding_box()
        max_scroll = (track_box["height"] - TARGET_H) if track_box else 1800
        print(f"Hero scroll track max travel: {max_scroll:.1f}px", flush=True)

        has_helper = page.evaluate("() => typeof window.__novaHero !== 'undefined'")
        print(f"window.__novaHero exposed: {has_helper}", flush=True)
        if not has_helper:
            print("ERROR: window.__novaHero not found in page!", flush=True)
            browser.close()
            return

        print(f"\nCapturing {TOTAL_FRAMES} deterministic 60 FPS frames...", flush=True)
        t_start = time.time()

        for i in range(TOTAL_FRAMES):
            # Timeline choreography:
            # Segment 1: [0..70] (0.0s - 1.16s) Intro entry: Frame 0 -> 14
            if i < 70:
                prog = i / 70.0
                eased = ease_out_quart(prog)
                target_frame = eased * 14.0
                scroll_y = 0.0

            # Segment 2: [70..130] (1.16s - 2.16s) Beauty pause at frame 14
            elif i < 130:
                target_frame = 14.0
                scroll_y = 0.0

            # Segment 3: [130..310] (2.16s - 5.16s) 3D Rotation + Scroll Scrub: Frame 14 -> 55
            elif i < 310:
                prog = (i - 130) / 180.0
                eased = ease_in_out_sine(prog)
                target_frame = 14.0 + eased * (55.0 - 14.0)
                scroll_y = eased * (max_scroll * 0.65)

            # Segment 4: [310..360] (5.16s - 6.00s) Profile hold at frame 55
            elif i < 360:
                target_frame = 55.0
                scroll_y = max_scroll * 0.65

            # Segment 5: [360..480] (6.00s - 8.00s) Smooth Return: Frame 55 -> 14, Scroll -> 0
            else:
                prog = (i - 360) / 120.0
                eased = ease_in_out_sine(prog)
                target_frame = 55.0 - eased * (55.0 - 14.0)
                scroll_y = (1.0 - eased) * (max_scroll * 0.65)

            # Update DOM deterministically
            page.evaluate(f"""() => {{
                window.scrollTo(0, {scroll_y});
                window.__novaHero.setFrame({target_frame});
            }}""")

            # Frame capture (JPEG quality 92 for high fidelity)
            frame_filename = os.path.join(TMP_FRAMES_DIR, f"frame_{i:04d}.jpg")
            page.screenshot(path=frame_filename, type="jpeg", quality=92)

            if i % 60 == 0 or i == TOTAL_FRAMES - 1:
                elapsed = time.time() - t_start
                rate = (i + 1) / max(0.01, elapsed)
                print(f"  Frame {i:3d}/{TOTAL_FRAMES} ({i/FPS:.2f}s) | target_frame={target_frame:4.1f} | {rate:.1f} fps", flush=True)

        browser.close()
        t_capture = time.time() - t_start
        print(f"\nAll {TOTAL_FRAMES} frames captured in {t_capture:.1f}s ({TOTAL_FRAMES/t_capture:.1f} fps)!", flush=True)

    # 2. Encode to high-bitrate, rock-solid 60 FPS MP4 using FFmpeg
    output_mp4_review = os.path.join(REVIEW_DIR, "hero_cinematic_demonstration.mp4")
    output_mp4_kwork = os.path.join(KWORK_DIR, "video.mp4")

    print("\nEncoding 60 FPS MP4 via FFmpeg...", flush=True)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(TMP_FRAMES_DIR, "frame_%04d.jpg"),
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
        
        # Copy to kwork_portfolio/work_1_hero_3d/video.mp4
        shutil.copy2(output_mp4_review, output_mp4_kwork)
        print(f"  [COPIED] {output_mp4_kwork}: {file_sz_mb:.2f} MB", flush=True)
    else:
        print("FFmpeg Error:", res.stderr, flush=True)

    # 3. Clean up temp frames to keep repository lightweight
    print("\nCleaning up temp frames...", flush=True)
    try:
        shutil.rmtree(TMP_FRAMES_DIR)
        print("Temp frames directory cleaned.", flush=True)
    except Exception as e:
        print("Cleanup error:", e, flush=True)

    print("\n" + "=" * 64, flush=True)
    print("60 FPS HERO VIDEO GENERATION FINISHED WITH ZERO LAG!", flush=True)
    print("=" * 64, flush=True)

if __name__ == "__main__":
    main()
