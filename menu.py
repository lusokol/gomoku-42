import pygame
from game import Game
import config
from utile import placeButtonAtPercent, draw_text_centered, draw_gomoku_board, draw_end_game_screen

def updateScreenSize(width, height, isFullScreen):
    config.SCREEN_HEIGHT = height
    config.SCREEN_WIDTH = width

    config.HPC = config.SCREEN_HEIGHT / 100
    config.WPC = config.SCREEN_WIDTH // 3 / 100
    if (isFullScreen):
        return pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.FULLSCREEN), pygame.font.SysFont('Comic Sans MS', int(config.SCREEN_WIDTH * 0.026)), pygame.font.SysFont('Comic Sans MS', int(config.SCREEN_WIDTH * 0.017))
    else:
        return pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT)), pygame.font.SysFont('Comic Sans MS', int(config.SCREEN_WIDTH * 0.026)), pygame.font.SysFont('Comic Sans MS', int(config.SCREEN_WIDTH * 0.017))

def getMenu(title_font, pos, logo, button_texts):
    button_surface = pygame.Surface((config.SCREEN_WIDTH // 3, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    button_surface.fill(config.COLOR_MENU)

    # Boutons avec texte centré
    if len(button_texts) == 1:
        button_rects = [placeButtonAtPercent(80)]
    else:
        button_rects = [placeButtonAtPercent(40 + (15*x)) for x in range(len(button_texts))]
    mouseOn = "none"

    for rect, text in zip(button_rects, button_texts):
        button_color = config.COLOR_BUTTON
        if rect.collidepoint(pos):
            button_color = config.COLOR_BUTTON_HOVER
            mouseOn = text
        pygame.draw.rect(button_surface, button_color, rect)
        draw_text_centered(button_surface, text, title_font, (255, 255, 255), rect)
    image_rect = logo.get_rect(center=(config.WPC * 50, config.HPC * 20))
    button_surface.blit(logo, image_rect)

    return button_surface, mouseOn

def main():
    # init de pygame
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    # choix de font et création de la fenetre
    infoObject = pygame.display.Info()
    screen, title_font, little_font = updateScreenSize(infoObject.current_w, infoObject.current_h, True)

    # Creation du rectangle contenant la surface de jeu (partie droite de l'ecran)
    game_surface = pygame.Surface((config.SCREEN_WIDTH // 3 * 2, config.SCREEN_HEIGHT), pygame.SRCALPHA)

    # Chargement de l'arriere plan 
    background_img = pygame.image.load("./images/bois bg.jpg").convert()
    background_img = pygame.transform.scale(background_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    # Chargement du logo, scale a la bonne taille en conservant le ratio HEIGHT/WIDTH
    logo = pygame.image.load("./images/logo gomoku.png")
    aspect_ratio = logo.get_height() / logo.get_width()
    newH = 30 * config.HPC
    newW =  newH / aspect_ratio
    logo = pygame.transform.scale(logo, (newW, newH))

    # HUD sur la gauche
    hud_left = pygame.Surface((config.SCREEN_WIDTH // 3, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    hud_left.fill(config.COLOR_MENU)
    image_rect = logo.get_rect(center=(config.WPC * 50, config.HPC * 20))
    hud_left.blit(logo, image_rect)


    # noms des bouttons du menu
    menu_accueil = ["JOUER", "OPTIONS", "QUITTER"]
    menu_jouer = ["SOLO", "PARTIE LOCAL", "RETOUR"]
    menu_option = ["PLEIN ECRAN", "FENÊTRÉ", "RETOUR"]
    menu_fenetre = ["1280X720", "1600X900", "1920X1080", "RETOUR"]
    menu_ingame = ["RETOUR"]

    menu_actif = menu_accueil
    run = True
    
    game = Game()
    # Boucle principale du jeu
    while run:
        clock.tick(60) # 60 fps max
        pos = pygame.mouse.get_pos()

        # necessaire uniquement lors d'un changement de taille de screen mais se fait a tous les ticks pour le moment (à changer?)
        screen.blit(background_img, (0, 0))
        newH = 30 * config.HPC
        newW =  newH / aspect_ratio
        logo = pygame.transform.scale(logo, (newW, newH))
        game_surface = pygame.Surface((config.SCREEN_WIDTH // 3 * 2, config.SCREEN_HEIGHT), pygame.SRCALPHA)

        # creation du menu
        mouseOn = "none"

        if menu_actif != "none":
            menu_surface, mouseOn = getMenu(title_font, pos, logo, menu_actif)

        # gestion des events
        clickedOutside = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pos[0] > config.SCREEN_WIDTH // 3:
                    clickedOutside = True
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
                elif mouseOn == "FENÊTRÉ":
                    menu_actif = menu_fenetre
                elif mouseOn == "1280X720":
                    screen, title_font, little_font = updateScreenSize(1280, 720, False)
                elif mouseOn == "1600X900":
                    screen, title_font, little_font = updateScreenSize(1600, 900, False)
                elif mouseOn == "1920X1080":
                    screen, title_font, little_font = updateScreenSize(1920, 1080, False)
                elif mouseOn == "RETOUR":
                    if menu_actif == menu_fenetre:
                        menu_actif = menu_option
                    else:
                        menu_actif = menu_accueil
                    game.reset()
            if event.type == pygame.QUIT:
                run = False

        # affiche le plateau du jeu dans la grande zone
        if menu_actif == menu_ingame:
            gameState = draw_gomoku_board(screen, game_surface, game, pos, clickedOutside)
            screen.blit(game_surface, ((config.SCREEN_WIDTH // 3, 0)))
            game.dispInfoOn(menu_surface, little_font)
            screen.blit(menu_surface, (0, 0))
            if (game.inGame == False):
                draw_end_game_screen(screen, game)
        if menu_actif != menu_ingame:
            screen.blit(menu_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
