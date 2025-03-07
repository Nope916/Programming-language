import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Set up game window
width, height = 600, 450  # Adjusted to be divisible by block_size (15)
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
gray = (150, 150, 150)

# Define block size
block_size = 15

# Game fonts
font = pygame.font.SysFont("Arial", 30)
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# Define button properties
button_width, button_height = 200, 50

# Buttons for the main menu
practice_button = pygame.Rect(200, 100, button_width, button_height)
normal_button = pygame.Rect(200, 180, button_width, button_height)
hard_button = pygame.Rect(200, 260, button_width, button_height)

# Buttons for the game over screen
retry_button = pygame.Rect(200, 150, button_width, button_height)
quit_button = pygame.Rect(200, 250, button_width, button_height)

def draw_button(button, text, bg_color=white):
    pygame.draw.rect(window, bg_color, button)
    pygame.draw.rect(window, black, button, 5)  # Border
    label = font.render(text, True, black)
    window.blit(label, (button.x + (button.width - label.get_width()) // 2,
                        button.y + (button.height - label.get_height()) // 2))

def Your_score(score):
    value = score_font.render("Your Score: " + str(score), True, white)
    window.blit(value, [10, 10])

def message(msg, color, y_offset=0):
    mesg = font_style.render(msg, True, color)
    text_rect = mesg.get_rect(center=(width // 2, height // 3 + y_offset))
    window.blit(mesg, text_rect)


def draw_obstacles(obstacles):
    for ob in obstacles:
        pygame.draw.rect(window, red, [ob[0], ob[1], block_size, block_size])

def draw_snake(snake_list):
    for x in snake_list:
        pygame.draw.rect(window, green, [x[0], x[1], block_size, block_size])

# Food explosion effect
def fractured_animation(x, y, color, num_pieces=50):
    """Creates a fractured animation when food is eaten or snake dies."""
    fragments = []
    clock = pygame.time.Clock()

    # Generate a large number of small pieces
    for _ in range(num_pieces):
        angle = random.uniform(0, 360)
        speed = random.uniform(2, 7)  # Faster effect
        dx = speed * pygame.math.Vector2(1, 0).rotate(angle).x
        dy = speed * pygame.math.Vector2(1, 0).rotate(angle).y
        fragments.append([x + block_size // 2, y + block_size // 2, dx, dy])

    for _ in range(15):  # Run animation for more frames
        window.fill(black)
        Your_score(Length_of_snake - 4)  # Keep the score displayed

        # Draw fragment pieces
        for fragment in fragments:
            fragment[0] += fragment[2]  # Move x position
            fragment[1] += fragment[3]  # Move y position
            pygame.draw.circle(window, color, (int(fragment[0]), int(fragment[1])), 2)  

        pygame.display.update()
        clock.tick(60)



def game_over_screen(difficulty):
    """Displays the game over screen with Retry and Quit buttons"""
    while True:
        window.fill(black)
        message("You Lost!", red, -50)
        Your_score(Length_of_snake - 4)

        # Draw buttons
        draw_button(retry_button, "Retry")
        draw_button(quit_button, "Quit")

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    gameLoop(difficulty)  # Restart game
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def gameLoop(difficulty):
    global Length_of_snake

    game_over = False

    x1 = width / 2
    y1 = height / 2
    x1_change = block_size
    y1_change = 0

    snake_List = [[x1 - (3 * block_size), y1], [x1 - (2 * block_size), y1], [x1 - block_size, y1], [x1, y1]]
    Length_of_snake = 4

    foodx = round(random.randrange(0, width - block_size) / block_size) * block_size
    foody = round(random.randrange(0, height - block_size) / block_size) * block_size

    obstacles = []
    num_obstacles = 5 if difficulty == "normal" else 10 if difficulty == "hard" else 0

    while num_obstacles > 0:
        obx = round(random.randrange(0, width - block_size) / block_size) * block_size
        oby = round(random.randrange(0, height - block_size) / block_size) * block_size
        if [obx, oby] not in snake_List and (obx != foodx or oby != foody):
            obstacles.append([obx, oby])
            num_obstacles -= 1

    clock = pygame.time.Clock()
    snake_speed = 5

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change != block_size:
                    x1_change = -block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change != -block_size:
                    x1_change = block_size
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change != block_size:
                    y1_change = -block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change != -block_size:
                    y1_change = block_size
                    x1_change = 0

        x1 += x1_change
        y1 += y1_change

        if x1 >= width:
            x1 = 0
        elif x1 < 0:
            x1 = width - block_size
        if y1 >= height:
            y1 = 0
        elif y1 < 0:
            y1 = height - block_size

        window.fill(black)
        pygame.draw.circle(window, blue, [foodx + block_size // 2, foody + block_size // 2], block_size // 2)

        snake_Head = [x1, y1]
        snake_List.append(snake_Head)

        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        if snake_Head in snake_List[:-1] or [x1, y1] in obstacles:
            fractured_animation(x1, y1, green, 100)  # Play animation before game over
            game_over_screen(difficulty)


        draw_snake(snake_List)
        draw_obstacles(obstacles)
        Your_score(Length_of_snake - 4)
        pygame.display.update()

        if x1 == foodx and y1 == foody:
            fractured_animation(foodx, foody, snake_List, obstacles, Length_of_snake)
            foodx = round(random.randrange(0, width - block_size) / block_size) * block_size
            foody = round(random.randrange(0, height - block_size) / block_size) * block_size
            Length_of_snake += 1

        clock.tick(snake_speed)


def main_menu():
    while True:
        window.fill(black)
        draw_button(practice_button, "Practice")
        draw_button(normal_button, "Normal")
        draw_button(hard_button, "Hard")

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if practice_button.collidepoint(event.pos):
                    gameLoop("practice")
                elif normal_button.collidepoint(event.pos):
                    gameLoop("normal")
                elif hard_button.collidepoint(event.pos):
                    gameLoop("hard")

main_menu()
