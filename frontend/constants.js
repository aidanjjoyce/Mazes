const CELL = 22;   // px per cell
const WALL = 2;    // wall stroke width

// Wall bit flags matching robot/state.py
const WALL_N = 0b0001;
const WALL_E = 0b0010;
const WALL_S = 0b0100;
const WALL_W = 0b1000;

// heading constants: 0=N, 1=E, 2=S, 3=W
const HEADING_ANGLES = [-Math.PI / 2, 0, Math.PI / 2, Math.PI];
