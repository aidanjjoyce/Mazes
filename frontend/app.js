const { useState, useRef, useEffect, useCallback } = React;

const CELL = 22;   // px per cell
const WALL = 2;    // wall stroke width

// Wall bit flags matching robot/state.py
const WALL_N = 0b0001;
const WALL_E = 0b0010;
const WALL_S = 0b0100;
const WALL_W = 0b1000;

// heading constants: 0=N, 1=E, 2=S, 3=W
const HEADING_ANGLES = [-Math.PI / 2, 0, Math.PI / 2, Math.PI];

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

function drawGroundTruth(canvas, maze, step) {
    drawMaze(canvas, maze);
    drawRobot(canvas.getContext("2d"), step.x, step.y, step.heading);
}

function drawKnownMap(canvas, maze, step) {
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

    drawRobot(ctx, step.x, step.y, step.heading);
}

function Slider({ label, value, min, max, onChange }) {
    return (
    <div className="field">
        <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <label>{label}</label>
        <span className="range-value">{value}</span>
        </div>
        <input type="range" min={min} max={max} value={value}
        onChange={e => onChange(Number(e.target.value))} />
    </div>
    );
}

function App() {
    const [width,       setWidth]       = useState(15);
    const [height,      setHeight]      = useState(15);
    const [maze,        setMaze]        = useState(null);
    const [steps,       setSteps]       = useState(null);
    const [currentStep, setCurrentStep] = useState(0);
    const [playing,     setPlaying]     = useState(false);
    const [speed,       setSpeed]       = useState(10);
    const [loading,     setLoading]     = useState(false);
    const [error,       setError]       = useState(null);

    const mazeCanvasRef  = useRef(null);
    const knownCanvasRef = useRef(null);

    const isSimulating = steps !== null;

    // ── Draw single maze (generate mode) ───────────────────────────────────
    useEffect(() => {
        if (maze && !isSimulating && mazeCanvasRef.current) {
            drawMaze(mazeCanvasRef.current, maze);
        }
    }, [maze, isSimulating]);

    // ── Redraw both canvases on step change (simulate mode) ─────────────────
    useEffect(() => {
        if (!steps || !maze) return;
        const step = steps[currentStep];
        if (mazeCanvasRef.current)  drawGroundTruth(mazeCanvasRef.current,  maze, step);
        if (knownCanvasRef.current) drawKnownMap(knownCanvasRef.current, maze, step);
    }, [currentStep, steps, maze]);

    // ── Playback timer ───────────────────────────────────────────────────────
    useEffect(() => {
        if (!playing || !steps) return;
        const id = setTimeout(() => {
            setCurrentStep(s => {
                if (s < steps.length - 1) return s + 1;
                setPlaying(false);
                return s;
            });
        }, 1000 / speed);
        return () => clearTimeout(id);
    }, [playing, currentStep, speed, steps]);

    // ── Auto-play when simulation first loads ────────────────────────────────
    useEffect(() => {
        if (steps && steps.length > 0) setPlaying(true);
    }, [steps]);

    // ── API calls ────────────────────────────────────────────────────────────
    const generate = useCallback(async () => {
        setLoading(true); setError(null); setSteps(null); setCurrentStep(0); setPlaying(false);
        try {
            const res = await fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ width, height }),
            });
            if (!res.ok) throw new Error(`Server error ${res.status}`);
            setMaze(await res.json());
        } catch (err) { setError(err.message); }
        finally { setLoading(false); }
    }, [width, height]);

    const simulate = useCallback(async () => {
        setLoading(true); setError(null); setSteps(null); setCurrentStep(0); setPlaying(false);
        try {
            const res = await fetch("/simulate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ width, height }),
            });
            if (!res.ok) throw new Error(`Server error ${res.status}`);
            const data = await res.json();
            setMaze(data.maze);
            setSteps(data.steps);
        } catch (err) { setError(err.message); }
        finally { setLoading(false); }
    }, [width, height]);

    const cellCount = width * height;
    const stepLabel = steps ? `${currentStep + 1} / ${steps.length}` : null;

    return (
    <>
        <header>
        <h1>MAZES</h1>
        <span>// maze lab v0.1</span>
        </header>
        <main>
        <aside className="sidebar">
            <div className="sidebar-section">
            <h2>Parameters</h2>
            <Slider label="width"  value={width}  min={5} max={40} onChange={w => { setWidth(w);  setSteps(null); }} />
            <Slider label="height" value={height} min={5} max={40} onChange={h => { setHeight(h); setSteps(null); }} />
            <button className="btn-generate" onClick={generate} disabled={loading}>
                {loading && !isSimulating ? "generating..." : "generate maze"}
            </button>
            <button className="btn-simulate" onClick={simulate} disabled={loading}>
                {loading && isSimulating ? "simulating..." : "run simulation"}
            </button>
            </div>

            {maze && (
            <div className="sidebar-section">
                <h2>Stats</h2>
                <div className="stat-grid">
                <div className="stat">
                    <div className="val">{maze.width}×{maze.height}</div>
                    <div className="lbl">size</div>
                </div>
                <div className="stat">
                    <div className="val">{cellCount}</div>
                    <div className="lbl">cells</div>
                </div>
                {steps && (
                    <div className="stat" style={{gridColumn:"1/-1"}}>
                    <div className="val">{steps.length}</div>
                    <div className="lbl">sim steps</div>
                    </div>
                )}
                </div>
            </div>
            )}

            {isSimulating && (
            <div className="sidebar-section">
                <h2>Playback</h2>
                <Slider label="speed (steps/s)" value={speed} min={1} max={60} onChange={setSpeed} />
            </div>
            )}

            <div className="sidebar-section">
            <h2>Legend</h2>
            <div className="legend">
                <div className="legend-item">
                <div className="legend-swatch" style={{background:"#7fff6e"}} />
                start
                </div>
                <div className="legend-item">
                <div className="legend-swatch" style={{background:"#ff6e6e"}} />
                end
                </div>
                {isSimulating && (
                <div className="legend-item">
                    <div className="legend-swatch" style={{background:"#ffd700", borderRadius:"50%"}} />
                    robot
                </div>
                )}
            </div>
            </div>
        </aside>

        <div className="canvas-area">
            {!maze && !loading && (
            <div className="empty-state">
                <div className="icon">⌗</div>
                <p>generate a maze to begin</p>
            </div>
            )}

            {maze && !isSimulating && <canvas ref={mazeCanvasRef} />}

            {isSimulating && (
            <div className="sim-layout">
                <div className="canvas-panels">
                <div className="canvas-panel">
                    <div className="canvas-panel-label">ground truth</div>
                    <div className="canvas-wrapper">
                    <canvas ref={mazeCanvasRef} />
                    </div>
                </div>
                <div className="canvas-panel">
                    <div className="canvas-panel-label">robot's map</div>
                    <div className="canvas-wrapper">
                    <canvas ref={knownCanvasRef} />
                    </div>
                </div>
                </div>

                <div className="playback-bar">
                <button className="btn-play" onClick={() => setPlaying(p => !p)}>
                    {playing ? "⏸" : "▶"}
                </button>
                <input
                    className="playback-scrub"
                    type="range"
                    min={0}
                    max={steps.length - 1}
                    value={currentStep}
                    onChange={e => { setPlaying(false); setCurrentStep(Number(e.target.value)); }}
                />
                <span className="step-counter">{stepLabel}</span>
                </div>
            </div>
            )}

            {loading && (
            <div className="loading-overlay">
                <div className="spinner" />
            </div>
            )}
            {error && <div className="error-bar">error: {error}</div>}
        </div>
        </main>
    </>
    );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
