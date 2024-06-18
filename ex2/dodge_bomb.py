import os
import random
import sys
import pygame as pg

WIDTH, HEIGHT = 1600, 900
DELTA = {  # 移動量辞書
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect，または，爆弾Rect
    戻り値：真理値タプル（横方向，縦方向）
    画面内ならTrue／画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向判定
        tate = False
    return yoko, tate

def prepare_kk_images(kk_img_original):
    """
    移動量の合計値タプルをキー、rotozoomしたSurfaceを値とする辞書を返す
    """
    kk_images = {
        (0, -5): pg.transform.rotozoom(kk_img_original, 0, 2.0),  # 上
        (0, 5): pg.transform.rotozoom(pg.transform.flip(kk_img_original, False, True), 0, 2.0),  # 下
        (-5, 0): pg.transform.rotozoom(pg.transform.flip(kk_img_original, True, False), 0, 2.0),  # 左
        (5, 0): pg.transform.rotozoom(kk_img_original, 0, 2.0),  # 右
    }
    return kk_images

def prepare_bomb_images_and_accs():
    """
    爆弾の加速度リストと拡大された爆弾画像のリストを返す
    """
    bb_accs = [a for a in range(1, 11)]
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r), pg.SRCALPHA)
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
    return bb_accs, bb_imgs

def show_game_over(screen):
    """
    ゲームオーバー画面を表示する
    """
    black_surface = pg.Surface((WIDTH, HEIGHT))    # ブラックアウト
    black_surface.fill((0, 0, 0))
    black_surface.set_alpha(128)
    screen.blit(black_surface, (0, 0))

    koakoton_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 2.0)  # こうかとん画像
    koakoton_rct_left = koakoton_img.get_rect(center=(WIDTH // 4, HEIGHT // 2))
    koakoton_rct_right = koakoton_img.get_rect(center=(3 * WIDTH // 4, HEIGHT // 2))
    screen.blit(koakoton_img, koakoton_rct_left)
    screen.blit(koakoton_img, koakoton_rct_right)

    font = pg.font.Font(None, 80)  # Game Overの文字表示
    game_over_surf = font.render("Game Over", True, (255, 255, 255))
    game_over_rect = game_over_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(game_over_surf, game_over_rect)

    pg.display.update()
    pg.time.wait(5000)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img_original = pg.image.load("fig/3.png")
    kk_images = prepare_kk_images(kk_img_original)
    kk_img = kk_images[(0, -5)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 900, 400

    bb_accs, bb_imgs = prepare_bomb_images_and_accs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾の横方向速度，縦方向速度

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        if kk_rct.colliderect(bb_rct):  # 衝突判定
            show_game_over(screen)   #ゲームオーバー画面の表示
            return  # ゲームオーバー

        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, v in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += v[0]
                sum_mv[1] += v[1]
        if tuple(sum_mv) in kk_images:
            kk_img = kk_images[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 爆弾の拡大と加速
        idx = min(tmr // 500, 9)
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]

        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向にはみ出たら
            vx *= -1
        if not tate:  # 縦方向にはみ出たら
            vy *= -1
        bb_rct = bb_img.get_rect(center=bb_rct.center)  # 新しいサイズの中心を保持
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()