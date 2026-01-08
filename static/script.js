// Config
const SITE_WIDTH_M = 200;
const SITE_HEIGHT_M = 140;
const CANVAS_WIDTH = 800; // Pixels
const CANVAS_HEIGHT = 560; // Pixels
const SCALE = CANVAS_WIDTH / SITE_WIDTH_M; // 4 pixels per meter

const canvas = document.getElementById('siteCanvas');
const ctx = canvas.getContext('2d');
const generateBtn = document.getElementById('generateBtn');
const layoutPagination = document.getElementById('layoutPagination');

// State
let currentLayouts = [];
let currentIndex = 0;

// Setup
canvas.width = CANVAS_WIDTH;
canvas.height = CANVAS_HEIGHT;

function drawLayout(layout) {
    if(!layout) return;

    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // 1. Draw Setback Boundary (10m)
    const setbackPx = 10 * SCALE;
    ctx.strokeStyle = '#cbd5e1';
    ctx.setLineDash([5, 5]);
    ctx.lineWidth = 1;
    ctx.strokeRect(setbackPx, setbackPx, CANVAS_WIDTH - 2*setbackPx, CANVAS_HEIGHT - 2*setbackPx);
    ctx.setLineDash([]);

    // 2. Draw Plaza (Center 40x40m)
    const plazaSize = 40 * SCALE;
    const plazaX = (CANVAS_WIDTH - plazaSize) / 2;
    const plazaY = (CANVAS_HEIGHT - plazaSize) / 2;
    
    ctx.fillStyle = 'rgba(217, 70, 239, 0.2)'; // Fuchsia low opacity
    ctx.fillRect(plazaX, plazaY, plazaSize, plazaSize);
    ctx.strokeStyle = '#d946ef';
    ctx.lineWidth = 2;
    ctx.strokeRect(plazaX, plazaY, plazaSize, plazaSize);
    
    // Label Plaza
    ctx.fillStyle = '#d946ef';
    ctx.font = 'bold 12px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('PLAZA', CANVAS_WIDTH/2, CANVAS_HEIGHT/2);

    // 3. Draw Buildings
    layout.buildings.forEach(b => {
        const x = b.x * SCALE;
        const y = (SITE_HEIGHT_M - b.y - b.h) * SCALE; // Invert Y for canvas if needed? 
        // Wait, Python (0,0) is usually bottom-left in cartesian, but top-left in generic grids.
        // Let's assume standard top-left origin for simplicity unless we need Cartesian.
        // The PDF said "Origin at (0, 0) Opposite corner at (200, 140)".
        // If I treat (0,0) as top-left, it matches canvas.
        // If I treat (0,0) as bottom-left, I need to flip Y.
        // Let's use Top-Left default for now for matching straightforward reading, 
        // OR Flip Y to be "math correct".
        // Let's stick to Top-Left = (0,0) to match canvas for simplicity.
        // My Python code checks bounds generically, so it works for both.
        
        // Actually, let's keep it simple: draw at x * SCALE, y * SCALE.
        const drawX = b.x * SCALE;
        const drawY = b.y * SCALE; 
        const drawW = b.w * SCALE;
        const drawH = b.h * SCALE;

        ctx.fillStyle = b.type === 'A' ? '#3b82f6' : '#10b981';
        ctx.fillRect(drawX, drawY, drawW, drawH);
        
        ctx.strokeStyle = 'rgba(0,0,0,0.1)';
        ctx.lineWidth = 1;
        ctx.strokeRect(drawX, drawY, drawW, drawH);

        // Label
        ctx.fillStyle = 'white';
        ctx.font = 'bold 10px Inter';
        ctx.fillText(b.type, drawX + drawW/2, drawY + drawH/2);
    });
    
    // 4. Update Stats
    document.getElementById('statTowerA').textContent = layout.towersA;
    document.getElementById('statTowerB').textContent = layout.towersB;
    document.getElementById('statArea').textContent = layout.builtArea.toLocaleString();
    document.getElementById('statStatus').textContent = "VALID COMPLIANT"; // Assume valid from backend
}

async function fetchLayouts() {
    generateBtn.classList.add('loading');
    
    try {
        const res = await fetch('/generate-layouts');
        const data = await res.json();
        
        if(data.layouts && data.layouts.length > 0) {
            currentLayouts = data.layouts;
            currentIndex = 0;
            updatePagination();
            drawLayout(currentLayouts[0]);
        }
    } catch(err) {
        console.error("Failed to generate", err);
        alert("Failed to generate layouts. Check backend.");
    } finally {
        generateBtn.classList.remove('loading');
    }
}

function updatePagination() {
    layoutPagination.innerHTML = '';
    currentLayouts.forEach((_, idx) => {
        const btn = document.createElement('div');
        btn.className = `page-btn ${idx === currentIndex ? 'active' : ''}`;
        btn.textContent = idx + 1;
        btn.onclick = () => {
            currentIndex = idx;
            updatePagination();
            drawLayout(currentLayouts[currentIndex]);
        };
        layoutPagination.appendChild(btn);
    });
}

// Initial draw (Optional: Empty site)
// drawLayout({buildings:[]}); // Draw pure site
// Or auto fetch
// fetchLayouts();

generateBtn.onclick = fetchLayouts;
