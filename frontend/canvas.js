function drawMaze(canvas, maze) {
    const ctx = canvas.getContext("2d");
    const W = maze.width  * CELL;
    const H = maze.height * CELL;
    canvas.width  = W;
    canvas.height = H;

    ctx.fillStyle = "#141714";
    ctx.fillRect(0, 0, W, H);

    for (let y = 0; y < maze.height; y++) {
    for (let x = 0; x < maze.width; x++) {
        const px = x * CELL;
        const py = y * CELL;
        const cell = maze.cells[y][x];

        const isStart = maze.start.x === x && maze.start.y === y;
        const isEnd   = maze.end.x   === x && maze.end.y   === y;

        if (isStart) {
            ctx.fillStyle = "rgba(127,255,110,0.15)";
            ctx.fillRect(px + 1, py + 1, CELL - 2, CELL - 2);
        } else if (isEnd) {
            ctx.fillStyle = "rgba(255,110,110,0.15)";
            ctx.fillRect(px + 1, py + 1, CELL - 2, CELL - 2);
        }

        ctx.strokeStyle = "#d4e0d3";
        ctx.lineWidth   = WALL;

        if (cell.walls.N) { ctx.beginPath(); ctx.moveTo(px, py);        ctx.lineTo(px + CELL, py);        ctx.stroke(); }
        if (cell.walls.S) { ctx.beginPath(); ctx.moveTo(px, py + CELL); ctx.lineTo(px + CELL, py + CELL); ctx.stroke(); }
        if (cell.walls.W) { ctx.beginPath(); ctx.moveTo(px, py);        ctx.lineTo(px, py + CELL);        ctx.stroke(); }
        if (cell.walls.E) { ctx.beginPath(); ctx.moveTo(px + CELL, py); ctx.lineTo(px + CELL, py + CELL); ctx.stroke(); }
    }
    }

    const drawDot = (x, y, color) => {
        const cx = x * CELL + CELL / 2;
        const cy = y * CELL + CELL / 2;
        ctx.beginPath();
        ctx.arc(cx, cy, CELL * 0.22, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
    };
    drawDot(maze.start.x, maze.start.y, "#7fff6e");
    drawDot(maze.end.x,   maze.end.y,   "#ff6e6e");
}

function drawRobot(ctx, rx, ry, heading) {
    const cx = rx * CELL + CELL / 2;
    const cy = ry * CELL + CELL / 2;
    const r  = CELL * 0.30;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(HEADING_ANGLES[heading]);
    ctx.beginPath();
    ctx.moveTo( r,       0);
    ctx.lineTo(-r * 0.6, -r * 0.55);
    ctx.lineTo(-r * 0.6,  r * 0.55);
    ctx.closePath();
    ctx.fillStyle = "#ffd700";
    ctx.fill();
    ctx.restore();
}

function drawTrail(ctx, steps, currentStep) {
    ctx.fillStyle = "rgba(127, 255, 110, 0.5)";
    const seen = new Set();
    for (let i = 0; i <= currentStep; i++) {
        const { x, y } = steps[i];
        const key = `${x},${y}`;
        if (!seen.has(key)) {
            seen.add(key);
            ctx.fillRect(x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2);
        }
        if (i > 0) {
            const px = steps[i - 1].x, py = steps[i - 1].y;
            if (x !== px || y !== py) {
                const pkey = `${Math.min(x,px)},${Math.min(y,py)},${x !== px ? 'h' : 'v'}`;
                if (!seen.has(pkey)) {
                    seen.add(pkey);
                    if (x !== px) {
                        const lx = Math.min(x, px);
                        ctx.fillRect(lx * CELL + CELL - 1, y * CELL + 1, 2, CELL - 2);
                    } else {
                        const ty = Math.min(y, py);
                        ctx.fillRect(x * CELL + 1, ty * CELL + CELL - 1, CELL - 2, 2);
                    }
                }
            }
        }
    }
}

function drawGroundTruth(canvas, maze, steps, currentStep) {
    const step = steps[currentStep];
    drawMaze(canvas, maze);
    const ctx = canvas.getContext("2d");
    drawTrail(ctx, steps, currentStep);
    drawRobot(ctx, step.x, step.y, step.heading);
}

function drawKnownMap(canvas, maze, steps, currentStep) {
    const step = steps[currentStep];
    const ctx = canvas.getContext("2d");
    const W = maze.width  * CELL;
    const H = maze.height * CELL;
    canvas.width  = W;
    canvas.height = H;

    ctx.fillStyle = "#141714";
    ctx.fillRect(0, 0, W, H);

    // Faint grid so unexplored areas still look structured
    ctx.strokeStyle = "#1c201c";
    ctx.lineWidth = 1;
    for (let r = 0; r <= maze.height; r++) {
        ctx.beginPath(); ctx.moveTo(0, r * CELL); ctx.lineTo(W, r * CELL); ctx.stroke();
    }
    for (let c = 0; c <= maze.width; c++) {
        ctx.beginPath(); ctx.moveTo(c * CELL, 0); ctx.lineTo(c * CELL, H); ctx.stroke();
    }

    // Known-present walls
    ctx.strokeStyle = "#d4e0d3";
    ctx.lineWidth = WALL;

    for (let y = 0; y < maze.height; y++) {
    for (let x = 0; x < maze.width; x++) {
        const idx   = y * maze.width + x;
        const known = step.walls_known[idx];
        const walls = step.walls[idx];
        const px = x * CELL, py = y * CELL;

        if ((known & WALL_N) && (walls & WALL_N)) { ctx.beginPath(); ctx.moveTo(px, py);        ctx.lineTo(px + CELL, py);        ctx.stroke(); }
        if ((known & WALL_S) && (walls & WALL_S)) { ctx.beginPath(); ctx.moveTo(px, py + CELL); ctx.lineTo(px + CELL, py + CELL); ctx.stroke(); }
        if ((known & WALL_W) && (walls & WALL_W)) { ctx.beginPath(); ctx.moveTo(px, py);        ctx.lineTo(px, py + CELL);        ctx.stroke(); }
        if ((known & WALL_E) && (walls & WALL_E)) { ctx.beginPath(); ctx.moveTo(px + CELL, py); ctx.lineTo(px + CELL, py + CELL); ctx.stroke(); }
    }
    }

    // End marker (robot always knows the goal location)
    ctx.beginPath();
    ctx.arc(maze.end.x * CELL + CELL / 2, maze.end.y * CELL + CELL / 2, CELL * 0.22, 0, Math.PI * 2);
    ctx.fillStyle = "#ff6e6e";
    ctx.fill();

    drawTrail(ctx, steps, currentStep);
    drawRobot(ctx, step.x, step.y, step.heading);
}
