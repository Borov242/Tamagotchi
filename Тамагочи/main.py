import json
import random

import pygame as pg

# Инициализация pg
pg.init()

# Размеры окна
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550

ICON_SIZE = 80
PADDING = 5

BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60

DOG_WIDTH = 310
DOG_HEIGHT = 500

MENU_NAV_XPAD = 90
MENU_NAV_YPAD = 130

FOOD_SIZE = 200

TOY_SIZE = 100

FPS = 60

font = pg.font.Font(None, 40)
font_mini = pg.font.Font(None, 15)
font_maxi = pg.font.Font(None, 200)


def load_image(file, width, height):
    image = pg.image.load(file)
    image = pg.transform.scale(image, (width, height))
    return image


def text_render(text, text_font=font):
    return text_font.render(str(text), True, "black")


class Toy(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        toys_list = ("ball", "blue bone", "red bone")
        self.image = load_image(f"images/toys/{random.choice(toys_list)}.png", TOY_SIZE, TOY_SIZE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(88, 613)
        self.rect.y = 0

    def update(self):
        self.rect.y += 5


class Dog(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("images/dog.png", DOG_WIDTH // 2, DOG_HEIGHT // 2)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15)

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.rect.x -= 5
        if keys[pg.K_d]:
            self.rect.x += 5

        if self.rect.x > 668:
            self.rect.x = 668
        if self.rect.x < 88:
            self.rect.x = 88


class MiniGame:
    def __init__(self, game):
        self.game = game

        self.background = load_image("images/game_background.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.dog = Dog()
        self.toys = pg.sprite.Group()

        self.score = 0

        self.start_time = pg.time.get_ticks()
        self.interval = 1000 * 10

    def new_game(self):
        self.dog = Dog()
        self.toys = pg.sprite.Group()

        self.score = 0

        self.start_time = pg.time.get_ticks()
        self.interval = 1000 * 20

    def update(self):
        self.dog.update()
        self.toys.update()
        if random.randint(1, 100) == 1:
            self.toys.add(Toy())
        hits = pg.sprite.spritecollide(self.dog, self.toys, True, pg.sprite.collide_rect_ratio(0.6))
        self.score += len(hits)
        if pg.time.get_ticks() - self.start_time > self.interval:
            self.game.happiness += int(self.score // 2)
            if self.game.happiness > 100:
                self.game.happiness = 100
            self.game.mode = "Main"
            self.new_game()

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        screen.blit(self.dog.image, self.dog.rect)

        screen.blit(text_render(self.score), (MENU_NAV_XPAD + 20, 80))

        self.toys.draw(screen)


class Food:
    def __init__(self, name, price, file, hunger, medicine_power=0):
        self.name = name
        self.price = price
        self.image = load_image(file, FOOD_SIZE, FOOD_SIZE)
        self.hunger = hunger
        self.medicine_power = medicine_power


class FoodMenu:
    def __init__(self, game):
        self.game = game
        self.menu_page = load_image("images/menu/menu_page.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.bottom_label_off = load_image("images/menu/bottom_label_off.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bottom_label_on = load_image("images/menu/bottom_label_on.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_off = load_image("images/menu/top_label_off.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_on = load_image("images/menu/top_label_on.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.items = [Food("Мясо", 30, "images/food/meat.png", 10),
                      Food("Яблоко", 30, "images/food/apple.png", 5),
                      Food("Кость", 30, "images/food/bone.png", 7),
                      Food("Корм", 40, "images/food/dog food.png", 15),
                      Food("Элитный корм", 100, "images/food/dog food elite.png", 25, medicine_power=2),
                      Food("Лекарство", 200, "images/food/medicine.png", 0, medicine_power=10)]

        self.current_item = 0

        self.item_rect = self.items[0].image.get_rect()
        self.item_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.next_button = Button("Вперёд", SCREEN_WIDTH - MENU_NAV_XPAD - BUTTON_WIDTH, SCREEN_HEIGHT - MENU_NAV_YPAD,
                                  width=int(BUTTON_WIDTH // 1.2), height=int(BUTTON_HEIGHT // 1.2), func=self.to_next)

        self.back_button = Button("Назад", MENU_NAV_XPAD + 30, SCREEN_HEIGHT - MENU_NAV_YPAD,
                                  width=int(BUTTON_WIDTH // 1.2), height=int(BUTTON_HEIGHT // 1.2), func=self.to_back)

        self.eat_button = Button("Съесть", 450 - BUTTON_WIDTH // 2.5,
                                 SCREEN_HEIGHT - MENU_NAV_YPAD - BUTTON_HEIGHT + 5,
                                 width=int(BUTTON_WIDTH // 1.2), height=int(BUTTON_HEIGHT // 1.2), func=self.eat)

        self.buttons = (self.next_button, self.back_button, self.eat_button)

        self.text_price = text_render(self.items[self.current_item].price, font)
        self.text_price_rect = self.text_price.get_rect()
        self.text_price_rect.center = (450, 180)

        self.text_name = text_render(self.items[self.current_item].name, font)
        self.text_name_rect = self.text_name.get_rect()
        self.text_name_rect.center = (450, 125)

    def eat(self):
        if self.game.money > self.items[self.current_item].price:
            self.game.money -= self.items[self.current_item].price

            self.game.hunger += self.items[self.current_item].hunger
            if self.game.hunger > 100:
                self.game.hunger = 100

            self.game.health += self.items[self.current_item].medicine_power
            if self.game.health > 100:
                self.game.health = 100

    def to_next(self):
        if self.current_item != len(self.items) - 1:
            self.current_item += 1

    def to_back(self):
        if self.current_item != 0:
            self.current_item -= 1

    def update(self):
        for button in self.buttons:
            button.update()

    def is_clicked(self, event):
        for button in self.buttons:
            button.is_clicked(event)

    def draw(self, screen):
        screen.blit(self.menu_page, (0, 0))

        screen.blit(self.items[self.current_item].image, self.item_rect)

        self.text_name = text_render(self.items[self.current_item].name, font)
        self.text_name_rect = self.text_name.get_rect()
        self.text_name_rect.center = (450, 125)
        screen.blit(self.text_name, self.text_name_rect)

        self.text_price = text_render(self.items[self.current_item].price, font)
        self.text_price_rect = self.text_price.get_rect()
        self.text_price_rect.center = (450, 180)
        screen.blit(self.text_price, self.text_price_rect)

        self.next_button.draw(screen)
        self.back_button.draw(screen)
        self.eat_button.draw(screen)


class Item:
    def __init__(self, name, price, file, is_using, is_bought):
        self.name = name
        self.price = price
        self.is_bought = is_bought
        self.is_using = is_using
        self.file = file

        self.image = load_image(file, DOG_WIDTH // 1.7, DOG_HEIGHT // 1.7)
        self.full_image = load_image(file, DOG_WIDTH, DOG_HEIGHT)


class ClothesMenu:
    def __init__(self, game, data):
        self.game = game
        self.menu_page = load_image("images/menu/menu_page.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.bottom_label_off = load_image("images/menu/bottom_label_off.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bottom_label_on = load_image("images/menu/bottom_label_on.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_off = load_image("images/menu/top_label_off.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_on = load_image("images/menu/top_label_on.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.items = []
        for item in data:
            self.items.append(Item(*item.values()))

        self.current_item = 0

        self.item_rect = self.items[0].image.get_rect()
        self.item_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.next_button = Button("Вперёд", SCREEN_WIDTH - MENU_NAV_XPAD - BUTTON_WIDTH, SCREEN_HEIGHT - MENU_NAV_YPAD,
                                  width=int(BUTTON_WIDTH // 1.2), height=int(BUTTON_HEIGHT // 1.2), func=self.to_next)

        self.back_button = Button("Назад", MENU_NAV_XPAD + 30, SCREEN_HEIGHT - MENU_NAV_YPAD,
                                  width=int(BUTTON_WIDTH // 1.2), height=int(BUTTON_HEIGHT // 1.2), func=self.to_back)

        self.put_on_button = Button("Надеть", MENU_NAV_XPAD + 30, SCREEN_HEIGHT - MENU_NAV_YPAD - BUTTON_HEIGHT - 5,
                                    width=int(BUTTON_WIDTH // 1.2), height=int(BUTTON_HEIGHT // 1.2), func=self.use)

        self.buy_button = Button("Купить", 450 - BUTTON_WIDTH // 2.5,
                                 SCREEN_HEIGHT - MENU_NAV_YPAD - BUTTON_HEIGHT + 5,
                                 width=int(BUTTON_WIDTH // 1.2), height=int(BUTTON_HEIGHT // 1.2), func=self.buy)

        self.buttons = (self.next_button, self.back_button, self.put_on_button, self.buy_button)

        self.text_price = text_render(self.items[self.current_item].price, font)
        self.text_price_rect = self.text_price.get_rect()
        self.text_price_rect.center = (450, 180)

        self.text_name = text_render(self.items[self.current_item].name, font)
        self.text_name_rect = self.text_name.get_rect()
        self.text_name_rect.center = (450, 125)

        self.text_bought = text_render("Куплено", font)
        self.text_bought_rect = self.text_bought.get_rect()
        self.text_bought_rect.center = (700, 200)

        self.text_put_on = text_render("Надето", font)
        self.text_put_on_rect = self.text_put_on.get_rect()
        self.text_put_on_rect.center = (700, 125)

    def use(self):
        if self.items[self.current_item].is_bought:
            self.items[self.current_item].is_using = not self.items[self.current_item].is_using
            if self.items[self.current_item].is_using:
                self.put_on_button.text = text_render("Снять", self.put_on_button.text_font)
            else:
                self.put_on_button.text = text_render("Надеть", self.put_on_button.text_font)

    def buy(self):
        if self.game.money > self.items[self.current_item].price and not self.items[self.current_item].is_bought:
            self.game.money -= self.items[self.current_item].price
            self.items[self.current_item].is_bought = True

    def to_next(self):
        if self.current_item != len(self.items) - 1:
            self.current_item += 1
        if self.items[self.current_item].is_using:
            self.put_on_button.text = text_render("Снять", self.put_on_button.text_font)
        else:
            self.put_on_button.text = text_render("Надеть", self.put_on_button.text_font)

    def to_back(self):
        if self.current_item != 0:
            self.current_item -= 1
        if self.items[self.current_item].is_using:
            self.put_on_button.text = text_render("Снять", self.put_on_button.text_font)
        else:
            self.put_on_button.text = text_render("Надеть", self.put_on_button.text_font)

    def update(self):
        for button in self.buttons:
            button.update()

    def is_clicked(self, event):
        for button in self.buttons:
            button.is_clicked(event)

    def draw(self, screen):
        screen.blit(self.menu_page, (0, 0))

        screen.blit(self.items[self.current_item].image, self.item_rect)

        if self.items[self.current_item].is_bought:
            screen.blit(self.bottom_label_on, (0, 0))
        else:
            screen.blit(self.bottom_label_off, (0, 0))

        if self.items[self.current_item].is_using:
            screen.blit(self.top_label_on, (0, 0))
        else:
            screen.blit(self.top_label_off, (0, 0))

        self.text_put_on = text_render("Надето", font)
        self.text_put_on_rect = self.text_put_on.get_rect()
        self.text_put_on_rect.center = (700, 125)
        screen.blit(self.text_put_on, self.text_put_on_rect)

        self.text_bought = text_render("Куплено", font)
        self.text_bought_rect = self.text_bought.get_rect()
        self.text_bought_rect.center = (700, 200)
        screen.blit(self.text_bought, self.text_bought_rect)

        self.text_name = text_render(self.items[self.current_item].name, font)
        self.text_name_rect = self.text_name.get_rect()
        self.text_name_rect.center = (450, 125)
        screen.blit(self.text_name, self.text_name_rect)

        self.text_price = text_render(self.items[self.current_item].price, font)
        self.text_price_rect = self.text_price.get_rect()
        self.text_price_rect.center = (450, 180)
        screen.blit(self.text_price, self.text_price_rect)

        self.next_button.draw(screen)
        self.back_button.draw(screen)
        self.put_on_button.draw(screen)
        self.buy_button.draw(screen)


class Button:
    def __init__(self, text, x, y, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=font, func=None):
        self.idle_image = load_image("images/button.png", width, height)
        self.pressed_image = load_image("images/button_clicked.png", width, height)
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.text_font = text_font
        self.text = text_render(text, self.text_font)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.rect.center

        self.is_pressed = False
        self.func = func

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if self.is_pressed:
                self.image = self.pressed_image
            else:
                self.image = self.idle_image

    def is_clicked(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                if self.func:
                    self.func()

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = False


class Game:
    def __init__(self):

        # Создание окна
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Виртуальный питомец")

        with open("save.json", encoding="utf-8") as f:
            data = json.load(f)

        self.happiness = data["happiness"]
        self.hunger = data["hunger"]
        self.health = data["health"]
        self.money = data["money"]
        self.coins_per_second = data["coins_per_second"]
        self.costs_of_upgrade = {}

        for key, value in data["costs_of_upgrade"].items():
            self.costs_of_upgrade[int(key)] = value

        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.happiness_image = load_image("images/happiness.png", ICON_SIZE, ICON_SIZE)
        self.hunger_image = load_image("images/hunger.png", ICON_SIZE, ICON_SIZE)
        self.health_image = load_image("images/health.png", ICON_SIZE, ICON_SIZE)
        self.money_image = load_image("images/money.png", ICON_SIZE, ICON_SIZE)
        self.dog = load_image("images/dog.png", DOG_WIDTH, DOG_HEIGHT)

        self.mode = "Main"

        button_x = SCREEN_WIDTH - BUTTON_WIDTH - PADDING

        self.buttons = list()
        self.eat_button = Button("Еда", button_x, PADDING + ICON_SIZE, func=self.food_menu_on)
        self.buttons.append(self.eat_button)
        self.clothes_button = Button("Одежда", button_x, PADDING + ICON_SIZE * 2, func=self.clothes_menu_on)
        self.buttons.append(self.clothes_button)
        self.games_button = Button("Игры", button_x, PADDING + ICON_SIZE * 3, func=self.game_on)
        self.buttons.append(self.games_button)

        self.upgrade_button = Button("Улучшить", SCREEN_WIDTH - ICON_SIZE, 0,
                                     width=BUTTON_WIDTH // 3, height=BUTTON_HEIGHT // 3,
                                     text_font=font_mini, func=self.increase_money)
        self.buttons.append(self.upgrade_button)

        self.clothes_menu = ClothesMenu(self, data["clothes"])
        self.food_menu = FoodMenu(self)
        self.mini_game = MiniGame(self)

        self.INCREASE_MONEY = pg.USEREVENT + 1
        pg.time.set_timer(self.INCREASE_MONEY, 1000)

        self.DECREASE = pg.USEREVENT + 1
        pg.time.set_timer(self.DECREASE, 1000)

        self.clock = pg.time.Clock()

        self.run()

    def clothes_menu_on(self):
        self.mode = "Clothes menu"

    def food_menu_on(self):
        self.mode = "Food menu"

    def game_on(self):
        self.mode = "Mini game"
        self.mini_game.new_game()

    def run(self):
        while True:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def increase_money(self):
        for cost in self.costs_of_upgrade:
            check = self.costs_of_upgrade[cost]
            if not check and self.money > cost:
                self.money -= cost
                self.costs_of_upgrade[cost] = True
                self.coins_per_second += 1
                break

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.mode == "Game over":
                    data = {
                        "happiness": 100,
                        "hunger": 100,
                        "health": 100,
                        "money": 10,
                        "coins_per_second": 1,
                        "costs_of_upgrade": {
                            "100": False,
                            "1000": False,
                            "5000": False,
                            "10000": False
                        },
                        "clothes": [
                            {
                                "name": "Синяя футболка",
                                "price": 10,
                                "image": "images/items/blue t-shirt.png",

                                "is_using": False,
                                "is_bought": False
                            },
                            {
                                "name": "Ботинки",
                                "price": 50,
                                "image": "images/items/boots.png",

                                "is_using": False,
                                "is_bought": False
                            },
                            {
                                "name": "Шляпа",
                                "price": 50,
                                "image": "images/items/hat.png",

                                "is_using": False,
                                "is_bought": False
                            }
                        ]
                    }

                else:
                    data = {
                        "happiness": self.happiness,
                        "hunger": self.hunger,
                        "health": self.health,
                        "money": self.money,
                        "coins_per_second": self.coins_per_second,
                        "costs_of_upgrade": {
                            "100": self.costs_of_upgrade[100],
                            "1000": self.costs_of_upgrade[1000],
                            "5000": self.costs_of_upgrade[5000],
                            "10000": self.costs_of_upgrade[10000]
                        },
                        "clothes": []
                    }
                    for item in self.clothes_menu.items:
                        data["clothes"].append({"name": item.name,
                                                "price": item.price,
                                                "image": item.file,
                                                "is_using": item.is_using,
                                                "is_bought": item.is_bought})
                with open("save.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.mode = "Main"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.money += self.coins_per_second

            if event.type == self.INCREASE_MONEY:
                self.money += self.coins_per_second
            if event.type == self.DECREASE:
                chance = random.randint(1, 10)
                if chance <= 5:
                    self.hunger -= 1
                elif 5 < chance <= 9:
                    self.happiness -= 1
                else:
                    self.health -= 1

            if self.mode == "Main":
                for button in self.buttons:
                    button.is_clicked(event)

            elif self.mode == "Clothes menu":
                self.clothes_menu.is_clicked(event)

            elif self.mode == "Food menu":
                self.food_menu.is_clicked(event)

            def update(self):
                if self.mode == "Clothes menu":
                    self.clothes_menu.update()

                elif self.mode == "Food menu":
                    self.food_menu.update()

                elif self.mode == "Mini game":
                    self.mini_game.update()

                else:
                    for button in self.buttons:
                        button.update()

                if self.hunger <= 0 or self.happiness <= 0 or self.health <= 0:
                    self.mode = "Game over"

            def draw(self):
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.happiness_image, (PADDING, PADDING))
                self.screen.blit(text_render(self.happiness), (PADDING + ICON_SIZE, PADDING * 6))

                self.screen.blit(self.hunger_image, (PADDING, PADDING + ICON_SIZE * 1))
                self.screen.blit(text_render(self.hunger), (PADDING + ICON_SIZE, PADDING * 6 + ICON_SIZE))

                self.screen.blit(self.health_image, (PADDING, PADDING + ICON_SIZE * 2))
                self.screen.blit(text_render(self.health), (PADDING + ICON_SIZE, PADDING * 6 + ICON_SIZE * 2))

                self.screen.blit(self.money_image, (SCREEN_WIDTH - PADDING - ICON_SIZE, PADDING))
                self.screen.blit(text_render(self.money), (SCREEN_WIDTH - PADDING * 10 - ICON_SIZE, PADDING * 6))

                self.screen.blit(self.dog, (SCREEN_WIDTH // 2 - 155, 100))

                for item in self.clothes_menu.items:
                    if item.is_using:
                        self.screen.blit(item.full_image, (SCREEN_WIDTH // 2 - 155, 100))

                for button in self.buttons:
                    button.draw(self.screen)

                if self.mode == "Clothes menu":
                    self.clothes_menu.draw(self.screen)

                if self.mode == "Food menu":
                    self.food_menu.draw(self.screen)

                if self.mode == "Mini game":
                    self.mini_game.draw(self.screen)

                if self.mode == "Game over":
                    text = font_maxi.render("Game over", True, "red")
                    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    self.screen.blit(text, text_rect)

                pg.display.flip()

        if __name__ == "__main__":
            Game()
