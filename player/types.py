from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Food:
    food_type: int
    amount: int


@dataclass
class FoodPoint:
    food: Food
    coord: Point


@dataclass
class Enemy:
    attack: int
    food: Food
    health: int
    coord: Point
    type: int
