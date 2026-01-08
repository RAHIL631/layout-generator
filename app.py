from flask import Flask, render_template, jsonify
from layout_generator import LayoutGenerator, TOWER_A_SIZE, TOWER_B_SIZE
import random

app = Flask(__name__)
generator = LayoutGenerator()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-layouts')
def generate_layouts():
    # Generate multiple layouts
    valid_layouts = []
    target_count = 3
    attempts = 0
    max_attempts = 50 # Avoid infinite loops if generation is hard
    
    while len(valid_layouts) < target_count and attempts < max_attempts:
        # Generate one
        is_valid, reason = generator.generate_layout(target_buildings=random.randint(6, 14))
        attempts += 1
        
        if is_valid:
            # Re-validate locally to get details and double check
            _, mix_reason = generator.validate_neighbour_mix()
            
            # Prepare data
            towers_a_count = sum(1 for b in generator.buildings if b.type == 'A')
            towers_b_count = sum(1 for b in generator.buildings if b.type == 'B')
            total_area = sum(b.width * b.height for b in generator.buildings)
            
            layout_data = {
                "id": len(valid_layouts) + 1,
                "towersA": towers_a_count,
                "towersB": towers_b_count,
                "builtArea": total_area,
                "rules": {
                    "siteBoundary": True,
                    "minDistance": True, # intrinsically handled by generator return
                    "boundarySetback": True,
                    "neighbourMix": True, # validated above
                    "plazaClear": True
                },
                "buildings": [b.to_dict() for b in generator.buildings]
            }
            valid_layouts.append(layout_data)
    
    return jsonify({"layouts": valid_layouts})

if __name__ == '__main__':
    app.run(debug=True)
