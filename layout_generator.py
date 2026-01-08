import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# --- Constants & Rules ---
SITE_WIDTH = 200
SITE_HEIGHT = 140
SITE_ORIGIN = (0, 0)
BOUNDARY_SETBACK = 10
MIN_BUILDING_DISTANCE = 15
PLAZA_SIZE = 40
TOWER_A_SIZE = (30, 20)  # Width, Height
TOWER_B_SIZE = (20, 20)  # Width, Height
NEIGHBOUR_MIX_DISTANCE = 60

class Building:
    def __init__(self, x, y, width, height, b_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = b_type  # 'A' or 'B'

    @property
    def bounds(self):
        # Returns (min_x, min_y, max_x, max_y)
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    @property
    def centroid(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    def intersects(self, other_bounds):
        # other_bounds is (min_x, min_y, max_x, max_y)
        # Check standard AABB intersection
        min_x1, min_y1, max_x1, max_y1 = self.bounds
        min_x2, min_y2, max_x2, max_y2 = other_bounds

        return not (max_x1 <= min_x2 or max_x2 <= min_x1 or
                    max_y1 <= min_y2 or max_y2 <= min_y1)

    def distance_to(self, other_building):
        # Calculate edge-to-edge distance
        # 1. Get ranges
        x1_min, y1_min, x1_max, y1_max = self.bounds
        x2_min, y2_min, x2_max, y2_max = other_building.bounds

        # 2. Calculate delta x
        if x1_max < x2_min:
            dx = x2_min - x1_max
        elif x2_max < x1_min:
            dx = x1_min - x2_max
        else:
            dx = 0  # Overlap in X

        # 3. Calculate delta y
        if y1_max < y2_min:
            dy = y2_min - y1_max
        elif y2_max < y1_min:
            dy = y1_min - y2_max
        else:
            dy = 0  # Overlap in Y

        return np.sqrt(dx**2 + dy**2)
    
    def to_dict(self):
        return {
            'type': self.type,
            'x': self.x,
            'y': self.y,
            'w': self.width,
            'h': self.height
        }


class Plaza:
    def __init__(self):
        # Centered plaza
        self.width = PLAZA_SIZE
        self.height = PLAZA_SIZE
        # Near center of site (loosely interpreted as centered for now, 
        # or we could randomize slightly if "somewhere near center" implies variability. 
        # Let's effectively center it for strict compliance with "near the center" usually meaning center.)
        self.x = (SITE_WIDTH - self.width) / 2
        self.y = (SITE_HEIGHT - self.height) / 2
    
    @property
    def bounds(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

class LayoutGenerator:
    def __init__(self):
        self.buildings = []
        self.plaza = Plaza()

    def is_valid_position(self, building):
        # Rule 1: Site Containment & Rule 3: Boundary Setback
        # Effectively, the building must be within (SITE_ORIGIN + setback) to (SITE_MAX - setback)
        min_x = BOUNDARY_SETBACK
        max_x = SITE_WIDTH - BOUNDARY_SETBACK
        min_y = BOUNDARY_SETBACK
        max_y = SITE_HEIGHT - BOUNDARY_SETBACK

        bx, by, bx_max, by_max = building.bounds
        
        if bx < min_x or by < min_y or bx_max > max_x or by_max > max_y:
            return False, "Boundary Violation"

        # Rule 5: Central Plaza Reservation
        # No intersection with plaza
        if building.intersects(self.plaza.bounds):
             return False, "Plaza Overlap"

        # Rule 2: Inter-Building Distance
        for other in self.buildings:
            dist = building.distance_to(other)
            if dist < MIN_BUILDING_DISTANCE:
                return False, f"Too Close to Building ({dist:.2f}m)"
        
        return True, "Valid"

    def validate_neighbour_mix(self):
        # Rule 4: Neighbour-Mix Rule
        # For every Tower A, there must exist at least one Tower B located within a distance of 60 meters.
        # We will use centroid-to-centroid for this calculation as permitted, 
        # or edge-to-edge. Let's stick to edge-to-edge as it is safer for "closeness", 
        # but the prompt allows either. Let's use EDGE-TO-EDGE to match Rule 2 logic style.
        # Wait, prompt says: "Distance may be calculated using: edge-to-edge distance, or centroid-to-centroid distance. The same method must be applied consistently across the project."
        # I used edge-to-edge for Rule 2. I should probably use edge-to-edge here too for consistency.
        
        tower_as = [b for b in self.buildings if b.type == 'A']
        tower_bs = [b for b in self.buildings if b.type == 'B']

        if not tower_as:
            return True, "No Tower A present"

        for ta in tower_as:
            has_neighbour = False
            for tb in tower_bs:
                # Using edge-to-edge
                if ta.distance_to(tb) <= NEIGHBOUR_MIX_DISTANCE:
                    has_neighbour = True
                    break
            if not has_neighbour:
                return False, "Neighbour-Mix Violation"
        
        return True, "Valid"

    def generate_layout(self, num_attempts=1000, target_buildings=10):
        # Simple Logic: 
        # 1. Clear buildings
        # 2. Try to place buildings randomly
        # 3. Ensure we have a mix of A and B
        
        self.buildings = []
        
        # We want a mix. Let's try to place a random number of A and B
        # Or just keep adding until we can't or hit a limit?
        # Let's try to add specific counts for better control, or random.
        # The goal is "Maximize density" or just "Explore many configurations". 
        # Let's try to place as many as possible up to a limit.
        
        failed_attempts = 0
        while len(self.buildings) < target_buildings and failed_attempts < 100:
            # Pick type
            b_type = random.choice(['A', 'B'])
            w, h = (TOWER_A_SIZE if b_type == 'A' else TOWER_B_SIZE)
            
            # Random position (respecting naive bounds to avoid immediate rejection)
            # Valid range for x: 10 to 200-10-width
            min_x = BOUNDARY_SETBACK
            max_x = SITE_WIDTH - BOUNDARY_SETBACK - w
            min_y = BOUNDARY_SETBACK
            max_y = SITE_HEIGHT - BOUNDARY_SETBACK - h
            
            if max_x < min_x or max_y < min_y:
                break # Should not happen with these sizes
                
            rx = random.uniform(min_x, max_x)
            ry = random.uniform(min_y, max_y)
            
            new_b = Building(rx, ry, w, h, b_type)
            
            is_valid, reason = self.is_valid_position(new_b)
            if is_valid:
                self.buildings.append(new_b)
                failed_attempts = 0 # Reset counter on success
            else:
                failed_attempts += 1
        
        # After filling, check global rules (Neighbour Mix)
        valid_mix, mix_reason = self.validate_neighbour_mix()
        return valid_mix, mix_reason

    def visualize(self, layout_id):
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Draw Site
        site_rect = patches.Rectangle((0, 0), SITE_WIDTH, SITE_HEIGHT, linewidth=2, edgecolor='black', facecolor='none', label='Site Boundary')
        ax.add_patch(site_rect)
        
        # Draw Setback Line (Optional, but good for visualization)
        setback_rect = patches.Rectangle((BOUNDARY_SETBACK, BOUNDARY_SETBACK), SITE_WIDTH - 2*BOUNDARY_SETBACK, SITE_HEIGHT - 2*BOUNDARY_SETBACK, linewidth=1, edgecolor='gray', linestyle='--', facecolor='none', label='Setback Limit')
        ax.add_patch(setback_rect)

        # Draw Plaza
        plaza_rect = patches.Rectangle((self.plaza.x, self.plaza.y), self.plaza.width, self.plaza.height, linewidth=2, edgecolor='purple', facecolor='violet', alpha=0.5, label='Central Plaza')
        ax.add_patch(plaza_rect)
        ax.text(self.plaza.x + self.plaza.width/2, self.plaza.y + self.plaza.height/2, 'Plaza', ha='center', va='center', color='purple', fontsize=10, weight='bold')

        # Draw Buildings
        count_a = 0
        count_b = 0
        area = 0
        
        for b in self.buildings:
            color = 'blue' if b.type == 'A' else 'green'
            label = f'Tower {b.type}'
            if b.type == 'A': count_a += 1
            else: count_b += 1
            area += b.width * b.height
            
            b_rect = patches.Rectangle((b.x, b.y), b.width, b.height, linewidth=1, edgecolor='black', facecolor=color, alpha=0.7)
            ax.add_patch(b_rect)
            ax.text(b.x + b.width/2, b.y + b.height/2, b.type, ha='center', va='center', color='white', weight='bold')

        # Stats
        valid, reason = self.validate_neighbour_mix() # Re-check
        status_text = "SATISFIED" if valid else f"VIOLATED ({reason})"
        status_color = "green" if valid else "red"
        
        stats = (
            f"Layout ID: {layout_id}\n"
            f"Tower A: {count_a}\n"
            f"Tower B: {count_b}\n"
            f"Total Area: {area} sqm\n"
            f"Rule Status: {status_text}"
        )
        
        plt.title(f"Generated Layout #{layout_id}", fontsize=14)
        # Place text outside or in a corner
        plt.figtext(0.02, 0.02, stats, fontsize=10,  bbox=dict(facecolor='white', alpha=0.8, edgecolor=status_color))

        plt.xlim(-10, SITE_WIDTH + 10)
        plt.ylim(-10, SITE_HEIGHT + 10)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(True, linestyle=':', alpha=0.6)
        
        # Custom legend to avoid duplicates
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        # Add building types manually if not in legend yet
        if 'Tower A' not in by_label and count_a > 0:
             by_label['Tower A'] = patches.Rectangle((0,0),1,1, facecolor='blue', alpha=0.7)
        if 'Tower B' not in by_label and count_b > 0:
             by_label['Tower B'] = patches.Rectangle((0,0),1,1, facecolor='green', alpha=0.7)
             
        plt.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        plt.tight_layout()
        # Save to file
        filename = f'layout_{layout_id}.png'
        plt.savefig(filename)
        print(f"Saved visualization to {filename}")
        plt.close(fig) # Close to free memory

if __name__ == "__main__":
    generator = LayoutGenerator()
    
    # Generate a few valid layouts
    valid_layouts_found = 0
    target_layouts = 3
    
    print("Starting generation...")
    
    while valid_layouts_found < target_layouts:
        # Heavily randomized attempts
        is_valid, reason = generator.generate_layout(target_buildings=random.randint(5, 15))
        
        if is_valid:
            valid_layouts_found += 1
            print(f"Found valid layout #{valid_layouts_found}")
            generator.visualize(valid_layouts_found)
        else:
             # Optional: print(f"Failed attempt: {reason}")
             pass

    print("Generation Complete.")
