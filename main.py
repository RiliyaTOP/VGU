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
    text_field_bg = pygame.transform.scale(text_field_bg, (WIDTH - 40, 150))
    text_bg_loaded = True
except Exception as e:
    text_bg_loaded = False

try:
    yes_photo = pygame.image.load("да.png").convert_alpha()
    no_photo = pygame.image.load("нет.png").convert_alpha()

    photo_width, photo_height = 200, 150
    yes_photo = pygame.transform.smoothscale(yes_photo, (photo_width, photo_height))
    no_photo = pygame.transform.smoothscale(no_photo, (photo_width, photo_height))


    def add_shadow(image, shadow_offset=5, shadow_color=(0, 0, 0, 128)):
        width, height = image.get_size()
        shadow_surface = pygame.Surface((width + shadow_offset, height + shadow_offset), pygame.SRCALPHA)

        shadow_rect = pygame.Rect(shadow_offset, shadow_offset, width, height)
        pygame.draw.rect(shadow_surface, shadow_color, shadow_rect, border_radius=10)

        shadow_surface.blit(image, (0, 0))

        return shadow_surface


    yes_photo_with_shadow = add_shadow(yes_photo)
    no_photo_with_shadow = add_shadow(no_photo)

    photos_loaded = True
except Exception as e:
    photos_loaded = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_WHITE = (200, 200, 200)
DARK_BLUE = (30, 30, 60)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GOLD = (255, 215, 0)

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
dialogue_font = pygame.font.Font(None, 20)
first_video_font = pygame.font.Font(None, 20)

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


class PhotoButton:
    def __init__(self, x, y, photo, border_color=WHITE, border_width=3):
        self.x = x
        self.y = y
        self.photo = photo
        self.border_color = border_color
        self.border_width = border_width
        self.rect = self.photo.get_rect(topleft=(x, y))
        self.is_hovered = False

    def draw(self, surface):
        surface.blit(self.photo, (self.x, self.y))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click


class ClickableImage:
    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_hovered = False
        self.clickable = True

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos) and self.clickable
        return self.is_hovered

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click and self.clickable


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
            if test_width > self.width - 40:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    while word:
                        for i in range(len(word), 0, -1):
                            part = word[:i]
                            if self.font.size(part)[0] <= self.width - 40:
                                lines.append(part)
                                word = word[i:]
                                break
            else:
                current_line.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        line_height = self.font.get_linesize()
        total_height = len(lines) * line_height
        start_y = (self.height - total_height) // 2

        max_lines = (self.height - 20) // line_height
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            if lines:
                last_line = lines[-1]
                while last_line and self.font.size(last_line + '...')[0] > self.width - 40:
                    last_line = last_line[:-1]
                lines[-1] = last_line + '...'

        for i, line in enumerate(lines):
            text_render = self.font.render(line, True, BLACK)
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

        text_surf = font.render(self.text, True, BLACK)
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


