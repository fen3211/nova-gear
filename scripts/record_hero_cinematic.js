const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

async function recordHeroDemo() {
  const tmpVideoDir = path.resolve(__dirname, '../review/temp_video');
  fs.mkdirSync(tmpVideoDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    recordVideo: {
      dir: tmpVideoDir,
      size: { width: 1440, height: 900 }
    }
  });

  const page = await context.newPage();
  await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));

  const fileUrl = 'file:///' + path.resolve(__dirname, '../index.html').replace(/\\/g, '/');
  console.log('Navigating to', fileUrl);
  await page.goto(fileUrl);
  await page.waitForLoadState('networkidle');

  // 1. Observe Intro Fly-in (Frame 0 -> 14) and Spring Reveal of Pins
  console.log('Waiting for intro fly-in...');
  await page.waitForTimeout(1400);

  // 2. Perform smooth scroll down the 250vh Hero track
  const track = page.locator('#heroScrollTrack');
  const trackBox = await track.boundingBox();
  const maxScroll = trackBox ? trackBox.height - 900 : 1800;

  console.log('Scrubbing hero track smoothly...');
  const stepsDown = 45;
  for (let i = 1; i <= stepsDown; i++) {
    const progress = i / stepsDown;
    const y = maxScroll * progress;
    await page.evaluate((top) => window.scrollTo(0, top), y);
    await page.waitForTimeout(45);
  }

  // Settle at final beauty angle
  await page.waitForTimeout(600);

  // 3. Reverse scrub back to top
  console.log('Reverse scrubbing back to top...');
  const stepsUp = 35;
  for (let i = 1; i <= stepsUp; i++) {
    const progress = 1 - (i / stepsUp);
    const y = maxScroll * progress;
    await page.evaluate((top) => window.scrollTo(0, top), y);
    await page.waitForTimeout(40);
  }

  // Settle back at resting hero frame
  await page.waitForTimeout(800);

  await context.close();
  await browser.close();

  // Find recorded webm file
  const videoFiles = fs.readdirSync(tmpVideoDir).filter(f => f.endsWith('.webm'));
  if (videoFiles.length > 0) {
    const rawWebm = path.join(tmpVideoDir, videoFiles[0]);
    const finalMp4 = path.resolve(__dirname, '../review/hero_cinematic_demonstration.mp4');
    console.log(`Converting ${rawWebm} -> ${finalMp4}...`);
    try {
      execSync(`ffmpeg -y -i "${rawWebm}" -c:v libx264 -pix_fmt yuv420p -crf 20 -preset fast -movflags +faststart "${finalMp4}"`, { stdio: 'inherit' });
      console.log('Video saved successfully!');
    } catch (err) {
      console.error('FFmpeg conversion error:', err);
    }
    // Clean up temp dir
    try {
      fs.rmSync(tmpVideoDir, { recursive: true, force: true });
    } catch (e) {}
  }
}

recordHeroDemo().catch(console.error);
