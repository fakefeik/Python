import graphics


def start_game():
    map_file = "configs/mapdefault.txt"
    config = "configs/mapconfig.txt"
    images = "images"
    leaderboard = "configs/leaderboard.txt"
    animated = True
    speed = 5

    graphics.Graphics(map_file=map_file,
                      config=config,
                      images=images,
                      animated=animated,
                      speed=speed,
                      leaderboard=leaderboard)


if __name__ == '__main__':
    start_game()