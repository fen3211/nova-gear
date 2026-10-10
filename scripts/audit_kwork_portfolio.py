import os
from PIL import Image

portfolio_dir = "kwork_portfolio"
works = sorted([d for d in os.listdir(portfolio_dir) if os.path.isdir(os.path.join(portfolio_dir, d))])

print("=" * 75)
print("KWORK PORTFOLIO AUDIT REPORT")
print("=" * 75)

total_ok = True
for idx, w in enumerate(works, 1):
    wdir = os.path.join(portfolio_dir, w)
    files = sorted(os.listdir(wdir))
    
    title_path = os.path.join(wdir, "title.txt")
    title = ""
    if os.path.exists(title_path):
        with open(title_path, "r", encoding="utf-8") as f:
            title = f.read().strip()
            
    t_len = len(title)
    t_status = "OK" if t_len <= 40 else "FAIL (>40)"
    if t_len > 40:
        total_ok = False
    
    print(f"\n[{idx}] {w}")
    print(f"    Title: \"{title}\" ({t_len} chars, limit <= 40) [{t_status}]")
    
    for fn in files:
        fpath = os.path.join(wdir, fn)
        sz = os.path.getsize(fpath)
        if fn.endswith(".jpg"):
            with Image.open(fpath) as im:
                sz_kb = sz / 1024
                res_ok = (im.size == (1920, 1280))
                sz_ok = (300 <= sz_kb <= 3072)
                f_ok = res_ok and sz_ok
                if not f_ok:
                    total_ok = False
                status = "OK" if f_ok else f"FAIL (res={im.size}, sz={sz_kb:.1f}KB)"
                print(f"    - {fn:10s} : {im.size[0]}x{im.size[1]} | {sz_kb:6.1f} KB [{status}]")
        elif fn.endswith(".mp4"):
            sz_mb = sz / (1024 * 1024)
            v_ok = (sz_mb <= 50)
            if not v_ok:
                total_ok = False
            status = "OK" if v_ok else f"FAIL ({sz_mb:.1f}MB > 50MB)"
            print(f"    - {fn:10s} : MP4 Video | {sz_mb:6.2f} MB [{status}]")
        else:
            print(f"    - {fn:10s} : Metadata  | {sz} bytes")

print("\n" + "=" * 75)
if total_ok:
    print("ALL KWORK PORTFOLIO CRITERIA FULLY SATISFIED (100% PASS)")
else:
    print("AUDIT FAILED")
print("=" * 75)
