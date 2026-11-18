import random

COLS = 53
ROWS = 7
CELL = 13
GAP = 3
STEP = CELL + GAP
WIDTH = COLS * STEP + 20
HEIGHT = ROWS * STEP + 36
FPS = 12
MAX_FRAMES = 420

def simulate_game():
    # Start in center
    snake = [(26, 3), (25, 3), (24, 3)]
    direction = (1, 0)
    
    def spawn_food(current_snake):
        empty = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in current_snake]
        return random.choice(empty) if empty else None

    food = spawn_food(snake)
    frames = []
    
    # Welcome screen frames (approx 1.5 seconds)
    for _ in range(18):
        frames.append({
            "state": "WELCOME",
            "snake": list(snake),
            "food": food,
            "score": 0
        })

    score = 0
    for _ in range(MAX_FRAMES):
        head_x, head_y = snake[0]
        
        # Choose smart move toward food while avoiding tail/walls
        possible_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        # Prevent 180-degree reversal
        possible_dirs = [d for d in possible_dirs if (d[0] + direction[0], d[1] + direction[1]) != (0, 0)]
        
        safe_moves = []
        for dx, dy in possible_dirs:
            nx, ny = head_x + dx, head_y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and (nx, ny) not in snake[:-1]:
                dist = abs(nx - food[0]) + abs(ny - food[1]) if food else 0
                safe_moves.append((dist, (dx, dy)))
        
        if not safe_moves:
            # Forced to hit tail or wall -> Game Over
            for _ in range(18):
                frames.append({
                    "state": "GAMEOVER",
                    "snake": list(snake),
                    "food": food,
                    "score": score
                })
            return frames

        # Pick best move (with slight randomness so it eventually traps itself naturally)
        safe_moves.sort(key=lambda x: x[0])
        if random.random() < 0.12 and len(safe_moves) > 1:
            direction = random.choice(safe_moves)[1]
        else:
            direction = safe_moves[0][1]

        new_head = (head_x + direction[0], head_y + direction[1])
        
        # Check tail collision
        if new_head in snake[:-1]:
            for _ in range(18):
                frames.append({
                    "state": "GAMEOVER",
                    "snake": list(snake),
                    "food": food,
                    "score": score
                })
            return frames

        snake.insert(0, new_head)
        if new_head == food:
            score += 1
            food = spawn_food(snake)
            if not food:
                break
        else:
            snake.pop()

        frames.append({
            "state": "PLAY",
            "snake": list(snake),
            "food": food,
            "score": score
        })

    # End loop with Game Over / Restart prompt
    for _ in range(18):
        frames.append({
            "state": "GAMEOVER",
            "snake": list(snake),
            "food": food,
            "score": score
        })
    return frames

def build_svg(frames, dark_mode=False):
    bg_color = "#0d1117" if dark_mode else "#ffffff"
    cell_color = "#161b22" if dark_mode else "#ebedf0"
    snake_head = "#39d353" if dark_mode else "#216e39"
    snake_body = "#26a641" if dark_mode else "#40c463"
    food_color = "#ff6b00"
    text_color = "#c9d1d9" if dark_mode else "#24292f"
    
    total_frames = len(frames)
    duration = total_frames / FPS
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{bg_color}" />',
        '<style>',
        '  .label { font-family: monospace; font-weight: bold; font-size: 13px; }',
        '  .banner { font-family: monospace; font-weight: bold; font-size: 18px; letter-spacing: 2px; }',
        '</style>'
    ]
    
    # Static background grid
    for y in range(ROWS):
        for x in range(COLS):
            px = 10 + x * STEP
            py = 26 + y * STEP
            svg.append(f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}" rx="2" fill="{cell_color}" />')

    # Frame groups using CSS keyframe visibility
    svg.append('<style>')
    for i in range(total_frames):
        start_pct = (i / total_frames) * 100
        end_pct = ((i + 1) / total_frames) * 100
        svg.append(
            f'@keyframes f{i} {{ '
            f'0%, {start_pct:.3f}% {{ opacity: 0; }} '
            f'{start_pct + 0.001:.3f}%, {end_pct:.3f}% {{ opacity: 1; }} '
            f'{end_pct + 0.001:.3f}%, 100% {{ opacity: 0; }} }}'
            f'.frame-{i} {{ animation: f{i} {duration:.2f}s infinite; opacity: 0; }}'
        )
    svg.append('</style>')

    for i, frame in enumerate(frames):
        svg.append(f'<g class="frame-{i}">')
        svg.append(f'<text x="12" y="18" fill="{text_color}" class="label">SCORE: {frame["score"]} | LENGTH: {len(frame["snake"])}</text>')
        
        # Draw Food
        if frame["food"]:
            fx = 10 + frame["food"][0] * STEP + CELL // 2
            fy = 26 + frame["food"][1] * STEP + CELL // 2
            svg.append(f'<circle cx="{fx}" cy="{fy}" r="{CELL // 2}" fill="{food_color}" />')
        
        # Draw Snake
        for idx, (sx, sy) in enumerate(frame["snake"]):
            px = 10 + sx * STEP
            py = 26 + sy * STEP
            color = snake_head if idx == 0 else snake_body
            svg.append(f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}" rx="3" fill="{color}" />')
        
        # Overlay Banners
        if frame["state"] == "WELCOME":
            svg.append(f'<rect x="{WIDTH//2 - 140}" y="{HEIGHT//2 - 12}" width="280" height="36" rx="6" fill="{bg_color}" stroke="{snake_head}" stroke-width="2" />')
            svg.append(f'<text x="{WIDTH//2}" y="{HEIGHT//2 + 11}" text-anchor="middle" fill="{snake_head}" class="banner">WELCOME! STARTING...</text>')
        elif frame["state"] == "GAMEOVER":
            svg.append(f'<rect x="{WIDTH//2 - 175}" y="{HEIGHT//2 - 12}" width="350" height="36" rx="6" fill="{bg_color}" stroke="{food_color}" stroke-width="2" />')
            svg.append(f'<text x="{WIDTH//2}" y="{HEIGHT//2 + 11}" text-anchor="middle" fill="{food_color}" class="banner">TAIL HIT! RESTARTING...</text>')
            
        svg.append('</g>')

    svg.append('</svg>')
    return "\n".join(svg)

if __name__ == "__main__":
    import os
    os.makedirs("dist", exist_ok=True)
    game_frames = simulate_game()
    with open("dist/github-contribution-grid-snake.svg", "w") as f:
        f.write(build_svg(game_frames, dark_mode=False))
    with open("dist/github-contribution-grid-snake-dark.svg", "w") as f:
        f.write(build_svg(game_frames, dark_mode=True))
