import pygame
import cv2
import numpy as np
import sys
import os

pygame.init()

try:
    background = pygame.image.load("image-f62ffc38-38cf-4c34-bf41-f1537f657da5.png")
    WIDTH, HEIGHT = background.get_size()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
except:
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((50, 50, 100))

pygame.display.set_caption("Моя Игра")

try:
    overlay_image = pygame.image.load("b6cb3085-eb56-4a2a-a7cc-a024f1afa0fe (1) (1).png").convert_alpha()
    original_width, original_height = overlay_image.get_size()
    target_height = HEIGHT * 2 // 3
    target_width = HEIGHT * 2 // 3

    if original_width > original_height:
        scale_factor = target_width / original_width
        new_width = target_width
        new_height = int(original_height * scale_factor)
    else:
        scale_factor = target_height / original_height
        new_width = int(original_width * scale_factor)
        new_height = target_height

    new_width = int(new_width * 1.5)
    new_height = int(new_height * 1.5)

    overlay_image = pygame.transform.smoothscale(overlay_image, (new_width, new_height))
    image_loaded = True

except Exception as e:
    image_loaded = False
    overlay_image = pygame.Surface((300, 300), pygame.SRCALPHA)
    overlay_image.fill((255, 0, 0, 128))

try:
    text_field_bg = pygame.image.load("поле.png").convert_alpha()
    text_field_bg = pygame.transform.scale(text_field_bg, (450, 180))
    text_bg_loaded = True
except Exception as e:
    text_bg_loaded = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_WHITE = (200, 200, 200)
DARK_BLUE = (30, 30, 60)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GOLD = (255, 215, 0)

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
dialogue_font = pygame.font.Font(None, 26)
first_video_font = pygame.font.Font(None, 22)

try:
    title_font = pygame.font.Font(None, 72)
except:
    title_font = pygame.font.Font(None, 60)


class TriangleButton:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.base_size = size
        self.is_hovered = False
        self.rect = pygame.Rect(x - size, y - size, size * 2, size * 2)

    def draw(self, surface):
        current_size = int(self.size * 1.3) if self.is_hovered else self.size
        color = LIGHT_WHITE if self.is_hovered else WHITE

        points = [
            (self.x - current_size, self.y - current_size),
            (self.x - current_size, self.y + current_size),
            (self.x + current_size, self.y)
        ]

        pygame.draw.polygon(surface, color, points)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click


