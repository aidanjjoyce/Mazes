const { useState, useRef, useEffect, useCallback } = React;

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
        if (mazeCanvasRef.current)  drawGroundTruth(mazeCanvasRef.current,  maze, steps, currentStep);
        if (knownCanvasRef.current) drawKnownMap(knownCanvasRef.current, maze, steps, currentStep);
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
