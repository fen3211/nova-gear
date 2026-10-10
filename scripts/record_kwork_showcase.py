import os
import sys
import math
import shutil
import subprocess
import time
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "file:///" + os.path.join(BASE_DIR, "index.html").replace("\\", "/")
OUT_KWORK = os.path.join(BASE_DIR, "kwork_portfolio", "showcase_video.mp4")
OUT_REVIEW = os.path.join(BASE_DIR, "review", "kwork_showcase.mp4")

# 1920x1080 @ 60 FPS | 30.0 seconds = 1800 frames
TARGET_W = 1920
TARGET_H = 1080
FPS = 60
TOTAL_FRAMES = 1800  # Exactly 30.0 seconds

def ease_out_quart(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 4

def ease_in_out_cubic(t):
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4.0 * t * t * t
    else:
        return 1.0 - math.pow(-2.0 * t + 2.0, 3) / 2.0

def ease_in_out_sine(t):
    t = max(0.0, min(1.0, t))
    return 0.5 * (1.0 - math.cos(math.pi * t))

def lerp(a, b, t):
    return a + (b - a) * t

def get_video_info(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    lines = res.stdout.strip().split("\n")
    duration = float(lines[0]) if len(lines) > 0 and lines[0] else 0.0
    size_bytes = int(lines[1]) if len(lines) > 1 and lines[1] else os.path.getsize(file_path)
    return duration, size_bytes

def main():
    print("=" * 72, flush=True)
    print(" NOVA GEAR — KWORK 60 FPS SHOWCASE VIDEO RECORDER (V2)", flush=True)
    print(f" Resolution: {TARGET_W}x{TARGET_H} @ {FPS} FPS", flush=True)
    print(f" Timeline: {TOTAL_FRAMES} frames ({TOTAL_FRAMES/FPS:.1f}s)", flush=True)
    print(f" Outputs:\n  1. {OUT_KWORK}\n  2. {OUT_REVIEW}", flush=True)
    print("=" * 72, flush=True)

    os.makedirs(os.path.dirname(OUT_KWORK), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_REVIEW), exist_ok=True)

    # Setup FFmpeg pipe with required parameters:
    # -c:v libx264 -pix_fmt yuv420p -crf 20 -preset slow -r 60
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-framerate", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        "-preset", "slow",
        "-r", str(FPS),
        "-movflags", "+faststart",
        OUT_REVIEW
    ]

    print("\nStarting FFmpeg encoder process...", flush=True)
    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

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
        print("Navigating to NOVA GEAR site...", flush=True)
        page.goto(SITE_URL)
        page.wait_for_load_state("networkidle")
        page.locator("body.hero-intro-ready").wait_for(timeout=4000)
        page.wait_for_timeout(300)

        # Inject virtual cursor overlay and setup deterministic clean scroll environment
        page.evaluate("""() => {
            window.__novaHeroManualMode = true;
            if (window.__lenis) {
                window.__lenis.destroy();
                window.__lenis = null;
            }
            document.documentElement.classList.remove('lenis', 'lenis-stopped', 'lenis-smooth');
            document.documentElement.style.overflow = 'visible';
            document.body.style.overflow = 'visible';

            // Pre-reveal cards to prevent layout jump during capture
            document.querySelectorAll('.product-card').forEach(c => c.classList.add('card-revealed'));

            // Pre-decode hero frames
            if (window.__novaHero) {
                for (let i = 0; i < 56; i++) {
                    window.__novaHero.drawFrame(i);
                }
            }

            // Virtual elegant cursor for video presentation
            const cur = document.createElement('div');
            cur.id = 'kworkDemoCursor';
            cur.style.position = 'fixed';
            cur.style.pointerEvents = 'none';
            cur.style.zIndex = '999999';
            cur.style.transform = 'translate(-2px, -2px)';
            cur.style.filter = 'drop-shadow(0 3px 8px rgba(0,0,0,0.45))';
            cur.innerHTML = `
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                    <path d="M3 2L10 21L13.5 13.5L21 10L3 2Z" fill="#111111" stroke="#FFFFFF" stroke-width="1.8" stroke-linejoin="round"/>
                </svg>
            `;
            document.body.appendChild(cur);

            window.__updateDemoCursor = (x, y, clicking = false) => {
                cur.style.left = x + 'px';
                cur.style.top = y + 'px';
                cur.style.transform = clicking ? 'translate(-2px, -2px) scale(0.85)' : 'translate(-2px, -2px) scale(1)';
            };
        }""")

        t_start = time.time()
        print(f"\nRecording {TOTAL_FRAMES} frames into FFmpeg pipeline...", flush=True)

        studio_opened = False
        studio_closed = False

        for i in range(TOTAL_FRAMES):
            # -------------------------------------------------------------
            # STAGE 1: Frames 0..180 (0.0s – 3.0s) — Hero Entry & Resting Hold
            # -------------------------------------------------------------
            if i < 180:
                scrollY = 0.0
                if i < 70:
                    prog = i / 70.0
                    hero_frame = ease_out_quart(prog) * 14.0
                    cur_x = lerp(960, 1050, prog)
                    cur_y = lerp(600, 480, prog)
                else:
                    hero_frame = 14.0
                    prog_hold = (i - 70) / 110.0
                    cur_x = lerp(1050, 920, prog_hold)
                    cur_y = lerp(480, 440, prog_hold)

                clicking = False

            # -------------------------------------------------------------
            # STAGE 2: Frames 180..720 (3.0s – 12.0s) — 3D Orbit & Telemetry
            # Viewport pinned across 250vh track (scrollY = 0 -> 1700px)
            # -------------------------------------------------------------
            elif i < 720:
                prog = (i - 180) / 540.0
                eased = ease_in_out_cubic(prog)
                scrollY = eased * 1700.0
                hero_frame = 14.0 + eased * (55.0 - 14.0)

                cur_x = 980 + 35 * math.sin(prog * math.pi * 2)
                cur_y = 460 + 25 * math.cos(prog * math.pi * 2)
                clicking = False

            # -------------------------------------------------------------
            # STAGE 3: Frames 720..1080 (12.0s – 18.0s) — Catalog Showcase
            # -------------------------------------------------------------
            elif i < 1080:
                hero_frame = 55.0

                if i < 840:
                    # Scroll from hero unpin down to catalog Pulse/Orbit view
                    prog = (i - 720) / 120.0
                    eased = ease_in_out_cubic(prog)
                    scrollY = 1700.0 + eased * (3600.0 - 1700.0)
                    cur_x = lerp(980, 750, prog)
                    cur_y = lerp(460, 500, prog)
                    clicking = False

                elif i < 920:
                    # Hover Pulse Pro card
                    scrollY = 3600.0
                    prog = (i - 840) / 80.0
                    cur_x = lerp(750, 570, ease_in_out_sine(prog))
                    cur_y = lerp(500, 480, ease_in_out_sine(prog))
                    clicking = False

                elif i < 1000:
                    # Glide across to Orbit ANC card
                    scrollY = 3600.0
                    prog = (i - 920) / 80.0
                    cur_x = lerp(570, 1320, ease_in_out_sine(prog))
                    cur_y = lerp(480, 480, ease_in_out_sine(prog))
                    clicking = False

                else:
                    # Settle on K75 card towards STUDIO button (scrollY = 2950)
                    prog = (i - 1000) / 80.0
                    scrollY = 3600.0 - ease_in_out_cubic(prog) * (3600.0 - 2950.0)
                    cur_x = lerp(1320, 1366, ease_in_out_sine(prog))
                    cur_y = lerp(480, 733, ease_in_out_sine(prog))
                    clicking = (i >= 1075)

            # -------------------------------------------------------------
            # STAGE 4: Frames 1080..1560 (18.0s – 26.0s) — Interactive Keyboard Studio
            # -------------------------------------------------------------
            elif i < 1560:
                hero_frame = 55.0
                scrollY = 2950.0

                if not studio_opened:
                    page.evaluate("""() => {
                        const btn = document.querySelector('.card-theme-k75 .btn-configurator-trigger');
                        if (btn) btn.click();
                    }""")
                    studio_opened = True

                if i < 1140:
                    # Dialog settles into center
                    prog = (i - 1080) / 60.0
                    cur_x = lerp(1366, 700, ease_in_out_sine(prog))
                    cur_y = lerp(733, 400, ease_in_out_sine(prog))
                    clicking = False

                elif i < 1240:
                    # Glide to tactile switch and click
                    prog = (i - 1140) / 100.0
                    cur_x = lerp(700, 520, ease_in_out_sine(prog))
                    cur_y = lerp(400, 475, ease_in_out_sine(prog))
                    clicking = (1198 <= i <= 1205)

                    if i == 1200:
                        page.evaluate("""() => {
                            const sw = document.querySelector('.btn-cfg-switch[data-switch="tactile"]');
                            if (sw) sw.click();
                        }""")

                elif i < 1340:
                    # Glide to Windows OS switch and click
                    prog = (i - 1240) / 100.0
                    cur_x = lerp(520, 600, ease_in_out_sine(prog))
                    cur_y = lerp(475, 260, ease_in_out_sine(prog))
                    clicking = (1298 <= i <= 1305)

                    if i == 1300:
                        page.evaluate("""() => {
                            const osBtn = document.querySelector('.btn-cfg-os[data-os="win"]');
                            if (osBtn) osBtn.click();
                        }""")

                elif i < 1440:
                    # Glide to virtual keycap ESC and click
                    prog = (i - 1340) / 100.0
                    cur_x = lerp(600, 800, ease_in_out_sine(prog))
                    cur_y = lerp(260, 495, ease_in_out_sine(prog))
                    clicking = (1398 <= i <= 1405)

                    if i == 1400:
                        page.evaluate("""() => {
                            const key = document.querySelector('.cfg-key[data-code="Escape"]');
                            if (key) key.click();
                        }""")

                elif i < 1500:
                    # Glide to modal close button
                    prog = (i - 1440) / 60.0
                    cur_x = lerp(800, 1546, ease_in_out_sine(prog))
                    cur_y = lerp(495, 136, ease_in_out_sine(prog))
                    clicking = (1488 <= i <= 1495)

                    if i == 1490 and not studio_closed:
                        page.evaluate("""() => {
                            const closeBtn = document.querySelector('.btn-close-configurator');
                            if (closeBtn) closeBtn.click();
                        }""")
                        studio_closed = True

                else:
                    # Modal fade finishes, cursor returns to center
                    prog = (i - 1500) / 60.0
                    cur_x = lerp(1546, 960, ease_in_out_sine(prog))
                    cur_y = lerp(136, 540, ease_in_out_sine(prog))
                    clicking = False

            # -------------------------------------------------------------
            # STAGE 5: Frames 1560..1800 (26.0s – 30.0s) — Return to Top of Page
            # -------------------------------------------------------------
            else:
                if i < 1740:
                    prog = (i - 1560) / 180.0
                    eased = ease_in_out_cubic(prog)
                    scrollY = (1.0 - eased) * 2950.0
                    hero_frame = 55.0 - eased * (55.0 - 14.0)
                    cur_x = lerp(960, 1020, prog)
                    cur_y = lerp(540, 460, prog)
                else:
                    scrollY = 0.0
                    hero_frame = 14.0
                    prog = (i - 1740) / 60.0
                    cur_x = lerp(1020, 960, prog)
                    cur_y = lerp(460, 480, prog)

                clicking = False

            # Synchronize page scroll & hero 3D camera
            page.evaluate(f"""() => {{
                window.scrollTo(0, {int(round(scrollY))});
                if (window.__novaHero) {{
                    window.__novaHero.setFrame({hero_frame:.2f});
                }}
                if (window.__updateDemoCursor) {{
                    window.__updateDemoCursor({cur_x:.1f}, {cur_y:.1f}, {'true' if clicking else 'false'});
                }}
            }}""")

            # Move mouse natively for CSS :hover feedback and trigger :active states
            page.mouse.move(cur_x, cur_y)
            if clicking:
                page.mouse.down()
            else:
                page.mouse.up()

            # Capture frame and pipe to FFmpeg
            frame_bytes = page.screenshot(type="jpeg", quality=95)
            ffmpeg_proc.stdin.write(frame_bytes)

            if i % 120 == 0 or i == TOTAL_FRAMES - 1:
                elapsed = time.time() - t_start
                rate = (i + 1) / max(0.01, elapsed)
                sec_point = i / FPS
                print(f"  Frame {i:4d}/{TOTAL_FRAMES} ({sec_point:4.1f}s) | scrollY={int(scrollY):4d}px | 3D={hero_frame:4.1f} | {rate:4.1f} fps", flush=True)

        browser.close()

    # Finish FFmpeg encoding
    print("\nClosing FFmpeg input pipe and waiting for encoding...", flush=True)
    ffmpeg_proc.stdin.close()
    _, stderr_data = ffmpeg_proc.communicate()
    stderr_out = stderr_data.decode('utf-8', errors='ignore') if stderr_data else ""

    if ffmpeg_proc.returncode != 0:
        print("FFmpeg encoding failed!\nError:", stderr_out, flush=True)
        sys.exit(1)

    # Copy to kwork_portfolio
    shutil.copy2(OUT_REVIEW, OUT_KWORK)

    # Inspect results
    duration, size_bytes = get_video_info(OUT_KWORK)
    size_mb = size_bytes / (1024 * 1024)

    print("\n" + "=" * 72, flush=True)
    print(" SHOWCASE VIDEO GENERATION COMPLETE", flush=True)
    print("=" * 72, flush=True)
    print(f" File 1: {OUT_KWORK}", flush=True)
    print(f" File 2: {OUT_REVIEW}", flush=True)
    print(f" Resolution: {TARGET_W}x{TARGET_H} (Full HD, 60 FPS)", flush=True)
    print(f" Duration:   {duration:.2f} seconds", flush=True)
    print(f" File Size:  {size_mb:.2f} MB ({size_bytes:,} bytes)", flush=True)
    print(f" Limit (<50MB): {'[PASSED]' if size_mb < 50 else '[FAILED]'}", flush=True)
    print("=" * 72, flush=True)

if __name__ == "__main__":
    main()
