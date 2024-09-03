import pygame

from game.sprite import Sprite


class TestPlayer(Sprite):
    active_elements : list['TestPlayer'] = []
    inactive_elements : list['TestPlayer'] = []
    #load assets
    test_image : pygame.Surface = pygame.surface.Surface((50, 50))
    pygame.draw.rect(test_image, "Red", (0,0, 50, 50))

    def __init__(self) -> None:
        super().__init__()
        TestPlayer.inactive_elements.append(self)

    @classmethod
    def spawn(cls, new_pos : pygame.Vector2):
        element = cls.inactive_elements[0]

        element.image = cls.test_image
        element.rect = element.image.get_rect()

        element.position = new_pos
        element.align_rect()
        element.zindex = 0

        cls.unpool(element)
        return element
    
    def update(self, delta: float):
        keyboard_map = pygame.key.get_pressed()
        move_vector : pygame.Vector2 = pygame.Vector2(0,0)
        speed : int = 5
        if keyboard_map[pygame.K_a]:
            move_vector += pygame.Vector2(-1, 0)
        if keyboard_map[pygame.K_d]:
            move_vector += pygame.Vector2(1, 0)
        if keyboard_map[pygame.K_s]:
            move_vector += pygame.Vector2(0, 1)
        if keyboard_map[pygame.K_w]:
            move_vector += pygame.Vector2(0, -1)
        if move_vector.magnitude(): move_vector.normalize()
        self.position += move_vector * speed * delta
        self.align_rect()
    
    def clean_instance(self):
        self.image = None
        self.rect = None

        self.position = pygame.Vector2(0,0)
        self.zindex = None

Sprite.register_class(TestPlayer)