import pygame
import neat
import os

from base import Base
from bird import Bird
from pipe import Pipe

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
SPACE_BETWEEN_PIPES = 700
GROUND_LEVEL = 730

BIRD_SPAWN_X = 230
BIRD_SPAWN_Y = 350

TIMER = 30

BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

FONT = pygame.font.SysFont("comicsans", 45)

score = 0
speed = TIMER


def display_window_solo(window, bird, pipes, base):
    window.blit(BACKGROUND_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(window)

    text = FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    bird.draw(window)

    base.draw(window)
    pygame.display.update()


def display_window_multiple(window, birds, pipes, base):
    window.blit(BACKGROUND_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(window)

    text = FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    text = FONT.render("Bird Number: " + str(len(birds)), 1, (255, 255, 255))
    window.blit(text, (0 - 10, 10))
    text = FONT.render("SPEED: " + str(speed), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 60))
    # DRAW
    for bird in birds:
        bird.draw(window)

    base.draw(window)
    pygame.display.update()


def game_with_genome(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(BIRD_SPAWN_X, BIRD_SPAWN_Y))
        g.fitness = 0
        ge.append(g)

    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    base = Base(GROUND_LEVEL)
    pipes = [Pipe(SPACE_BETWEEN_PIPES)]
    clock = pygame.time.Clock()
    run = True
    global score
    global speed
    score = 0
    while run and len(birds) > 0:
        if speed > 0:
            clock.tick(speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    run = False
                if event.key == pygame.K_z:
                    speed = 0
                if event.key == pygame.K_MINUS or event.key == pygame.K_RIGHT:
                    if speed > 0:
                        speed -= 1
                if event.key == pygame.K_PLUS or event.key == pygame.K_LEFT:
                    if speed < 5000:
                        speed += 1

        pip_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pip_ind = 1
        for x, bird in enumerate(birds):
            ge[x].fitness += 1
            bird.move()
            if len(pipes) > 0:
                output = nets[birds.index(bird)].activate((bird.y, pipes[pip_ind].height, pipes[pip_ind].bottom))
            else:
                output = nets[birds.index(bird)].activate(bird.y, WIN_HEIGHT / 2, WIN_HEIGHT / 2)

            if output[0] > 0.5:
                bird.jump()

        base.move()

        remove_pipes = []
        add_pipe = False

        # PIPE
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)
            pipe.move()
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(SPACE_BETWEEN_PIPES))
        for remove in remove_pipes:
            pipes.remove(remove)

        # GROUND/AIR CHECK
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= GROUND_LEVEL or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        display_window_multiple(window, birds, pipes, base)


def run_game(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(game_with_genome, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat config.txt")
    run_game(config_path)
