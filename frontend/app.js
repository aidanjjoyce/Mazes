const { useState, useRef, useEffect, useCallback } = React;

const CELL = 22;   // px per cell
const WALL = 2;    // wall stroke width

function drawMaze(canvas, maze) {
    const ctx = canvas.getContext("2d");
    const W = maze.width  * CELL;
    const H = maze.height * CELL;
    canvas.width  = W;
    canvas.height = H;

    // background
    ctx.fillStyle = "#141714";
    ctx.fillRect(0, 0, W, H);

    for (let y = 0; y < maze.height; y++) {
    for (let x = 0; x < maze.width; x++) {
        const px = x * CELL;
        const py = y * CELL;
        const cell = maze.cells[y][x];

        // start / end markers
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

        if (cell.walls.N) {
        ctx.beginPath();
        ctx.moveTo(px, py); ctx.lineTo(px + CELL, py);
        ctx.stroke();
        }
        if (cell.walls.S) {
        ctx.beginPath();
        ctx.moveTo(px, py + CELL); ctx.lineTo(px + CELL, py + CELL);
        ctx.stroke();
        }
        if (cell.walls.W) {
        ctx.beginPath();
        ctx.moveTo(px, py); ctx.lineTo(px, py + CELL);
        ctx.stroke();
        }
        if (cell.walls.E) {
        ctx.beginPath();
        ctx.moveTo(px + CELL, py); ctx.lineTo(px + CELL, py + CELL);
        ctx.stroke();
        }
    }
    }

    // dot markers for start / end
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
    const [width,   setWidth]   = useState(15);
    const [height,  setHeight]  = useState(15);
    const [maze,    setMaze]    = useState(null);
    const [loading, setLoading] = useState(false);
    const [error,   setError]   = useState(null);
    const canvasRef = useRef(null);

    useEffect(() => {
    if (maze && canvasRef.current) {
        drawMaze(canvasRef.current, maze);
    }
    }, [maze]);

    const generate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
        const res = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ width, height }),
        });
        if (!res.ok) throw new Error(`Server error ${res.status}`);
        const data = await res.json();
        setMaze(data);
    } catch (err) {
        setError(err.message);
    } finally {
        setLoading(false);
    }
    }, [width, height]);

    const cellCount = width * height;

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
            <Slider label="width"  value={width}  min={5} max={40} onChange={setWidth}  />
            <Slider label="height" value={height} min={5} max={40} onChange={setHeight} />
            <button className="btn-generate" onClick={generate} disabled={loading}>
                {loading ? "generating..." : "generate maze"}
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
                </div>
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
            {maze && <canvas ref={canvasRef} />}
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