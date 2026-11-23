# 從高解析白底原圖做「只去外部白底」的去背：
# 1) 近白像素中，與圖片邊框連通者 = 背景
# 2) 被角色包圍、但面積大且是純白的封閉區（例如手臂與身體間的空隙）也視為背景
# 3) 邊緣：用「白色程度」算半透明 + 反算顏色去白邊（decontaminate），再縮小
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
def cutout(path, size):
    im = Image.open(path).convert('RGB')
    rgb = np.asarray(im).astype(np.float32)
    H, W = rgb.shape[:2]
    mn = rgb.min(-1); mx = rgb.max(-1); sat = mx - mn
    cand = (mn > 228) & (sat < 22)
    m = Image.fromarray(np.where(cand, 255, 0).astype(np.uint8)).copy()
    # 從邊框種子灌水
    arr = np.asarray(m)
    seeds = [(x, 0) for x in range(W)] + [(x, H-1) for x in range(W)] + [(0, y) for y in range(H)] + [(W-1, y) for y in range(H)]
    for (x, y) in seeds:
        if m.getpixel((x, y)) == 255:
            ImageDraw.floodfill(m, (x, y), 100, thresh=0)
    a = np.asarray(m).copy()
    bg = a == 100
    # 封閉的大塊純白區也當背景：先侵蝕純白遮罩，只有大塊區域會留下種子
    pure = (mn > 247) & (sat < 8) & (a == 255)
    core = np.asarray(Image.fromarray((pure*255).astype(np.uint8)).filter(ImageFilter.MinFilter(15))) > 0
    ys, xs = np.nonzero(core)
    for y, x in zip(ys[::50], xs[::50]):
        if m.getpixel((int(x), int(y))) == 255:
            ImageDraw.floodfill(m, (int(x), int(y)), 60, thresh=0)
    a2 = np.asarray(m)
    reg_all = a2 == 60
    # 逐區檢查純白比例（區域數很少）
    if reg_all.any():
        mm = Image.fromarray(np.where(reg_all, 255, 0).astype(np.uint8)).copy()
        for y, x in zip(*np.nonzero(reg_all)):
            if mm.getpixel((int(x), int(y))) != 255: continue
            ImageDraw.floodfill(mm, (int(x), int(y)), 80, thresh=0)
            reg = np.asarray(mm) == 80
            if reg.sum() > H*W*0.002 and ((mn[reg] > 247) & (sat[reg] < 8)).mean() > 0.85:
                bg |= reg
            mm = Image.fromarray(np.where(reg, 0, np.asarray(mm)).astype(np.uint8)).copy()
    # 邊緣軟化：背景附近 3px 內的近白像素依白色程度給 alpha
    bgimg = Image.fromarray((bg*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
    near = (np.asarray(bgimg) > 0) & ~bg
    alpha = np.where(bg, 0.0, 1.0)
    whiteness = np.clip((mn - 200) / 55.0, 0, 1)
    soft = near & (sat < 40)
    alpha[soft] = 1.0 - whiteness[soft]
    # 去白邊：C = (C - (1-a)*255) / a
    a3 = alpha[..., None]
    dec = np.where(a3 > 0.02, (rgb - (1 - a3) * 255) / np.maximum(a3, 0.02), 0)
    dec = np.clip(dec, 0, 255)
    out = np.dstack([dec, alpha * 255]).astype(np.uint8)
    img = Image.fromarray(out, 'RGBA')
    # 預乘後縮小，避免透明區顏色滲入
    pm = Image.fromarray(np.dstack([dec * alpha[..., None], alpha * 255]).astype(np.uint8), 'RGBA')
    small = np.asarray(pm.resize((size, size), Image.LANCZOS)).astype(np.float32)
    sa = small[..., 3:4] / 255
    col = np.where(sa > 0.004, small[..., :3] / np.maximum(sa, 0.004), 0)
    res = np.dstack([np.clip(col, 0, 255), small[..., 3]]).astype(np.uint8)
    return Image.fromarray(res, 'RGBA')
if __name__ == '__main__':
    src, dst, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
    cutout(src, size).save(dst, optimize=True)
    print('ok', dst)