def play_rewind_video(video_file):
    if not os.path.exists(video_file):
        return False

    try:
        cap = cv2.VideoCapture(video_file)

        if not cap.isOpened():
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)

        clock = pygame.time.Clock()
        playing = True

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

            screen.blit(video_surface, (0, 0))

            skip_hint = small_font.render("Нажмите ПРОБЕЛ для пропуска", True, WHITE)
            screen.blit(skip_hint, (WIDTH // 2 - skip_hint.get_width() // 2, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(fps if fps > 0 else 30)

        cap.release()
        return True

    except Exception as e:
        return False


def show_photo_for_10_seconds(photo_file, next_video_file=None, third_video_file=None, fourth_video_file=None,
                              fifth_video_file=None):
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

        text_field = TextField(20, HEIGHT - 170, WIDTH - 40, 150,
                               "Вот это, голубчик, просто идеально. Эхх, молодость. Тогда молоко было вкуснее и корм слаще. Пойдем внутрь?")

        if photos_loaded:
            photo_width = yes_photo_with_shadow.get_width()
            photo_height = yes_photo_with_shadow.get_height()
            photo_spacing = 50

            total_photos_width = photo_width * 2 + photo_spacing
            start_x = (WIDTH - total_photos_width) // 2

            # Используем изображения с тенью
            yes_button = PhotoButton(start_x, HEIGHT // 2 + 80, yes_photo_with_shadow)
            no_button = PhotoButton(start_x + photo_width + photo_spacing, HEIGHT // 2 + 80, no_photo_with_shadow)
        else:
            yes_button = ChoiceButton(WIDTH // 2 - 150, HEIGHT // 2 + 100, 120, 50, "Да", GREEN)
            no_button = ChoiceButton(WIDTH // 2 + 30, HEIGHT // 2 + 100, 120, 50, "Нет", RED)

        text_shown = False
        space_pressed = False

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
                    elif event.key == pygame.K_SPACE and not space_pressed:
                        space_pressed = True
                        if next_video_file:
                            return play_second_video(next_video_file, third_video_file, fourth_video_file,
                                                     fifth_video_file)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True
                        if yes_button.is_clicked(mouse_pos, mouse_click):
                            if next_video_file:
                                return play_second_video(next_video_file, third_video_file, fourth_video_file,
                                                     fifth_video_file)
                        elif no_button.is_clicked(mouse_pos, mouse_click):
                            showing = False
                            return False

            screen.blit(photo, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

            if not text_shown:
                text_field.show()
                text_shown = True

            text_field.update()
            text_field.draw(screen)

            if photos_loaded:
                yes_button.check_hover(mouse_pos)
                no_button.check_hover(mouse_pos)
                yes_button.draw(screen)
                no_button.draw(screen)
            else:
                yes_button.check_hover(mouse_pos)
                no_button.check_hover(mouse_pos)
                yes_button.draw(screen)
                no_button.draw(screen)
            space_hint = small_font.render("Нажмите ПРОБЕЛ для выбора ДА", True, WHITE)
            screen.blit(space_hint, (WIDTH // 2 - space_hint.get_width() // 2, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(60)

        return True

    except Exception as e:
        return False


def play_first_video(video_file, photo_file=None, next_video_file=None, third_video_file=None, fourth_video_file=None,
                     fifth_video_file=None):
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
        target_y = HEIGHT - image_height - 30

        animated_image = AnimatedImage(overlay_image, target_x, target_y)

        text_field = TextField(20, HEIGHT - 170, WIDTH - 40, 150,
                               "Ну здравствуй, Голубчик. Не бойтесь, ты в безопасности. Пойдемс, кое-что покажу.",
                               custom_font=first_video_font)

        video_surface = pygame.Surface((WIDTH, HEIGHT))

        text_shown = False
        space_pressed = False

        while playing and cap.isOpened():
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                    elif event.key == pygame.K_SPACE and not space_pressed:
                        space_pressed = True
                        if photo_file:
                            cap.release()
                            return show_photo_for_10_seconds(photo_file, next_video_file, third_video_file,
                                                             fourth_video_file, fifth_video_file)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False

            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

            screen.blit(video_surface, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

            if not text_shown:
                text_field.show()
                text_shown = True

            text_field.update()
            text_field.draw(screen)

            space_hint = small_font.render("Нажмите ПРОБЕЛ для продолжения", True, WHITE)
            screen.blit(space_hint, (WIDTH // 2 - space_hint.get_width() // 2, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(fps if fps > 0 else 30)

        cap.release()
        return True

    except Exception as e:
        return False


def play_second_video(video_file, next_video_file=None, fourth_video_file=None, fifth_video_file=None):
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
        target_x = WIDTH - image_width
        target_y = HEIGHT - image_height
        animated_image = AnimatedImage(overlay_image, target_x, target_y)

        try:
            student_image = pygame.image.load("студ.png").convert_alpha()
            student_width, student_height = 400, 600
            student_image = pygame.transform.smoothscale(student_image, (student_width, student_height))
            student_x = 50
            student_y = HEIGHT - student_height - 1
            clickable_student = ClickableImage(student_image, student_x, student_y)
            student_loaded = True
        except Exception as e:
            print(f"Не удалось загрузить студ.png: {e}")
            student_loaded = False

        student_text = "                                А наши лаборатории оснащены по последнему слову техники, хоть и не всегда хватает импортных приборов, но мы сами мастерим, что нужно. В                                       общежитии жизнь кипит: комсомольские собрания, субботники, а по вечерам — песни под гитару или споры о марксизме-ленинизме. Конечно, сессия — это ад, зубрежка до утра, но зато после — чувство, что ты часть большой страны, которая строит коммунизм."
        student_text_field = TextField(40, 20, WIDTH - 180, 175, student_text)
        student_text_visible = False

        new_text = "                                    1980‑е — ВГУ выходит на новый уровень: новые факультеты, лаборатории, наука кипит. Студенты серьёзные, но иногда включали магнетофон                                      тайком — звучало как подпольный рок‑клуб! Деканы грозились, но коту нравилось мурчать от музыки. Времена моей молодости когда молоко было в разы вкуснее."
        text_field = TextField(20, HEIGHT - 170, WIDTH - 180, 175, new_text)

        video_surface = pygame.Surface((WIDTH, HEIGHT))

        text_shown = False
        space_pressed = False

        while playing and cap.isOpened():
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                    elif event.key == pygame.K_SPACE and not space_pressed:
                        space_pressed = True
                        if next_video_file:
                            cap.release()
                            return play_third_video(next_video_file, fourth_video_file, fifth_video_file)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True
                        if student_loaded and clickable_student.is_clicked(mouse_pos, mouse_click):
                            student_text_visible = not student_text_visible
                            if student_text_visible:
                                student_text_field.show()
                            else:
                                student_text_field.hide()

            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

            screen.blit(video_surface, (0, 0))

            if student_loaded:
                clickable_student.check_hover(mouse_pos)
                clickable_student.draw(screen)

                if clickable_student.is_hovered:
                    hint_text = small_font.render("Нажмите для рассказа студента", True, WHITE)
                    screen.blit(hint_text, (clickable_student.x, clickable_student.y - 25))

                student_text_field.update()
                student_text_field.draw(screen)

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

            if not text_shown:
                text_field.show()
                text_shown = True

            text_field.update()
            text_field.draw(screen)

            space_hint = small_font.render("Нажмите ПРОБЕЛ для продолжения", True, WHITE)
            screen.blit(space_hint, (WIDTH // 2 - space_hint.get_width() // 2, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(fps if fps > 0 else 30)

        cap.release()
        return True

    except Exception as e:
        return False


def play_third_video(video_file, fourth_video_file=None, fifth_video_file=None):
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

        third_text = "                                     Университет имел около 35 кафедр, 80 лабораторий и бюджет в миллионы рублей, что позволяло готовить специалистов для промышленности и науки региона. Это время заложило основу для современного ВГУ как ведущего вуза Центрального Черноземья."

        text_field = TextField(20, HEIGHT - 170, WIDTH - 180, 175, third_text)

        video_surface = pygame.Surface((WIDTH, HEIGHT))
        text_shown = False
        space_pressed = False

        while playing and cap.isOpened():
            current_time = pygame.time.get_ticks()
            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                    elif event.key == pygame.K_SPACE and not space_pressed:
                        space_pressed = True
                        if fourth_video_file:
                            cap.release()
                            return play_fourth_video(fourth_video_file, fifth_video_file)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False

            screen.blit(video_surface, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

            if not text_shown:
                text_field.show()
                text_shown = True

            text_field.update()
            text_field.draw(screen)

            space_hint = small_font.render("Нажмите ПРОБЕЛ для продолжения", True, WHITE)
            screen.blit(space_hint, (WIDTH // 2 - space_hint.get_width() // 2, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(fps if fps > 0 else 30)

        cap.release()
        if fourth_video_file:
            return play_fourth_video(fourth_video_file, fifth_video_file)
        return True

    except Exception as e:
        return False


def play_fourth_video(video_file, fifth_video_file=None):
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

        fourth_text = "                                     2010, голубчик, послушай что я тебе скажу... Времена меняются, но ВГУ всегда остается местом, где рождаются великие умы. Цени каждый момент здесь!"

        text_field = TextField(20, HEIGHT - 170, WIDTH - 180, 175, fourth_text)

        video_surface = pygame.Surface((WIDTH, HEIGHT))
        space_pressed = False

        while playing and cap.isOpened():
            current_time = pygame.time.get_ticks()
            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                    elif event.key == pygame.K_SPACE and not space_pressed:
                        space_pressed = True
                        if fifth_video_file:
                            playing = False
                            cap.release()
                            return play_fifth_video(fifth_video_file)
                        else:
                            playing = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False

            screen.blit(video_surface, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

            text_field.show()
            text_field.update()
            text_field.draw(screen)

            space_hint = small_font.render("Нажмите ПРОБЕЛ для завершения", True, WHITE)
            screen.blit(space_hint, (WIDTH // 2 - space_hint.get_width() // 2, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(fps if fps > 0 else 30)

        cap.release()
        return True

    except Exception as e:
        return False


def play_fifth_video(video_file):
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
        target_x = WIDTH // 2 - image_width // 2
        target_y = HEIGHT - image_height - 30

        animated_image = AnimatedImage(overlay_image, target_x, target_y)

        fifth_text = "                                Студенческий городок подключён к интернету, внедряются электронные дневники и расписания. Кафедры международного сотрудничества                           заключают обмен с зарубежными вузами. Кот замечает: лапки коротки, чтобы дотянуться до электронной зачётки, но дух науки живой‑с!"

        text_field = TextField(20, HEIGHT - 170, WIDTH - 180, 175, fifth_text)

        video_surface = pygame.Surface((WIDTH, HEIGHT))
        space_pressed = False

        while playing and cap.isOpened():
            current_time = pygame.time.get_ticks()
            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                    elif event.key == pygame.K_SPACE and not space_pressed:
                        space_pressed = True
                        playing = False
                        cap.release()
                        return show_final_scene()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False

            screen.blit(video_surface, (0, 0))

            if image_loaded:
                animated_image.update()
                animated_image.draw(screen)

            text_field.show()
            text_field.update()
            text_field.draw(screen)

            space_hint = small_font.render("Нажмите ПРОБЕЛ для продолжения", True, WHITE)
            screen.blit(space_hint, (WIDTH // 2 - space_hint.get_width() // 2, HEIGHT - 30))

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
                        rewind_video = "перемотка.mp4"
                        if os.path.exists(rewind_video):
                            play_rewind_video(rewind_video)

                        first_video = "grok-video-2c2186c2-d7e3-468a-9b63-c607bb5a83bc.mp4"
                        photo_file = "photo_5278349064456048963_y.jpg"
                        second_video = "grok-video-5e9e0399-857b-40cf-8d67-35818b6f128b.mp4"
                        third_video = "студенты.mp4"
                        fourth_video = "говорит.mp4"
                        fifth_video = "стул.mp4"
                        play_first_video(first_video, photo_file, second_video, third_video, fourth_video, fifth_video)

        triangle_button.check_hover(mouse_pos)

        screen.blit(background, (0, 0))
        draw_title(screen)
        triangle_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)


def show_final_scene():
    try:
        background_image = pygame.image.load("тест.jpg").convert_alpha()
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

        final_image = pygame.image.load("b6cb3085-eb56-4a2a-a7cc-a024f1afa0fe (1) (1).png").convert_alpha()


        original_width, original_height = final_image.get_size()

        max_image_height = HEIGHT - 150
        max_image_width = WIDTH // 2 - 40

        image_ratio = original_width / original_height

        if original_width > original_height:
            new_width = max_image_width
            new_height = int(new_width / image_ratio)
        else:
            new_height = max_image_height
            new_width = int(new_height * image_ratio)

        if new_height > max_image_height:
            new_height = max_image_height
            new_width = int(new_height * image_ratio)

        if new_width > max_image_width:
            new_width = max_image_width
            new_height = int(new_width / image_ratio)

        final_image = pygame.transform.smoothscale(final_image, (new_width * 2, new_height * 2))

        image_x = 0
        image_y = -200

        final_text = "Так, а ты сам то, чем интересуешься?"
        text_field = TextField(WIDTH // 2, HEIGHT // 2 - 140, WIDTH // 2 + 50, 180, final_text)
        text_field.show()

        clock = pygame.time.Clock()
        showing = True
        space_pressed = False

        while showing:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    showing = False
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing = False
                        return False
                    elif event.key == pygame.K_SPACE and not space_pressed:
                        space_pressed = True
                        showing = False
                        return show_test_image("тест.jpg")
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False

            screen.blit(background_image, (0, 0))

            screen.blit(final_image, (image_x, image_y))

            text_field.update()
            text_field.draw(screen)

            space_hint = small_font.render("Нажмите ПРОБЕЛ для продолжения", True, WHITE)
            screen.blit(space_hint, (WIDTH // 2 - space_hint.get_width() // 2, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(60)

        return True

    except Exception as e:
        print(f"Ошибка в финальной сцене: {e}")
        return False


def show_test_image(image_file):
    if not os.path.exists(image_file):
        return False

    try:
        test_image = pygame.image.load(image_file).convert_alpha()
        test_image = pygame.transform.scale(test_image, (WIDTH, HEIGHT))

        try:
            scroll_image = pygame.image.load("свиток.png").convert_alpha()
            scroll_width, scroll_height = 550, 750
            scroll_image = pygame.transform.smoothscale(scroll_image, (scroll_width, scroll_height))
            scroll_x = WIDTH - scroll_width - 20
            scroll_y = HEIGHT // 2 - scroll_height // 2
            scroll_loaded = True
        except Exception as e:
            print(f"Не удалось загрузить свиток.png: {e}")
            scroll_loaded = False

        try:
            yes_img = pygame.image.load("да.png").convert_alpha()
            no_img = pygame.image.load("нет.png").convert_alpha()

            original_yes_width, original_yes_height = yes_img.get_size()
            original_no_width, original_no_height = no_img.get_size()

            target_height = 60
            yes_ratio = original_yes_width / original_yes_height
            no_ratio = original_no_width / original_no_height

            button_width_yes = int(target_height * yes_ratio)
            button_width_no = int(target_height * no_ratio)
            button_height = target_height

            yes_img = pygame.transform.smoothscale(yes_img, (button_width_yes, button_height))
            no_img = pygame.transform.smoothscale(no_img, (button_width_no, button_height))

            yes_img_without_shadow = yes_img
            no_img_without_shadow = no_img

            photos_loaded_in_test = True
        except Exception as e:
            print(f"Не удалось загрузить изображения кнопок: {e}")
            photos_loaded_in_test = False
        questions = [
            "1. Нравится ли вам работать с цифрами и решать математические задачи?",
            "2. Любите ли вы выступать перед аудиторией?",
            "3. Интересуетесь ли вы компьютерными технологиями и программированием?",
            "4. Нравится ли вам изучать иностранные языки и культуры?",
            "5. Любите ли вы проводить эксперименты и научные исследования?",
            "6. Интересуетесь ли вы политикой и общественными процессами?",
            "7. Нравится ли вам работа с текстами и литературой?"
        ]

        directions = [
            "Математика/Экономика",
            "Педагогика/Политология",
            "Информатика/Физика",
            "Лингвистика/Международные отношения",
            "Естественные науки/Химия",
            "Юриспруденция/Политология",
            "Филология/Журналистика"
        ]

        answers = [[0, 0] for _ in range(len(questions))]

        button_spacing = 15

        question_spacing = 90

        max_button_width = max(button_width_yes, button_width_no)
        base_x = scroll_x + scroll_width - (max_button_width * 2) - 80
        base_y = scroll_y + 80

        yes_buttons = []
        no_buttons = []

        # СОЗДАЕМ 7 ПАР КНОПОК
        for i in range(len(questions)):
            if photos_loaded_in_test:
                yes_button = PhotoButton(
                    base_x,
                    base_y + i * question_spacing,
                    yes_img_without_shadow
                )
                no_button = PhotoButton(
                    base_x + max_button_width + 10,
                    base_y + i * question_spacing,
                    no_img_without_shadow
                )
            else:
                yes_button = ChoiceButton(
                    base_x,
                    base_y + i * question_spacing,
                    button_width_yes, button_height, "Да", GREEN
                )
                no_button = ChoiceButton(
                    base_x + max_button_width + 10,
                    base_y + i * question_spacing,
                    button_width_no, button_height, "Нет", RED
                )
            yes_buttons.append(yes_button)
            no_buttons.append(no_button)

        clock = pygame.time.Clock()
        showing = True
        space_pressed = False
        all_answered = False
        show_results = False
        recommended_directions = []

        while showing:
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
                    elif event.key == pygame.K_SPACE and not space_pressed:
                        space_pressed = True
                        if show_results:
                            showing = False
                            return True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True
                        for i in range(len(questions)):
                            if yes_buttons[i].is_clicked(mouse_pos, mouse_click):
                                answers[i] = [1, 0]
                            elif no_buttons[i].is_clicked(mouse_pos, mouse_click):
                                answers[i] = [0, 1]

            all_answered = all(any(answer) for answer in answers)

            if all_answered and not show_results:
                show_results = True
                recommended_directions = []
                for i in range(len(questions)):
                    if answers[i][0]:
                        recommended_directions.append(directions[i])

            screen.blit(test_image, (0, 0))

            if scroll_loaded:
                screen.blit(scroll_image, (scroll_x, scroll_y))

                question_font = pygame.font.Font(None, 20)
                title_font = pygame.font.Font(None, 28)
                result_font = pygame.font.Font(None, 22)

                if not show_results:
                    title_text = "Определи своё направление"
                    title_render = title_font.render(title_text, True, BLACK)
                    screen.blit(title_render,
                                (scroll_x + (scroll_width - title_render.get_width()) // 2, scroll_y + 10))

                    for i, question in enumerate(questions):
                        words = question.split(' ')
                        lines = []
                        current_line = []

                        for word in words:
                            test_line = ' '.join(current_line + [word])
                            if question_font.size(test_line)[0] < scroll_width - 100:
                                current_line.append(word)
                            else:
                                if current_line:
                                    lines.append(' '.join(current_line))
                                current_line = [word]

                        if current_line:
                            lines.append(' '.join(current_line))

                        for j, line in enumerate(lines):
                            question_render = question_font.render(line, True, BLACK)
                            screen.blit(question_render, (scroll_x + 50,
                                                          scroll_y + 60 + i * question_spacing + j * 20))

                    for i in range(len(questions)):
                        yes_buttons[i].check_hover(mouse_pos)
                        no_buttons[i].check_hover(mouse_pos)

                        if answers[i][0]:
                            pygame.draw.rect(screen, (0, 255, 0),
                                             (yes_buttons[i].x - 3, yes_buttons[i].y - 3,
                                              yes_buttons[i].photo.get_width() + 6,
                                              yes_buttons[i].photo.get_height() + 6),
                                             3, border_radius=8)
                        elif answers[i][1]:
                            pygame.draw.rect(screen, (255, 0, 0),
                                             (no_buttons[i].x - 3, no_buttons[i].y - 3,
                                              no_buttons[i].photo.get_width() + 6,
                                              no_buttons[i].photo.get_height() + 6),
                                             3, border_radius=8)

                        yes_buttons[i].draw(screen)
                        no_buttons[i].draw(screen)

                else:
                    # Показываем результаты автоматически
                    title_text = "Результаты тестирования"
                    title_render = title_font.render(title_text, True, BLACK)
                    screen.blit(title_render,
                                (scroll_x + (scroll_width - title_render.get_width()) // 2, scroll_y + 20))

                    if recommended_directions:
                        result_text = "Вам подходят направления:"
                        result_render = result_font.render(result_text, True, BLACK)
                        screen.blit(result_render, (scroll_x + 50, scroll_y + 80))

                        # Отображаем рекомендованные направления
                        for i, direction in enumerate(recommended_directions):
                            dir_render = result_font.render(f"• {direction}", True, BLACK)
                            screen.blit(dir_render, (scroll_x + 70, scroll_y + 110 + i * 30))

                        # Советы по выбору факультета
                        advice_y = scroll_y + 110 + len(recommended_directions) * 30 + 20
                        advice_text = "Рекомендуем обратить внимание на соответствующие "
                        advice_render = result_font.render(advice_text, True, BLACK)
                        screen.blit(advice_render, (scroll_x + 50, advice_y))

                        advice_text1 = "факультеты ВГУ!"
                        advice_render1 = result_font.render(advice_text1, True, BLACK)
                        screen.blit(advice_render1, (scroll_x + 50, advice_y + 30))
                    else:
                        no_pref_text = "На основе ваших ответов сложно определить четкие"
                        no_pref_render = result_font.render(no_pref_text, True, BLACK)
                        screen.blit(no_pref_render, (scroll_x + 50, scroll_y + 80))


                        no_pref_text = "предпочтения."
                        no_pref_render = result_font.render(no_pref_text, True, BLACK)
                        screen.blit(no_pref_render, (scroll_x + 50, scroll_y + 110))

                        explore_text = "Рекомендуем изучить разные факультеты ВГУ!"
                        explore_render = result_font.render(explore_text, True, BLACK)
                        screen.blit(explore_render, (scroll_x + 50, scroll_y + 140))

            # Инструкция
            if not show_results:
                if not all_answered:
                    space_hint = small_font.render("Ответьте на все вопросы", True, WHITE)
                else:
                    space_hint = small_font.render("", True, WHITE)
            else:
                space_hint = small_font.render("Нажмите ПРОБЕЛ для завершения", True, WHITE)

            screen.blit(space_hint, (WIDTH // 2 - space_hint.get_width() // 2, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(60)

        return True

    except Exception as e:
        print(f"Ошибка в show_test_image: {e}")
        return False


triangle_button = TriangleButton(WIDTH // 2, HEIGHT // 2 + 220, 50)


def main():
    clock = pygame.time.Clock()
    running = True
    show_final_after_video = False


    pygame.mixer.init()
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.set_volume(0.23)
    pygame.mixer.music.play(-1)

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
                        rewind_video = "перемотка.mp4"
                        if os.path.exists(rewind_video):
                            play_rewind_video(rewind_video)

                        first_video = "grok-video-2c2186c2-d7e3-468a-9b63-c607bb5a83bc.mp4"
                        photo_file = "photo_5278349064456048963_y.jpg"
                        second_video = "grok-video-5e9e0399-857b-40cf-8d67-35818b6f128b.mp4"
                        third_video = "студенты.mp4"
                        fourth_video = "говорит.mp4"
                        fifth_video = "стул.mp4"

                        play_first_video(first_video, photo_file, second_video, third_video, fourth_video, fifth_video)

        triangle_button.check_hover(mouse_pos)

        screen.blit(background, (0, 0))
        draw_title(screen)
        triangle_button.draw(screen)


        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()
    pygame.mixer.music.stop()
    sys.exit()