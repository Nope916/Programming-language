import pygame
import random
import sys
import os

# 初始化 Pygame
pygame.init()

# 設置遊戲視窗
width, height = 600, 450  # 調整為 block_size (15) 的倍數
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# 定義顏色
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
gray = (150, 150, 150)

# 定義方塊大小
block_size = 15

# 載入背景圖片
background_normal = pygame.image.load("grass.png")  # 普通模式背景
background_hard = pygame.image.load("hell.png")     # 困難模式背景
snake_logo = pygame.image.load("snake.png").convert_alpha()  # 遊戲標誌

# 調整背景大小以適配螢幕
background_normal = pygame.transform.scale(background_normal, (width, height))
background_hard = pygame.transform.scale(background_hard, (width, height))

# 遊戲字體設定
font = pygame.font.SysFont("Arial", 30)
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# 定義按鈕屬性
button_width, button_height = 200, 50

# 主選單按鈕
practice_button = pygame.Rect(200, 100, button_width, button_height)
normal_button = pygame.Rect(200, 180, button_width, button_height)
hard_button = pygame.Rect(200, 260, button_width, button_height)

# 遊戲結束畫面按鈕
retry_button = pygame.Rect(200, 150, button_width, button_height)
quit_button = pygame.Rect(200, 250, button_width, button_height)
menu_button = pygame.Rect(200, 350, button_width, button_height)
resume_button = pygame.Rect(200, 120, button_width, button_height)
pause_retry_button = pygame.Rect(200, 200, button_width, button_height)
pause_menu_button = pygame.Rect(200, 280, button_width, button_height)

# 全局動畫狀態
Length_of_snake = 0
animation_active = False
fragments = []
animation_color = None
animation_frames_left = 0

LEADERBOARD_FILE = "leaderboard.txt"

# 排行榜相關功能
def load_leaderboard(difficulty):
    """載入指定難度的排行榜資料，練習模式不記錄"""
    file_name = f"leaderboard_{difficulty}.txt"
    if difficulty == "practice":
        return []
    if not os.path.exists(file_name):
        return []
    with open(file_name, "r") as f:
        scores = [line.strip().split(",") for line in f.readlines()]
        return sorted([(int(score), name) for score, name in scores], reverse=True)[:5]

def save_score(score, difficulty, name="Player"):
    """儲存新得分到排行榜檔案，練習模式不儲存"""
    file_name = f"leaderboard_{difficulty}.txt"
    if difficulty == "practice":
        if os.path.exists(file_name):
            os.remove(file_name)
        return
    scores = load_leaderboard(difficulty)
    scores.append((score, name))
    scores = sorted(scores, reverse=True)[:5]
    with open(file_name, "w") as f:
        for s, n in scores:
            f.write(f"{s},{n}\n")

