import pygame
import os
import json
from agents import AGENT
from typing import List

render_distance = 1  # Number of chunks to render around the player
chunk_size = (10, 10)  # Each chunk is 10x10 tiles
tile_size = (50, 50)  # Each tile is 50x50 pixels

root = os.path.dirname(os.path.abspath(__file__))
def world_generation():
    with open(os.path.join(root, "data", "world.json"), "r") as file:
        world_chunks_data = json.load(file)

    with open(os.path.join(root, "data", "agents.json"), "r") as file:
        agents_data = json.load(file)

    chunks = []
    for chunk_data in world_chunks_data:
        chunk_position = (
            chunk_data["position"][0] * 500,  # Convert chunk coordinates to world coordinates
            chunk_data["position"][1] * 500,
        )
        chunk_roomIdentifier = chunk_data["roomIdentifier"] if "roomIdentifier" in chunk_data else ""
        tile_map = chunk_data["tile"]

        # Filter agents for this chunk
        npcs_data = [
            agent for agent in agents_data
            if agent["chunk_position"] == chunk_data["position"]  # Match chunk position
        ]

        chunks.append(Chunk(chunk_position, chunk_size, chunk_roomIdentifier, tile_size, tile_map, npcs_data))
    return chunks

def get_visible_chunks(player_position, chunks):
    """Return chunks within a 5-chunk radius of the player's position."""
    visible_chunks = []
    player_chunk_x = player_position[0] // (chunk_size[0] * tile_size[0])
    player_chunk_y = player_position[1] // (chunk_size[1] * tile_size[1])

    for chunk in chunks:
        chunk_x = chunk.chunk_position[0] // (chunk_size[0] * tile_size[0])
        chunk_y = chunk.chunk_position[1] // (chunk_size[1] * tile_size[1])

        if abs(chunk_x - player_chunk_x) <= render_distance and abs(chunk_y - player_chunk_y) <= render_distance:
            visible_chunks.append(chunk)

    return visible_chunks

class Chunk:
    def __init__(self, chunk_position, chunk_size, chunk_roomIdentifier, tile_size, tile_map, npcs_data):
        self.chunk_position = chunk_position  # (x, y) position of the chunk in world space
        self.chunk_size = chunk_size  # (width, height) in tiles
        self.chunk_roomIdentifier = chunk_roomIdentifier  # (width, height) of each tile
        self.tile_size = tile_size  # (width, height) of each tile
        self.tiles = []  # List to store tiles in this chunk
        self.npcs = []  # List to store NPCs in this chunk

        # Generate tiles based on the tile_map
        for row_index, row in enumerate(tile_map):
            for col_index, tile_type in enumerate(row):
                tile_position = (
                    chunk_position[0] + col_index * tile_size[0],
                    chunk_position[1] + row_index * tile_size[1],
                )
                if tile_type == 0:  # Floor
                    self.tiles.append(Tile(tile_position, tile_size, "floor", walkable=True))
                elif tile_type == 1:  # Wall
                    self.tiles.append(Tile(tile_position, tile_size, "wall", walkable=False))
                elif tile_type == 2:  # Hole
                    self.tiles.append(Tile(tile_position, tile_size, "furniture", walkable=False))

        # Load NPCs from the JSON data
        for npc_data in npcs_data:
            npc_tile_position = (
                chunk_position[0] + npc_data["tile"][0] * tile_size[0],
                chunk_position[1] + npc_data["tile"][1] * tile_size[1],
            )
            # Apply the tile_offset
            npc_position = (
                npc_tile_position[0] + npc_data["tile_offset"][0],
                npc_tile_position[1] + npc_data["tile_offset"][1],
            )

            name = npc_data["name"] if "name" in npc_data else "Unknown"
            profession = npc_data["profession"] if "profession" in npc_data else "none"
            detection = npc_data["detection"] if "detection" in npc_data else 60
            self.npcs.append(AGENT(npc_position, detection, name, profession, npc_data["dialogue"]))

    def draw(self, screen, camera_offset):
        """Draw all tiles and NPCs in this chunk."""
        # Draw tiles
        for tile in self.tiles:
            if tile.tile_type == "floor":
                tile.draw(screen, camera_offset, "gray")
            elif tile.tile_type == "wall":
                tile.draw(screen, camera_offset, "black")
            elif tile.tile_type == "furniture":
                tile.draw(screen, camera_offset, "antiquewhite4")

        # Draw NPCs
        for npc in self.npcs:
            npc.draw(screen, camera_offset)

    def draw_debug_info(self, screen, camera_offset, font):
        """Draw debug information and grid lines for the chunk."""
        chunk_screen_pos = (
            self.chunk_position[0] - camera_offset.x,
            self.chunk_position[1] - camera_offset.y,
        )

        # Draw chunk coordinates
        text_surface = font.render(f"X: {self.chunk_position[0] // 500}, Y: {self.chunk_position[1] // 500}", True, (255, 255, 255))
        screen.blit(text_surface, (chunk_screen_pos[0] + 10, chunk_screen_pos[1] + 10))

        text_surface = font.render(f"{self.chunk_roomIdentifier}", True, (255, 255, 255))
        screen.blit(text_surface, (chunk_screen_pos[0] + 10, chunk_screen_pos[1] + 35))

        # Draw grid lines around the chunk
        chunk_width = self.chunk_size[0] * self.tile_size[0]
        chunk_height = self.chunk_size[1] * self.tile_size[1]
        pygame.draw.rect(
            screen,
            (255, 255, 255),  # White color for the grid lines
            (
                chunk_screen_pos[0],
                chunk_screen_pos[1],
                chunk_width,
                chunk_height,
            ),
            1,  # Line thickness
        )

class Tile:
    def __init__(self, position, size, tile_type="floor", walkable=True):
        self.position = position  # (x, y) position of the tile
        self.size = size  # Size of the tile (width, height)
        self.tile_type = tile_type  # "floor", "hole", "wall"
        self.walkable = walkable  # Whether the tile is walkable

    def draw(self, screen, camera_offset, color):
        """Draw the tile on the screen."""
        screen_pos = (self.position[0] - camera_offset.x, self.position[1] - camera_offset.y)
        pygame.draw.rect(screen, color, (screen_pos[0], screen_pos[1], self.size[0], self.size[1]))