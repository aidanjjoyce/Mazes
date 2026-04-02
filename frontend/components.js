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

function Select({ label, value, options, onChange }) {
    return (
    <div className="field">
        <label>{label}</label>
        <select value={value} onChange={e => onChange(e.target.value)}>
        {options.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
        ))}
        </select>
    </div>
    );
}