def display_leaderboard(difficulty):
    """顯示指定模式的排行榜，數字對齊"""
    leaderboard = load_leaderboard(difficulty)
    draw_background(difficulty)
    message(f"Leaderboard - {difficulty.capitalize()} Mode", white, 50 - height // 3)
    leaderboard_x, leaderboard_y = 80, 100
    monospaced_font = pygame.font.SysFont("Courier", 25)
    y_offset = leaderboard_y
    for i, (score, name) in enumerate(leaderboard):
        rank = f"{i+1}.".rjust(3)
        text = monospaced_font.render(f"{rank} {name}: {score}", True, white)
        window.blit(text, (leaderboard_x, y_offset))
        y_offset += 30
    pygame.display.update()

# 繪製背景
def draw_background(difficulty):
    """根據難度繪製對應的背景"""
    if difficulty == "practice":
        window.fill(black)
    elif difficulty == "normal":
        window.blit(background_normal, (0, 0))
    elif difficulty == "hard":
        window.blit(background_hard, (0, 0))

# 遊戲暫停功能
def pause_game(difficulty):
    paused = True
    while paused:
        draw_background(difficulty)
        message("Game Paused", white, -100)
        draw_button(resume_button, "Resume")
        draw_button(pause_retry_button, "Retry")
        draw_button(pause_menu_button, "Main Menu")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    paused = False
                elif pause_retry_button.collidepoint(event.pos):
                    gameLoop(difficulty)
                elif pause_menu_button.collidepoint(event.pos):
                    main_menu()

# 繪製按鈕
def draw_button(button, text, bg_color=white):
    pygame.draw.rect(window, bg_color, button)
    pygame.draw.rect(window, black, button, 5)
    label = font.render(text, True, black)
    window.blit(label, (button.x + (button.width - label.get_width()) // 2,
                        button.y + (button.height - label.get_height()) // 2))

# 顯示分數
def Your_score(score):
    value = score_font.render("Score: " + str(score), True, white)
    window.blit(value, [10, 10])

# 顯示訊息
def message(msg, color, y_offset=0):
    mesg = font_style.render(msg, True, color)
    text_rect = mesg.get_rect(center=(width // 2, height // 3 + y_offset))
    window.blit(mesg, text_rect)

# 繪製障礙物
def draw_obstacles(obstacles):
    for ob in obstacles:
        pygame.draw.rect(window, red, [ob[0], ob[1], block_size, block_size])

# 繪製蛇
def draw_snake(snake_list):
    for x in snake_list:
        pygame.draw.rect(window, green, [x[0], x[1], block_size, block_size])

# 遊戲結束畫面
def game_over_screen(difficulty):
    global Length_of_snake
    player_score = Length_of_snake - 4
    name = "Player"

    if difficulty != "practice":
        input_active = True
        user_text = ""
        while input_active:
            draw_background(difficulty)
            message("You Lost!", red, -120)
            text_surface = font_style.render("Enter your name: " + user_text, True, white)
            window.blit(text_surface, (width // 4, height // 2))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        name = user_text if user_text else "Player"
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode
    else:
        name = "Practice Mode"

    # 調整按鈕位置
    if difficulty == "practice":
        button_x = (width - button_width) // 2
        retry_y, quit_y, menu_y = height // 2 - 30, height // 2 + 30, height // 2 + 90
    else:
        button_x, retry_y, quit_y, menu_y = 350, 150, 250, 350

    retry_button.update(button_x, retry_y, button_width, button_height)
    quit_button.update(button_x, quit_y, button_width, button_height)
    menu_button.update(button_x, menu_y, button_width, button_height)

    save_score(player_score, difficulty, name)

    while True:
        draw_background(difficulty)
        if difficulty != "practice":
            message(f"Leaderboard - {difficulty.capitalize()} Mode", white, 30 - height // 3)
            leaderboard_x, leaderboard_y = 80, 100
            leaderboard = load_leaderboard(difficulty)
            y_offset = leaderboard_y
            for i, (score, name) in enumerate(leaderboard):
                text = font_style.render(f"{i+1}. {name}: {score}", True, white)
                window.blit(text, (leaderboard_x, y_offset))
                y_offset += 30
        message("You Lost!", red, -50)
        draw_button(retry_button, "Retry")
        draw_button(quit_button, "Quit")
        draw_button(menu_button, "Main Menu")
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    gameLoop(difficulty)
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif menu_button.collidepoint(event.pos):
                    main_menu()

# 主選單畫面
def main_menu():
    while True:
        window.fill(black)
        logo_x = (width - snake_logo.get_width()) // 2
        logo_y = 20
        window.blit(snake_logo, (logo_x, logo_y))
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

# 遊戲主迴圈
def gameLoop(difficulty):
    global Length_of_snake, animation_active, fragments, animation_color, animation_frames_left

    game_over = False
    x1 = width / 2
    y1 = height / 2
    x1_change = block_size
    y1_change = 0

    # 初始化蛇的位置
    snake_List = [[x1 - (3 * block_size), y1], [x1 - (2 * block_size), y1], [x1 - block_size, y1], [x1, y1]]
    Length_of_snake = 4

    # 隨機生成食物位置
    foodx = round(random.randrange(0, width - block_size) / block_size) * block_size
    foody = round(random.randrange(0, height - block_size) / block_size) * block_size

    # 根據難度設置障礙物數量
    max_obstacles = 10 if difficulty == "normal" else 20 if difficulty == "hard" else 0
    obstacles = []
    num_obstacles = 5 if difficulty == "normal" else 10 if difficulty == "hard" else 0

    # 生成障礙物的函數
    def generate_obstacle():
        quadrants = {
            "TL": (0, width // 2, 0, height // 2),
            "TR": (width // 2, width, 0, height // 2),
            "BL": (0, width // 2, height // 2, height),
            "BR": (width // 2, width, height // 2, height),
        }
        quadrant_counts = {key: 0 for key in quadrants}
        for obx, oby in obstacles:
            for q, (x_min, x_max, y_min, y_max) in quadrants.items():
                if x_min <= obx < x_max and y_min <= oby < y_max:
                    quadrant_counts[q] += 1
        unfilled_quadrants = [q for q, count in quadrant_counts.items() if count == 0]
        if unfilled_quadrants:
            selected_quadrant = random.choice(unfilled_quadrants)
        else:
            min_count = min(quadrant_counts.values())
            least_filled_quadrants = [q for q, count in quadrant_counts.items() if count == min_count]
            selected_quadrant = random.choice(least_filled_quadrants)
        x_min, x_max, y_min, y_max = quadrants[selected_quadrant]
        while True:
            obx = round(random.randrange(x_min, x_max - block_size) / block_size) * block_size
            oby = round(random.randrange(y_min, y_max - block_size) / block_size) * block_size
            if [obx, oby] not in snake_List and [obx, oby] not in obstacles and (obx != foodx or oby != foody):
                obstacles.append([obx, oby])
                break

    for _ in range(num_obstacles):
        generate_obstacle()

    # 設置邊界類型
    border_type = random.choice(["top-bottom", "left-right"]) if difficulty == "normal" else "all"

    # 控制遊戲速度與渲染
    clock = pygame.time.Clock()
    game_speed = 10
    render_speed = 120
    time_since_last_update = 0.0

    # 重置動畫狀態
    animation_active = False
    fragments = []
    animation_color = None
    animation_frames_left = 0

    # 設定分數上限
    score_limit = 10 if difficulty == "practice" else 999

    # 繪製邊界線
    def draw_border_lines():
        if difficulty == "normal":
            if border_type == "top-bottom":
                pygame.draw.line(window, red, (0, 0), (width, 0), 2)
                pygame.draw.line(window, red, (0, height - 2), (width, height - 2), 2)
            else:
                pygame.draw.line(window, red, (0, 0), (0, height), 2)
                pygame.draw.line(window, red, (width - 2, 0), (width - 2, height), 2)
        elif difficulty == "hard":
            pygame.draw.line(window, red, (0, 0), (width, 0), 2)
            pygame.draw.line(window, red, (0, height - 2), (width, height - 2), 2)
            pygame.draw.line(window, red, (0, 0), (0, height), 2)
            pygame.draw.line(window, red, (width - 2, 0), (width - 2, height), 2)

    # 遊戲主迴圈
    while not game_over or animation_frames_left > 0:
        dt = clock.tick(render_speed) / 1000.0
        time_since_last_update += dt

        # 處理事件
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
                elif event.key == pygame.K_ESCAPE:
                    pause_game(difficulty)

        if not game_over:
            while time_since_last_update >= 1 / game_speed:
                x1 += x1_change
                y1 += y1_change

                # 處理不同難度的邊界碰撞
                if difficulty == "hard":
                    if x1 < 0 or x1 >= width or y1 < 0 or y1 >= height:
                        animation_active = True
                        animation_color = white if difficulty == "hard" else red
                        animation_frames_left = 30
                        fragments = []
                        for _ in range(60):
                            angle = random.uniform(0, 360)
                            speed = random.uniform(5, 15)
                            dx = speed * pygame.math.Vector2(1, 0).rotate(angle).x
                            dy = speed * pygame.math.Vector2(1, 0).rotate(angle).y
                            fragments.append([x1 + block_size // 2, y1 + block_size // 2, dx, dy])
                        game_over = True
                elif difficulty == "normal":
                    if border_type == "top-bottom":
                        if y1 < 0 or y1 >= height:
                            animation_active = True
                            animation_color = red
                            animation_frames_left = 30
                            fragments = []
                            for _ in range(60):
                                angle = random.uniform(0, 360)
                                speed = random.uniform(5, 15)
                                dx = speed * pygame.math.Vector2(1, 0).rotate(angle).x
                                dy = speed * pygame.math.Vector2(1, 0).rotate(angle).y
                                fragments.append([x1 + block_size // 2, y1 + block_size // 2, dx, dy])
                            game_over = True
                        else:
                            if x1 < 0:
                                x1 = width - block_size
                            elif x1 >= width:
                                x1 = 0
                    elif border_type == "left-right":
                        if x1 < 0 or x1 >= width:
                            animation_active = True
                            animation_color = red
                            animation_frames_left = 30
                            fragments = []
                            for _ in range(60):
                                angle = random.uniform(0, 360)
                                speed = random.uniform(5, 15)
                                dx = speed * pygame.math.Vector2(1, 0).rotate(angle).x
                                dy = speed * pygame.math.Vector2(1, 0).rotate(angle).y
                                fragments.append([x1 + block_size // 2, y1 + block_size // 2, dx, dy])
                            game_over = True
                        else:
                            if y1 < 0:
                                y1 = height - block_size
                            elif y1 >= height:
                                y1 = 0
                else:  # 練習模式
                    if x1 < 0:
                        x1 = width - block_size
                    elif x1 >= width:
                        x1 = 0
                    if y1 < 0:
                        y1 = height - block_size
                    elif y1 >= height:
                        y1 = 0

                # 更新蛇的位置
                snake_Head = [x1, y1]
                snake_List.append(snake_Head)
                if len(snake_List) > Length_of_snake:
                    del snake_List[0]

                # 檢查是否撞到自己或障礙物
                if snake_Head in snake_List[:-1] or [x1, y1] in obstacles:
                    animation_active = True
                    animation_color = white if difficulty == "hard" else red
                    animation_frames_left = 30
                    fragments = []
                    for _ in range(60):
                        angle = random.uniform(0, 360)
                        speed = random.uniform(5, 15)
                        dx = speed * pygame.math.Vector2(1, 0).rotate(angle).x
                        dy = speed * pygame.math.Vector2(1, 0).rotate(angle).y
                        fragments.append([x1 + block_size // 2, y1 + block_size // 2, dx, dy])
                    game_over = True

                # 檢查是否吃到食物
                if x1 == foodx and y1 == foody:
                    Length_of_snake += 1
                    if (Length_of_snake - 4) % 5 == 0 and len(obstacles) < max_obstacles:
                        num_new_obstacles = 1 if difficulty == "normal" else 2
                        for _ in range(num_new_obstacles):
                            generate_obstacle()
                    animation_active = True
                    animation_color = blue
                    animation_frames_left = 30
                    fragments = []
                    for _ in range(30):
                        angle = random.uniform(0, 360)
                        speed = random.uniform(5, 15)
                        dx = speed * pygame.math.Vector2(1, 0).rotate(angle).x
                        dy = speed * pygame.math.Vector2(1, 0).rotate(angle).y
                        fragments.append([foodx + block_size // 2, foody + block_size // 2, dx, dy])
                    foodx = round(random.randrange(0, width - block_size) / block_size) * block_size
                    foody = round(random.randrange(0, height - block_size) / block_size) * block_size

                time_since_last_update -= 1 / game_speed

        # 繪製遊戲畫面
        draw_background(difficulty)
        draw_border_lines()
        draw_snake(snake_List)
        draw_obstacles(obstacles)
        pygame.draw.circle(window, blue, [foodx + block_size // 2, foody + block_size // 2], block_size // 2)
        Your_score(Length_of_snake - 4)

        # 處理動畫效果
        if animation_frames_left > 0:
            for fragment in fragments:
                fragment[0] += fragment[2]
                fragment[1] += fragment[3]
                pygame.draw.circle(window, animation_color, (int(fragment[0]), int(fragment[1])), 3)
            animation_frames_left -= 1

        pygame.display.update()

    if game_over:
        game_over_screen(difficulty)

# 程式入口
if __name__ == "__main__":
    main_menu()
