import random
import pygame
from main import PLAYER_SIZE, Target, move_point, random_target, target_is_collected


def test_move_point_uses_elapsed_time():
    x, y = move_point(100, 100, 1, 0, 200, 0.5)
    assert x == 200
    assert y == 100


def test_move_point_wraps_after_right_edge():
    x, y = move_point(601, 100, 1, 0, 10, 0.01, width=600, height=400, size=20)
    assert x == -20
    assert y == 100


def test_move_point_wraps_after_left_edge():
    x, y = move_point(-21, 100, -1, 0, 10, 0.01, width=600, height=400, size=20)
    assert x == 600
    assert y == 100


def test_target_is_collected_when_overlapping_player():
    rect = pygame.Rect(100, 100, PLAYER_SIZE, PLAYER_SIZE)
    assert target_is_collected(rect, Target(110, 110))


def test_target_is_not_collected_when_far_away():
    rect = pygame.Rect(100, 100, PLAYER_SIZE, PLAYER_SIZE)
    assert not target_is_collected(rect, Target(300, 300))


def test_random_target_stays_inside_margins():
    target = random_target(random.Random(123), width=900, height=600, margin=55)
    assert 55 <= target.x <= 845
    assert 105 <= target.y <= 545
