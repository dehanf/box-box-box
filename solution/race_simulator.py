#!/usr/bin/env python3
"""
Box Box Box - F1 Race Simulator Template (Python)
"""

import json
import sys

"""v = [-2.71, 2.09, 0.002, 0.00071, 0.000298, 4.84, 6.81, 5.87]

PARAMS = {
    'compound_offset': {
        'SOFT':   v[0],
        'MEDIUM':  0.0,
        'HARD':    v[1],
    },
    'deg_rate': {
        'SOFT':   v[2],
        'MEDIUM': v[3],
        'HARD':   v[4],
    },
    'deg_exp': v[5],

    # "Initial performance period" — laps of zero degradation.
    # Regulations say this varies by compound. Set to 0 for now;
    # re-run optimizer including these to find the true values.
    'deg_threshold': {
        'SOFT':   v[5],
        'MEDIUM': v[6],
        'HARD':   v[7],
    }
}"""

PARAMS = {
    'compound_offset': {'SOFT': -3.0, 'MEDIUM': 0.0, 'HARD': 2.34},
    'deg_rate':        {'SOFT': 0.276, 'MEDIUM': 0.11, 'HARD': 0.030},
    'deg_exp':         2.5,
    'deg_threshold':   {'SOFT': 8, 'MEDIUM': 19, 'HARD': 28},
    'temp_scale':      0.025,
    'temp_ref':        29.0,
}


def calc_lap_time(base, tire, tire_age, temp, params):
    offset    = params['compound_offset'][tire]
    threshold = params['deg_threshold'][tire]
    rate      = params['deg_rate'][tire]
    ts        = params['temp_scale']
    tref      = params['temp_ref']

    t_mult        = 1.0 + ts * (temp - tref)
    effective_age = max(0.0, tire_age - threshold)
    degradation   = rate * (effective_age ** params['deg_exp']) * t_mult

    return base + offset + degradation


def simulate_race(race_config, strategies, params):
    base       = race_config['base_lap_time']
    pit_time   = race_config['pit_lane_time']
    total_laps = race_config['total_laps']
    temp       = race_config['track_temp']

    driver_times = {}

    for strat in strategies.values():
        driver   = strat['driver_id']
        pit_map  = {ps['lap']: ps['to_tire'] for ps in strat['pit_stops']}

        current_tire = strat['starting_tire']
        tire_age     = 0
        total_time   = 0.0

        for lap in range(1, total_laps + 1):
            tire_age  += 1
            total_time += calc_lap_time(base, current_tire, tire_age, temp, params)

            if lap in pit_map:
                total_time  += pit_time
                current_tire = pit_map[lap]
                tire_age     = 0

        driver_times[driver] = total_time

    return sorted(driver_times, key=driver_times.__getitem__)


def main():
    test_case = json.load(sys.stdin)


    finishing_positions = simulate_race(
        test_case['race_config'],
        test_case['strategies'],
        PARAMS,
    )
    print(json.dumps({
        'race_id': test_case['race_id'],
        'finishing_positions': finishing_positions,
    }))


if __name__ == '__main__':
    main()