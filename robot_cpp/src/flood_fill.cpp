#include "flood_fill.hpp"
#include <queue>

namespace robot {

// Sentinel value meaning "no path to goal found yet".
// uint8_t max is 255; valid distances are always < CELLS (225 for a 15×15 maze).
static constexpr uint8_t UNREACHABLE = 255;

// ---------------------------------------------------------------------------
// Construction
// ---------------------------------------------------------------------------

FloodFill::FloodFill(RobotState& state, Hal& hal)
    : _state(state), _hal(hal)
{
    // Validate immediately — any missing HAL function is a programming error
    // that should blow up at construction time, not buried in run().
    _hal.validate();

    // Initial flood with no walls known — every cell gets an optimistic
    // distance assuming all passages are open.  The robot will correct this
    // as it senses walls during run().
    _dist.fill(UNREACHABLE);
    _flood();
}

// ---------------------------------------------------------------------------
// Private helpers  (identical in structure to WallFollower's helpers)
// ---------------------------------------------------------------------------

bool FloodFill::_sense_and_record(int relative_offset) {
    bool wall = false;
    if      (relative_offset == -1) wall = _hal.sense_left();
    else if (relative_offset ==  0) wall = _hal.sense_front();
    else                            wall = _hal.sense_right();

    const Direction absolute = _state.relative_to_absolute(relative_offset);
    _state.mark_wall(_state.x, _state.y, absolute, wall);
    return wall;
}

void FloodFill::_move_forward_and_record() {
    const Direction dir = _state.relative_to_absolute(0);

    _state.mark_wall(_state.x, _state.y, dir, false);

    _state.x += DX[static_cast<int>(_state.heading)];
    _state.y += DY[static_cast<int>(_state.heading)];

    _hal.move_forward();

    const Direction opposite = static_cast<Direction>(
        (static_cast<int>(dir) + 2) % 4
    );
    _state.mark_wall(_state.x, _state.y, opposite, false);
}

void FloodFill::_turn_left() {
    _state.heading = static_cast<Direction>(
        (static_cast<int>(_state.heading) + 3) % 4
    );
    if (_hal.on_turn_left) _hal.on_turn_left();
}

void FloodFill::_turn_right() {
    _state.heading = static_cast<Direction>(
        (static_cast<int>(_state.heading) + 1) % 4
    );
    if (_hal.on_turn_right) _hal.on_turn_right();
}

// ---------------------------------------------------------------------------
// _flood — BFS distance propagation from the goal
//
// Assigns every cell its shortest-path distance to the goal, honouring only
// walls that have been recorded in _state.walls.  Walls not yet sensed are
// treated as absent (open passage) — the optimistic assumption ensures the
// robot always has a route to attempt; when a wall is later discovered the
// re-flood will route around it.
// ---------------------------------------------------------------------------

void FloodFill::_flood() {
    _dist.fill(UNREACHABLE);

    const int goal_x   = WIDTH  - 1;
    const int goal_y   = HEIGHT - 1;
    const int goal_idx = goal_y * WIDTH + goal_x;

    _dist[goal_idx] = 0;

    std::queue<int> q;
    q.push(goal_idx);

    while (!q.empty()) {
        const int idx = q.front();
        q.pop();

        const int cx = idx % WIDTH;
        const int cy = idx / WIDTH;

        for (int d = 0; d < 4; ++d) {
            // Skip directions where we know there is a wall.
            if (_state.has_wall(cx, cy, static_cast<Direction>(d))) continue;

            const int nx = cx + DX[d];
            const int ny = cy + DY[d];

            // Bounds check — outer boundary is implicit from the maze walls,
            // but guard here in case a wall was not yet marked at the edge.
            if (nx < 0 || nx >= WIDTH || ny < 0 || ny >= HEIGHT) continue;

            // Also check the wall from the neighbour's side.
            // Sensing only marks the wall on the current cell — the neighbour's
            // reciprocal wall stays unknown (treated as open) until the robot
            // visits that cell.  Without this check, the BFS can cross a known
            // wall from the unvisited side, giving cells a falsely low distance
            // and causing the robot to oscillate toward unreachable passages.
            const Direction opp = static_cast<Direction>((d + 2) % 4);
            if (_state.has_wall(nx, ny, opp)) continue;

            const int nidx = ny * WIDTH + nx;
            if (_dist[nidx] > _dist[idx] + 1) {
                _dist[nidx] = static_cast<uint8_t>(_dist[idx] + 1);
                q.push(nidx);
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Main loop
// ---------------------------------------------------------------------------

void FloodFill::run() {
    int steps = 0;
    while (_state.x != WIDTH - 1 || _state.y != HEIGHT - 1) {
        if (++steps > CELLS * 10) break;  // DEBUG: safety cap against infinite loops
        // Sense the three directly accessible directions and update wall map.
        _sense_and_record(-1);
        _sense_and_record( 0);
        _sense_and_record(+1);

        // Recompute distances now that we have fresh wall information.
        _flood();

        // Choose the open neighbour with the lowest distance to goal.
        int best_dist = static_cast<int>(UNREACHABLE) + 1;  // above any valid value
        int best_dir  = -1;

        for (int d = 0; d < 4; ++d) {
            if (_state.has_wall(_state.x, _state.y, static_cast<Direction>(d))) continue;

            const int nx = _state.x + DX[d];
            const int ny = _state.y + DY[d];
            if (nx < 0 || nx >= WIDTH || ny < 0 || ny >= HEIGHT) continue;

            const int nd = static_cast<int>(_dist[ny * WIDTH + nx]);
            if (nd < best_dist) {
                best_dist = nd;
                best_dir  = d;
            }
        }

        // In a valid, connected maze this should never happen.
        if (best_dir < 0) break;

        // Rotate to face the target direction.
        // delta: 0 = straight, 1 = right, 2 = U-turn, 3 = left
        const int delta = (best_dir - static_cast<int>(_state.heading) + 4) % 4;
        if      (delta == 1) _turn_right();
        else if (delta == 2) { _turn_left(); _turn_left(); }  // U-turn
        else if (delta == 3) _turn_left();

        _move_forward_and_record();
    }
}

} // namespace robot
