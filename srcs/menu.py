import pygame
from game import Game
import config
from utile import (
    placeButtonAtPercent,
    draw_text_centered,
    draw_gomoku_board,
    draw_end_game_screen,
)


def updateScreenSize(width, height, isFullScreen):
    config.SCREEN_HEIGHT = height
    config.SCREEN_WIDTH = width

    config.HPC = config.SCREEN_HEIGHT / 100
    config.WPC = config.SCREEN_WIDTH // 3 / 100
    if isFullScreen:
        return (
            pygame.display.set_mode(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.FULLSCREEN
            ),
            pygame.font.SysFont("Comic Sans MS", int(config.SCREEN_WIDTH * 0.026)),
            pygame.font.SysFont("Comic Sans MS", int(config.SCREEN_WIDTH * 0.017)),
        )
    else:
        return (
            pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT)),
            pygame.font.SysFont("Comic Sans MS", int(config.SCREEN_WIDTH * 0.026)),
            pygame.font.SysFont("Comic Sans MS", int(config.SCREEN_WIDTH * 0.017)),
        )


def getMenu(title_font, pos, logo, button_texts, menu_disable):
    button_surface = pygame.Surface(
        (config.SCREEN_WIDTH // 3, config.SCREEN_HEIGHT), pygame.SRCALPHA
    )
    button_surface.fill(config.COLOR_MENU)

    # Boutons avec texte centré
    if len(button_texts) == 1:
        button_rects = [placeButtonAtPercent(80)]
    else:
        button_rects = [
            placeButtonAtPercent(40 + (15 * x)) for x in range(len(button_texts))
        ]
    mouseOn = "none"

    for rect, text in zip(button_rects, button_texts):
        button_color = config.COLOR_BUTTON
        if rect.collidepoint(pos) and not menu_disable:
            button_color = config.COLOR_BUTTON_HOVER
            mouseOn = text
        pygame.draw.rect(button_surface, button_color, rect)
        draw_text_centered(button_surface, text, title_font, (255, 255, 255), rect)
    image_rect = logo.get_rect(center=(config.WPC * 50, config.HPC * 20))
    button_surface.blit(logo, image_rect)

    return button_surface, mouseOn

def main():
    # === INIT ===
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    # === SETUP ECRAN ===
    infoObject = pygame.display.Info()
    screen, title_font, little_font = updateScreenSize(
        infoObject.current_w, infoObject.current_h, True
    )

    def resize_logo():
        newH = 30 * config.HPC
        newW = newH / aspect_ratio
        return pygame.transform.scale(logo_original, (newW, newH))

    def update_assets_after_resize():
        nonlocal screen, title_font, little_font, logo
        logo = resize_logo()

    # === CHARGEMENT RESSOURCES ===
    background_img = pygame.image.load("./images/bois bg.jpg").convert()
    background_img = pygame.transform.scale(
        background_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    )
    logo_original = pygame.image.load("./images/logo gomoku.png")
    aspect_ratio = logo_original.get_height() / logo_original.get_width()
    logo = resize_logo()

    # === MENUS ===
    menu_accueil = ["JOUER", "OPTIONS", "QUITTER"]
    menu_jouer = ["SOLO", "PARTIE LOCAL", "RETOUR"]
    menu_option = ["PLEIN ECRAN", "FENÊTRÉ", "RETOUR"]
    menu_fenetre = ["1280X720", "1600X900", "1920X1080", "RETOUR"]
    menu_ingame = ["RETOUR"]

    menu_actif = menu_accueil
    run = True
    game = Game()

    def handle_click(mouseOn):
        nonlocal run, screen, title_font, little_font, menu_actif
        if menu_actif == menu_ingame and not game.inGame:
            if mouseOn == "accueil":
                game.reset()
                menu_actif = menu_accueil
            elif mouseOn == "rejouer":
                game.reset()
                game.startGame()
                menu_actif = menu_ingame
        elif mouseOn == "JOUER":
            menu_actif = menu_jouer
        elif mouseOn == "OPTIONS":
            menu_actif = menu_option
        elif mouseOn == "QUITTER":
            run = False
        elif mouseOn == "PARTIE LOCAL":
            menu_actif = menu_ingame
            game.startGame()
        elif mouseOn == "PLEIN ECRAN":
            screen, title_font, little_font = updateScreenSize(infoObject.current_w, infoObject.current_h, True)
            update_assets_after_resize()
        elif mouseOn == "FENÊTRÉ":
            menu_actif = menu_fenetre
        elif mouseOn in ["1280X720", "1600X900", "1920X1080"]:
            w, h = map(int, mouseOn.split("X"))
            screen, title_font, little_font = updateScreenSize(w, h, False)
            update_assets_after_resize()
        elif mouseOn == "RETOUR":
            menu_actif = menu_option if menu_actif == menu_fenetre else menu_accueil
            game.reset()

    def draw_game_screen():
        game_surface = pygame.Surface(
            (config.SCREEN_WIDTH // 3 * 2, config.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        draw_gomoku_board(screen, game_surface, game, pos, menu_disable)
        screen.blit(game_surface, ((config.SCREEN_WIDTH // 3, 0)))
        game.dispInfoOn(menu_surface, little_font)
        screen.blit(menu_surface, (0, 0))
        if not game.inGame:
            endGame_rect = draw_end_game_screen(screen, game, title_font, little_font)
            if endGame_rect["accueil"] and menu_disable:
                handle_click("accueil")
            elif endGame_rect["rejouer"] and menu_disable:
                handle_click("rejouer")

    # === BOUCLE PRINCIPALE ===
    while run:
        clock.tick(60)
        pos = pygame.mouse.get_pos()
        screen.blit(background_img, (0, 0))

        mouseOn = "none"
        if menu_actif != "none":
            menu_surface, mouseOn = getMenu(title_font, pos, logo, menu_actif, (menu_actif == menu_ingame and not game.inGame))

        menu_disable = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pos[0] > config.SCREEN_WIDTH // 3 or (menu_actif == menu_ingame and not game.inGame):
                    menu_disable = True
                else:
                    handle_click(mouseOn)
            if event.type == pygame.QUIT:
                run = False

        if menu_actif == menu_ingame:
            draw_game_screen()
        else:
            screen.blit(menu_surface, (0, 0))

        pygame.display.flip()

    pygame.quit()



if __name__ == "__main__":
    main()