class TextField:
    def __init__(self, x, y, width, height, text, custom_font=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.visible = False
        self.alpha = 0
        self.font = custom_font if custom_font else dialogue_font

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
        self.alpha = 0

    def update(self):
        if self.visible and self.alpha < 255:
            self.alpha += 10
            if self.alpha > 255:
                self.alpha = 255

    def draw(self, surface):
        if not self.visible:
            return

        text_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if text_bg_loaded:
            text_surface.blit(text_field_bg, (0, 0))
        else:
            pygame.draw.rect(text_surface, (40, 40, 80, self.alpha),
                             (0, 0, self.width, self.height), border_radius=15)
            pygame.draw.rect(text_surface, (255, 255, 255, self.alpha),
                             (0, 0, self.width, self.height), 2, border_radius=15)

        lines = []
        words = self.text.split(' ')
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = self.font.size(test_line)[0]
            if test_width <= self.width - 40:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        line_height = self.font.get_linesize()
        total_height = len(lines) * line_height
        start_y = (self.height - total_height) // 2 + 15

        for i, line in enumerate(lines):
            text_render = self.font.render(line, True, WHITE)
            text_rect = text_render.get_rect(center=(self.width // 2, start_y + i * line_height))
            text_surface.blit(text_render, text_rect)

        if self.alpha < 255:
            text_surface.set_alpha(self.alpha)

        surface.blit(text_surface, (self.x, self.y))


class ChoiceButton:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click


class AnimatedImage:
    def __init__(self, image, target_x, target_y):
        self.image = image
        self.target_x = target_x
        self.target_y = target_y
        self.width, self.height = image.get_size()
        self.x = target_x
        self.y = HEIGHT + 100
        self.animation_speed = 30
        self.is_animating = True
        self.animation_complete = False

    def update(self):
        if self.is_animating:
            if self.y > self.target_y:
                self.y -= self.animation_speed
                if self.y <= self.target_y:
                    self.y = self.target_y
                    self.is_animating = False
                    self.animation_complete = True
                    return True
            else:
                self.is_animating = False
                self.animation_complete = True
                return True
        return False

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def is_animation_complete(self):
        return self.animation_complete


def draw_title(surface):
    title_text = "ВГУ назад в будущее"
    title_shadow = title_font.render(title_text, True, (0, 0, 0))
    title_main = title_font.render(title_text, True, GOLD)
    title_rect = title_main.get_rect(center=(WIDTH // 2, 80))
    shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 3, 83))
    surface.blit(title_shadow, shadow_rect)
    surface.blit(title_main, title_rect)


def show_photo_for_10_seconds(photo_file, next_video_file=None, third_video_file=None):
    if not os.path.exists(photo_file):
        return False

    try:
        photo = pygame.image.load(photo_file).convert_alpha()
        photo = pygame.transform.scale(photo, (WIDTH, HEIGHT))

        clock = pygame.time.Clock()
        showing = True

        image_width, image_height = overlay_image.get_size()
        target_x = 20
        target_y = HEIGHT // 2 - image_height // 2

        animated_image = AnimatedImage(overlay_image, target_x, target_y)

        text_field_x = target_x + image_width + 20
        text_field_y = target_y

        text_field = TextField(text_field_x, text_field_y, 450, 180,
                               "Вот это, голубчик, просто идеально. Эхх, молодость. Тогда молоко было вкуснее и корм слаще. Пойдем внутрь?")

        yes_button = ChoiceButton(WIDTH // 2 - 150, HEIGHT // 2 + 100, 120, 50, "Да", GREEN)
        no_button = ChoiceButton(WIDTH // 2 + 30, HEIGHT // 2 + 100, 120, 50, "Нет", RED)

        photo_start_time = pygame.time.get_ticks()
        photo_duration = 10000
        text_shown = False

        while showing:
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    showing = False
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing = False
                        return False
                    elif event.key == pygame.K_SPACE:
                        if next_video_file:
                            return play_second_video(next_video_file, third_video_file)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True
                        if yes_button.is_clicked(mouse_pos, mouse_click):
                            if next_video_file:
                                return play_second_video(next_video_file, third_video_file)
                        elif no_button.is_clicked(mouse_pos, mouse_click):
                            showing = False
                            return False

            screen.blit(photo, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

                if animated_image.is_animation_complete() and not text_shown:
                    text_field.show()
                    text_shown = True

            text_field.update()
            text_field.draw(screen)

            yes_button.check_hover(mouse_pos)
            no_button.check_hover(mouse_pos)

            yes_button.draw(screen)
            no_button.draw(screen)

            pygame.display.flip()
            clock.tick(60)

        return True

    except Exception as e:
        return False


def play_first_video(video_file, photo_file=None, next_video_file=None, third_video_file=None):
    if not os.path.exists(video_file):
        return False

    try:
        cap = cv2.VideoCapture(video_file)

        if not cap.isOpened():
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = int(1000 / fps) if fps > 0 else 33

        clock = pygame.time.Clock()
        playing = True

        image_width, image_height = overlay_image.get_size()
        target_x = 20
        target_y = HEIGHT - image_height - 30

        animated_image = AnimatedImage(overlay_image, target_x, target_y)

        text_field_x = target_x + image_width + 50
        text_field_y = target_y + 50

        text_field = TextField(text_field_x, text_field_y, 450, 180,
                               "Ну здравствуй, Голубчик. Не бойтесь, ты в безопасности. Пойдемс, кое-что покажу.",
                               custom_font=first_video_font)

        video_surface = pygame.Surface((WIDTH, HEIGHT))

        video_start_time = pygame.time.get_ticks()
        video_duration = 10000

        while playing and cap.isOpened():
            current_time = pygame.time.get_ticks()

            if current_time - video_start_time >= video_duration:
                if photo_file:
                    cap.release()
                    return show_photo_for_10_seconds(photo_file, next_video_file, third_video_file)
                else:
                    break

            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                    elif event.key == pygame.K_SPACE:
                        if photo_file:
                            cap.release()
                            return show_photo_for_10_seconds(photo_file, next_video_file, third_video_file)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    playing = False

            screen.blit(video_surface, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

                if animated_image.is_animation_complete():
                    text_field.show()

            text_field.update()
            text_field.draw(screen)

            pygame.display.flip()
            clock.tick(fps if fps > 0 else 30)

        cap.release()
        return True

    except Exception as e:
        return False


def play_second_video(video_file, next_video_file=None):
    if not os.path.exists(video_file):
        return False

    try:
        cap = cv2.VideoCapture(video_file)

        if not cap.isOpened():
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)

        clock = pygame.time.Clock()
        playing = True

        image_width, image_height = overlay_image.get_size()
        target_x = WIDTH - image_width - 20
        target_y = HEIGHT - image_height - 30

        animated_image = AnimatedImage(overlay_image, target_x, target_y)

        text_field_x = target_x - 470
        text_field_y = target_y + 120

        new_text = "1918‑й\n\n" \
                   "1918‑с — университет переехал из Юрьева: 4 факультета, около 800 студентовас.\n" \
                   "Писали пером и чернилом, как художники. Кто ошибался — тушь летела по бумаге, как фейерверк!\n" \
                   "Зато уважение к письму было большое‑с. Было время, не то ч... Ой, ладно давай дальше"

        text_field = TextField(text_field_x, text_field_y, 450, 180, new_text)

        video_surface = pygame.Surface((WIDTH, HEIGHT))

        video_start_time = pygame.time.get_ticks()
        video_duration = 7000

        while playing and cap.isOpened():
            current_time = pygame.time.get_ticks()

            if current_time - video_start_time >= video_duration:
                if next_video_file:
                    cap.release()
                    return play_third_video(next_video_file)
                else:
                    break

            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                    elif event.key == pygame.K_SPACE:
                        if next_video_file:
                            cap.release()
                            return play_third_video(next_video_file)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    playing = False

            screen.blit(video_surface, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

                if animated_image.is_animation_complete():
                    text_field.show()

            text_field.update()
            text_field.draw(screen)

            pygame.display.flip()
            clock.tick(fps if fps > 0 else 30)

        cap.release()
        return True

    except Exception as e:
        return False


def play_third_video(video_file):
    if not os.path.exists(video_file):
        return False

    try:
        cap = cv2.VideoCapture(video_file)

        if not cap.isOpened():
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)

        clock = pygame.time.Clock()
        playing = True

        image_width, image_height = overlay_image.get_size()
        target_x = 20
        target_y = HEIGHT - image_height - 10

        animated_image = AnimatedImage(overlay_image, target_x, target_y)
        animated_image.animation_speed = 50

        text_field_x = target_x + image_width + 20
        text_field_y = target_y + 50

        third_text = "1980‑е — ВГУ выходит на новый уровень: новые факультеты, лаборатории, наука кипит. Студенты серьёзные, но иногда включали магнетофон тайком — звучало как подпольный рок‑клуб! Деканы грозились, но коту нравилось мурчать от музыки. Времена моей молодости когда молоко было в разы вкуснее."

        text_field = TextField(text_field_x, text_field_y, 450, 180, third_text)

        video_surface = pygame.Surface((WIDTH, HEIGHT))

        while playing and cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        playing = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    playing = False

            screen.blit(video_surface, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

                if animated_image.is_animation_complete():
                    text_field.show()

            text_field.update()
            text_field.draw(screen)

            pygame.display.flip()
            clock.tick(fps if fps > 0 else 30)

        cap.release()
        return True

    except Exception as e:
        return False


triangle_button = TriangleButton(WIDTH // 2, HEIGHT // 2 + 220, 50)


def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_click = True
                    if triangle_button.is_clicked(mouse_pos, mouse_click):
                        first_video = "grok-video-2c2186c2-d7e3-468a-9b63-c607bb5a83bc.mp4"
                        photo_file = "photo_5278349064456048963_y.jpg"
                        second_video = "grok-video-5e9e0399-857b-40cf-8d67-35818b6f128b.mp4"
                        third_video = "студенты.mp4"
                        play_first_video(first_video, photo_file, second_video, third_video)

        triangle_button.check_hover(mouse_pos)

        screen.blit(background, (0, 0))
        draw_title(screen)
        triangle_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()