import pygame
import os
import json
from agents import NPC

rootFolder = os.path.dirname(os.path.realpath(__file__))
chunk_size = (10, 10)  # Each chunk is 10x10 tiles
tile_size = (50, 50)  # Each tile is 50x50 pixels


def world_generation():
    with open(os.path.join(rootFolder, "data", "world_chunk.json"), "r") as file:
        world_chunks_data = json.load(file)

    chunks = []
    for chunk_data in world_chunks_data:
        chunk_position = (
            chunk_data["position"][0] * 500,  # Convert chunk coordinates to world coordinates
            chunk_data["position"][1] * 500,
        )
        tile_map = chunk_data["tile"]
        npcs_data = chunk_data.get("npc", [])  # Get NPC data for this chunk
        chunks.append(Chunk(chunk_position, chunk_size, tile_size, tile_map, npcs_data))
    return chunks

class Chunk:
    def __init__(self, position, chunk_size, tile_size, tile_map, npcs_data):
        self.position = position  # (x, y) position of the chunk in world space
        self.chunk_size = chunk_size  # (width, height) in tiles
        self.tile_size = tile_size  # (width, height) of each tile
        self.tiles = []  # List to store tiles in this chunk
        self.npcs = []  # List to store NPCs in this chunk

        # Generate tiles based on the tile_map
        for row_index, row in enumerate(tile_map):
            for col_index, tile_type in enumerate(row):
                tile_position = (
                    position[0] + col_index * tile_size[0],
                    position[1] + row_index * tile_size[1],
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
                position[0] + npc_data["tile"][0] * tile_size[0],
                position[1] + npc_data["tile"][1] * tile_size[1],
            )
            # Apply the tile_offset
            npc_position = (
                npc_tile_position[0] + npc_data["tile_offset"][0],
                npc_tile_position[1] + npc_data["tile_offset"][1],
            )

            name = npc_data["name"] if "name" in npc_data else "Unknown"
            detection = npc_data["detection"] if "detection" in npc_data else 60
            self.npcs.append(NPC(npc_position, detection, name, npc_data["dialogue"]))

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
            self.position[0] - camera_offset.x,
            self.position[1] - camera_offset.y,
        )

        # Draw chunk coordinates
        text_surface = font.render(f"X: {self.position[0] // 500}, Y: {self.position[1] // 500}", True, (255, 255, 255))
        screen.blit(text_surface, (chunk_screen_pos[0] + 10, chunk_screen_pos[1] + 10))

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