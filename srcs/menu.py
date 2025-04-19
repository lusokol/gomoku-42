import pygame
from game import Game
import config
from utile import (
    placeButtonAtPercent,
    draw_text_centered,
    draw_gomoku_board,
    draw_end_game_screen,
    draw_notification,
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

    mouseOn = "none"

    if len(button_texts) == 1:
        button_rects = [placeButtonAtPercent(80)]
    else:
        button_rects = [
            placeButtonAtPercent(40 + (15 * x)) for x in range(len(button_texts))
        ]

    for rect, text in zip(button_rects, button_texts):
        if text in ["MUSIQUE", "EFFETS SONOR"]:
            # Nom centré
            draw_text_centered(button_surface, text, title_font, (255, 255, 255), rect)

            # Boutons - et +
            margin = 10
            side_width = config.HPC * 10
            side_height = rect.height
            left_rect = pygame.Rect(rect.left, rect.top, side_width, side_height)
            right_rect = pygame.Rect(
                rect.right - side_width, rect.top, side_width, side_height
            )

            if left_rect.collidepoint(pos) and not menu_disable:
                pygame.draw.rect(button_surface, config.COLOR_BUTTON_HOVER, left_rect)
                mouseOn = f"{text}-"
            else:
                pygame.draw.rect(button_surface, config.COLOR_BUTTON, left_rect)

            if right_rect.collidepoint(pos) and not menu_disable:
                pygame.draw.rect(button_surface, config.COLOR_BUTTON_HOVER, right_rect)
                mouseOn = f"{text}+"
            else:
                pygame.draw.rect(button_surface, config.COLOR_BUTTON, right_rect)

            draw_text_centered(
                button_surface, "-", title_font, (255, 255, 255), left_rect
            )
            draw_text_centered(
                button_surface, "+", title_font, (255, 255, 255), right_rect
            )

            # Barre de volume
            bar_width = rect.width - 2 * side_width - 2 * margin
            bar_x = rect.left + side_width + margin
            bar_y = rect.bottom - 20  # Position en bas du bouton
            segment_width = bar_width // 10
            segment_height = 5
            volumes = {
                "MUSIQUE": config.sound_manager.music_volume,
                "EFFETS SONOR": config.sound_manager.sounds_volume,
            }
            current_volume = volumes[text]

            for i in range(10):
                seg_color = (255, 255, 255) if i < current_volume else (100, 100, 100)
                pygame.draw.rect(
                    button_surface,
                    seg_color,
                    pygame.Rect(
                        bar_x + i * segment_width,
                        bar_y,
                        segment_width - 2,
                        segment_height,
                    ),
                )

        else:
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
    pygame.mixer.init()
    clock = pygame.time.Clock()

    # === SETUP ECRAN ===
    infoObject = pygame.display.Info()
    # screen, title_font, little_font = updateScreenSize(1280, 720, False)
    screen, title_font, little_font = updateScreenSize(
        infoObject.current_w, infoObject.current_h, True
    )

    def resize_logo():
        newH = 30 * config.HPC
        newW = newH / aspect_ratio
        return pygame.transform.scale(logo_original, (newW, newH))

    def update_assets_after_resize():
        nonlocal logo
        logo = resize_logo()

    # === CHARGEMENT RESSOURCES ===
    background_img = pygame.image.load("./images/bois bg.jpg").convert()
    background_img = pygame.transform.scale(
        background_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    )
    logo_original = pygame.image.load("./images/logo gomoku.png")
    aspect_ratio = logo_original.get_height() / logo_original.get_width()
    logo = resize_logo()

    menus = {
        "accueil": ["JOUER", "OPTIONS", "QUITTER"],
        "jouer": ["SOLO CONTRE L'IA", "PARTIE LOCAL", "RETOUR"],
        "ia": ["FACILE", "MOYEN", "IMPOSSIBLE", "RETOUR"],
        "option": ["AFFICHAGE", "AUDIO", "RETOUR"],
        "audio": ["MUSIQUE", "EFFETS SONOR", "RETOUR"],
        "affichage": ["PLEIN ECRAN", "FENÊTRÉ", "RETOUR"],
        "fenetre": ["1280X720", "1600X900", "1920X1080", "RETOUR"],
        "ingame": ["RETOUR"],
    }

    retour_map = {
        "fenetre": "affichage",
        "affichage": "option",
        "ia": "jouer",
        "jouer": "accueil",
        "option": "accueil",
        "audio": "option",
        "ingame": "accueil",
    }

    menu_actif_id = "accueil"
    menu_actif = menus[menu_actif_id]
    run = True
    game = Game()

    def changeMenu(new_menu_id):
        nonlocal menu_actif_id, menu_actif
        menu_actif_id = new_menu_id
        menu_actif = menus[menu_actif_id]

    def handle_menu_click(mouseOn):
        nonlocal run, screen, title_font, little_font
        if mouseOn == "JOUER":
            changeMenu("jouer")
        elif mouseOn == "OPTIONS":
            changeMenu("option")
        elif mouseOn == "AFFICHAGE":
            changeMenu("affichage")
        elif mouseOn == "AUDIO":
            changeMenu("audio")
        elif mouseOn == "MUSIQUE+":
            config.sound_manager.music_up()
        elif mouseOn == "MUSIQUE-":
            config.sound_manager.music_down()
        elif mouseOn == "EFFETS SONOR+":
            config.sound_manager.sound_up()
        elif mouseOn == "EFFETS SONOR-":
            config.sound_manager.sound_down()
        elif mouseOn == "QUITTER":
            run = False
        elif mouseOn == "SOLO CONTRE L'IA":
            changeMenu("ia")
        elif mouseOn in ["FACILE", "MOYEN", "IMPOSSIBLE"]:
            game.setAIdifficulty(mouseOn)
            changeMenu("ingame")
            game.startAIgame()
        elif mouseOn == "PARTIE LOCAL":
            changeMenu("ingame")
            game.startGame()
        elif mouseOn == "PLEIN ECRAN":
            screen, title_font, little_font = updateScreenSize(
                infoObject.current_w, infoObject.current_h, True
            )
            update_assets_after_resize()
        elif mouseOn == "FENÊTRÉ":
            changeMenu("fenetre")
        elif mouseOn in ["1280X720", "1600X900", "1920X1080"]:
            w, h = map(int, mouseOn.split("X"))
            screen, title_font, little_font = updateScreenSize(w, h, False)
            update_assets_after_resize()
        elif mouseOn == "RETOUR":
            if menu_actif_id == "ingame":
                config.sound_manager.load_music("sounds/menu.ogg")
                config.sound_manager.play_music()
            changeMenu(retour_map.get(menu_actif_id, "accueil"))
            game.reset()

    def draw_game_screen(menu_disable):
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
                handle_menu_click("RETOUR")
            elif endGame_rect["rejouer"] and menu_disable:
                # A GERER ================================================
                handle_menu_click("REJOUER")
                # A GERER ================================================

    config.sound_manager.load_music("sounds/menu.ogg")
    config.sound_manager.play_music()

    # === BOUCLE PRINCIPALE ===
    while run:
        clock.tick(60)
        pos = pygame.mouse.get_pos()
        screen.blit(background_img, (0, 0))

        mouseOn = "none"
        if menu_actif != "none":
            menu_surface, mouseOn = getMenu(
                title_font,
                pos,
                logo,
                menu_actif,
                (menu_actif == menus["ingame"] and not game.inGame),
            )

        menu_disable = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pos[0] > config.SCREEN_WIDTH // 3 or (
                    menu_actif == menus["ingame"] and not game.inGame
                ):
                    menu_disable = True
                else:
                    if mouseOn != "none":
                        config.sound_manager.play_sound("clic")
                    handle_menu_click(mouseOn)
            if event.type == pygame.QUIT:
                run = False

        if menu_actif == menus["ingame"]:
            draw_game_screen(menu_disable)
        else:
            screen.blit(menu_surface, (0, 0))
        draw_notification(screen, little_font)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
