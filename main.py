# Example file showing a basic pygame "game loop"
import pygame
import random
import math

# pygame setup
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True

#collision
collision_objects = []

#Player
player_pos = pygame.Vector2(0,0)
player_rect = pygame.Rect((player_pos.x, player_pos.y, 100, 100))
player_vel = pygame.Vector2(0,0)
player_drag = 0.9
player_mass = 0.1
is_grounded = False

check_y = 0
check_x = [0,0]

#shotgun
shotgun_pos = pygame.Vector2(0,0)
shotgun_img = pygame.transform.scale(pygame.image.load("shotgun_normal.png").convert_alpha(), (87, 18))
shotgun_img_inverted = pygame.transform.scale(pygame.image.load("shotgun_inverted.png").convert_alpha(), (87, 18))
shotgun_sound = pygame.mixer.Sound("shotgun_fire.wav")

def calculate_shotgun_angle():
    #Calculate direction of mouse cursor from shotgun, then calculate angle
    mouse_pos = pygame.mouse.get_pos()
    dx = mouse_pos[0] - shotgun_pos[0]
    dy = mouse_pos[1] - shotgun_pos[1]
    angle = math.degrees(math.atan2(-dy, dx))
    return angle

#bullets
bullet_image = pygame.image.load("bullet.png")
bullets = []

class bullet():
    def __init__(self, n_pos, n_velocity, n_force) -> None:
        self.velocity = n_velocity
        self.pos = n_pos
        self.force = n_force
    
    def update(self):
        #increase position over lifetime
        self.pos += self.velocity * self.force

        #draw image an store as rect for collisions
        bullet_rect = screen.blit(bullet_image, self.pos)

        #check if we hit into anything.
        if bullet_rect.collidelist(collision_objects) != -1: #meaning that we have hit a wall
            #remove self from bullets list
            bullets.remove(self)

        #if hit enemy
            #enemy.kill

#Floor
floor_pos = pygame.Vector2(0, height - 100)
floor_rect = pygame.Rect((floor_pos.x, floor_pos.y, width, 100))
collision_objects.append(floor_rect)

#blocks
for i in range(5):
    block_pos = pygame.Vector2(random.randrange(0, width - 100), random.randrange(0, height - 100))
    block_rect = pygame.Rect((block_pos.x, block_pos.y, 100, 100))
    collision_objects.append(block_rect)


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN: #SHOOT
            if event.button == 1:
                #Calculate direction of mouse cursor from player
                #Normalise direction and then apply to player_vel * 20
                cursor_pos = pygame.mouse.get_pos()
                target_dir = pygame.Vector2(cursor_pos[0] - player_rect.centerx, cursor_pos[1] - player_rect.centery)
                target_dir = target_dir.normalize()
                player_vel += -target_dir * 25
                is_grounded = False

                #Effects and sound
                shotgun_sound.play()

                #Instantiate bullet
                bullets.append(bullet(shotgun_pos, target_dir, 15))


    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # RENDER YOUR GAME HERE

    #draw collision objects
    #Run through list of all collision obejcts and draw them within the level
    for i in range(len(collision_objects)):
        pygame.draw.rect(screen, "grey", collision_objects[i])

    #collision + gravity
    collision_index = player_rect.collidelist(collision_objects)
    if collision_index != -1: #Meaning that there is a collision
        #Check if we hit from the top, sides, or bottom
        collided_object = collision_objects[collision_index]
        # Calculate the depths of overlap on each side
        overlap_left = collided_object.right - player_rect.left
        overlap_right = player_rect.right - collided_object.left
        overlap_top = collided_object.bottom - player_rect.top
        overlap_bottom = player_rect.bottom - collided_object.top
        print("col")

        # Find the minimum overlap
        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        # Adjust the position of the moving rectangle based on the collision side
        if min_overlap == overlap_left: #player collided with right
            player_vel.x = -player_vel.x * 0.4
            player_pos.x = collided_object.x + 100
        elif min_overlap == overlap_right: #player collided with left
            player_vel.x = -player_vel.x * 0.4
            player_pos.x = collided_object.x - 100
        elif min_overlap == overlap_top: #player collided with bottom
            player_pos.y = collided_object.top + 100
            player_vel.y = 0
        elif min_overlap == overlap_bottom: #player collided with top
            player_vel.y = 0
            player_pos.y = collided_object.top - 100
            is_grounded = True

            #Store top and sides of collision object for later use...
            check_y = collided_object.top
            check_x = [collided_object.left,collided_object.right]

        else:
            is_grounded = False

    elif not is_grounded: #Meaning that there are no collisions
        #Apply gravity
        player_vel.y += 9.81 * player_mass
    else: #This area fixes the bug where the player would slide on the air, after being grounded.
        #Check if we are still grounded (on top of object)...
        #If the player is still on the y-level of the object, we check to see
        #if the left and right sides of the player are within the left and right
        #sides of the object. If they both aren't, we are no longer on an object.
        if player_rect.bottom == check_y:
            if (player_rect.left < check_x[0] and player_rect.right < check_x[0]):
                is_grounded = False
            elif (player_rect.left > check_x[1] and player_rect.right > check_x[1]):
                is_grounded = False

    #player draw - draw at player_pos each frame
    player_rect = pygame.Rect((player_pos.x, player_pos.y, 100, 100))
    pygame.draw.rect(screen, "blue", player_rect)
    player_pos += player_vel

    #shotgun draw
    #Calculate angle that shotgun must face and assign to variable.
    shotgun_pos = player_rect.center
    angle = calculate_shotgun_angle()

    #update bullets
    for bullet_ in bullets:
        bullet_.update()

    #Here, image is rotated by angle variable, and shotgun_rect is centered.

    #If angle surpasses top or bottom of player, rotate inverted image...
    if angle > 90 or angle < -90:
        rotated_shotgun = pygame.transform.rotate(shotgun_img_inverted, angle)
        shotgun_rect = rotated_shotgun.get_rect(center=player_rect.center)
    else: #Rotate normal image...
        rotated_shotgun = pygame.transform.rotate(shotgun_img, angle)
        shotgun_rect = rotated_shotgun.get_rect(center=player_rect.center)

    #Draw newly rotated shotgun...
    screen.blit(rotated_shotgun, shotgun_rect.topleft)

    #Apply drag to player velocity
    player_vel *= player_drag

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()