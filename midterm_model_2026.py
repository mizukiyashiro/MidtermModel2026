"""
2026 Midterm Forecast Model  (as of Oct 18, 2026)
=================================================
Polls + Fundamentals + Expert-Ratings blend, simulated with correlated errors.

For each race i (margin = Dem/Ind-challenger share minus Rep share, in points):

  1) Poll average      P_i = sum_j w_ij * (m_ij - h_ij) / sum_j w_ij
       w_ij = exp(-age_ij / 14) * sqrt(n_ij / 600) * LV_ij * S_ij
       LV = 1.0 likely voters, 0.8 registered/adults
       S  = 0.6 if partisan-sponsored, h = +/-1.5 pt house-effect correction

  2) Fundamentals      F_i = GB - 2*PVI_i + INC_i + Q_i
       GB  = expected national House popular-vote margin (D+7.5)
       PVI = Cook PVI (R positive); x2 converts share-lean to margin-lean
       INC = +/-3 elected Senate incumbent, +/-1.5 appointed; +/-4 governor
       Q   = documented candidate effects (e.g. Osborn's 2024 overperformance)

  3) Expert prior      E_i = mean forecaster rating mapped to margin
       Safe 18 | Likely 9 | Lean 4.5 | Tilt 2 | Toss-up 0

  Blend:   mu_i = 0.65*P_i + 0.15*F_i + 0.20*E_i   (races with polling)
           mu_i = 0.25*F_i + 0.75*E_i              (races without polling)

  Simulation (50,000 draws):
       outcome_i = mu_i + eps_nat + eps_i
       eps_nat ~ N(0, 2.5)   shared national polling/environment error
       eps_i   ~ N(0, 4.5)   state-specific error (6.0 if thinly polled)
  Seat totals = seats not up + simulated winners.

House:  D_seats = 435 / (1 + exp(-k * (V - b)))
       V ~ N(7.0, 3.0)  national popular vote margin (generic ballot D+8.2 to D+8.9,
                        shrunk ~15% toward fundamentals per historical GB error)
       b = +1.0 (map bias: Dems need ~D+1 to reach 218 after 2025-26 redistricting)
       k = 0.025 (seats-votes slope ~2.7 seats/pt, calibrated to 2018: D+8.6 -> 235 D)
"""
import numpy as np
from math import exp, sqrt

rng = np.random.default_rng(2026)
N = 50_000
GB = 7.5
TODAY_OFFSET = 0  # ages below are days before Oct 18, 2026

# ---------------------------------------------------------------------------
# Senate races: state -> (PVI [R+ positive], INC, Q, expert E, D-side name, R name, D-side party)
# INC sign: + helps D-side, - helps R side
# ---------------------------------------------------------------------------
SEN = {
 "AL": (15, 0, 0, -18, "Everett Wess", "Barry Moore", "D"),
 "AK": (6, -3, 0, 1, "Mary Peltola", "Dan Sullivan", "D"),
 "AR": (15, -3, 0, -18, "Hallie Shoffner", "Tom Cotton", "D"),
 "CO": (-6, 3, 0, 18, "John Hickenlooper", "Mark Baisley", "D"),
 "DE": (-8, 3, 0, 18, "Chris Coons", "Michael Katz", "D"),
 "FL": (5, -1.5, 0, -9, "Angie Nixon", "Ashley Moody", "D"),
 "GA": (1, 3, 0, 8, "Jon Ossoff", "Mike Collins", "D"),
 "ID": (18, -3, 0, -18, "Todd Achilles", "Jim Risch", "I"),
 "IL": (-6, 0, 0, 18, "Juliana Stratton", "Don Tracy", "D"),
 "IA": (6, 0, 0, 0, "Josh Turek", "Ashley Hinson", "D"),
 "KS": (8, -3, 0, -3, "Adam Hamilton", "Roger Marshall", "D"),
 "KY": (15, 0, 0, -18, "Charles Booker", "Andy Barr", "D"),
 "LA": (11, 0, 0, -16, "Jamie Davis", "Julia Letlow", "D"),
 "ME": (-4, -3, 0, 1.5, "Troy Jackson", "Susan Collins", "D"),
 "MA": (-14, 3, 0, 18, "Ed Markey", "John Deaton", "D"),
 "MI": (0, 0, 0, 4, "Abdul El-Sayed", "Mike Rogers", "D"),
 "MN": (-3, 0, 0, 8, "Peggy Flanagan", "Michele Tafoya", "D"),
 "MS": (11, -3, 0, -16, "Scott Colom", "Cindy Hyde-Smith", "D"),
 "MT": (10, 0, 4, -15, "Seth Bodnar", "Kurt Alme", "I"),
 "NE": (10, -3, 10, -8, "Dan Osborn", "Pete Ricketts", "I"),
 "NH": (-2, 0, 0, 7, "Chris Pappas", "John E. Sununu", "D"),
 "NJ": (-4, 3, 0, 18, "Cory Booker", "Justin Murphy", "D"),
 "NM": (-4, 3, 0, 17, "Ben Ray Lujan", "Larry Marker", "D"),
 "NC": (1, 0, 0, 7, "Roy Cooper", "Michael Whatley", "D"),
 "OH": (5, -1.5, 0, 1.5, "Sherrod Brown", "Jon Husted", "D"),
 "OK": (17, 0, 0, -18, "Jasmine Thomas", "Kevin Hern", "D"),
 "OR": (-8, 3, 0, 18, "Jeff Merkley", "David Brock Smith", "D"),
 "RI": (-8, 3, 0, 18, "Jack Reed", "Raymond McKay", "D"),
 "SC": (8, -1.5, 0, -9, "Annie Andrews", "Darline Graham", "D"),
 "SD": (15, -3, 0, -17, "Brian Bengs", "Mike Rounds", "I"),
 "TN": (14, -3, 0, -18, "Marquita Bradshaw", "Bill Hagerty", "D"),
 "TX": (6, 0, 0, 1, "James Talarico", "Ken Paxton", "D"),
 "VA": (-3, 3, 0, 18, "Mark Warner", "Bert Mizusawa", "D"),
 "WV": (21, -3, 0, -18, "Rachel Fetty Anderson", "Shelley Moore Capito", "D"),
 "WY": (23, 0, 0, -18, "James Byrd", "Harriet Hageman", "D"),
}
SEN_NOT_UP = {"D": 32, "I": 2, "R": 31}

# Senate polls: (state, D-side margin, n, age_days, LV?, partisan_sponsor: 0 none, 'D' or 'R')
SEN_POLLS = [
 # Alaska (first-round margins)
 ("AK", 7, 504, 20, 1, 0), ("AK", 2, 1512, 16, 1, 0), ("AK", 5.6, 1200, 9, 1, 0),
 ("AK", 0, 600, 17, 1, 0), ("AK", -1, 1079, 25, 1, 0), ("AK", 5, 800, 30, 1, 0),
 # Florida
 ("FL", -10, 625, 20, 0, 0), ("FL", -2, 800, 11, 1, 0),
 # Georgia
 ("GA", 10, 1000, 26, 1, 0), ("GA", 7, 800, 45, 1, 0),
 # Iowa
 ("IA", 4, 500, 15, 1, 0), ("IA", -2, 800, 14, 1, 0), ("IA", -2, 700, 13, 1, 0),
 ("IA", 1, 2245, 7, 1, 0), ("IA", 3, 600, 8, 1, 0), ("IA", -1, 606, 18, 1, 0),
 ("IA", -2, 700, 20, 1, 0),
 # Kansas
 ("KS", 4, 800, 18, 1, "D"), ("KS", 0, 700, 17, 1, 0), ("KS", 3, 2255, 15, 1, 0),
 ("KS", 0.8, 1200, 8, 1, 0), ("KS", 0.9, 1095, 18, 1, 0), ("KS", 2, 800, 14, 1, 0),
 # Maine (Jackson replaced Platner)
 ("ME", 2, 500, 8, 1, 0), ("ME", 4, 900, 11, 1, 0), ("ME", 4, 1505, 15, 0, 0),
 ("ME", 3, 800, 19, 1, 0),
 # Michigan
 ("MI", 1, 1500, 13, 1, 0), ("MI", 1, 700, 12, 1, 0), ("MI", 5, 650, 14, 1, 0),
 # Minnesota
 ("MN", 4, 800, 11, 1, 0), ("MN", 3, 600, 5, 1, 0), ("MN", 4, 1000, 10, 0, 0),
 ("MN", 2, 622, 19, 1, 0),
 # Nebraska (Osborn = independent, D-side)
 ("NE", 1, 1100, 13, 1, 0), ("NE", -3, 600, 7, 1, "R"), ("NE", 0, 600, 65, 1, "D"),
 # New Hampshire
 ("NH", 8, 900, 13, 1, 0), ("NH", 7, 1042, 19, 1, 0), ("NH", 7, 600, 3, 1, 0),
 ("NH", 8, 1418, 27, 1, 0), ("NH", 5, 613, 26, 1, 0),
 # North Carolina
 ("NC", 14, 643, 8, 1, 0), ("NC", 7, 600, 11, 1, 0), ("NC", 11, 800, 40, 1, 0),
 # Ohio
 ("OH", 6, 900, 12, 1, 0), ("OH", 3, 500, 14, 1, 0), ("OH", 8, 1100, 14, 0, 0),
 ("OH", 3, 800, 16, 1, 0),
 # South Carolina
 ("SC", -1, 1200, 19, 1, 0),
 # Texas
 ("TX", 2, 1000, 21, 1, 0), ("TX", 3, 800, 12, 1, "D"), ("TX", 4, 500, 6, 1, 0),
 ("TX", 6, 1200, 13, 1, 0),
]
# Candidate/state-specific poll-bias adjustments (documented history)
POLL_ADJ = {"ME": -2.0,   # Collins beat final 2020 polls by ~10 pts
            "AK": -1.0}   # Alaska polls have leaned D in recent cycles

# ---------------------------------------------------------------------------
# Governor races: state -> (PVI, INC, Q, E, D name, R name)
# ---------------------------------------------------------------------------
GOV = {
 "AL": (15, 0, 0, -18, "Doug Jones", "Tommy Tuberville"),
 "AK": (6, 0, 0, 0.5, "Jonathan Kreiss-Tomkins", "Dave Bronson"),
 "AZ": (2, 4, 0, 5, "Katie Hobbs", "Andy Biggs"),
 "AR": (15, -4, 0, -18, "Fredrick Love", "Sarah Huckabee Sanders"),
 "CA": (-12, 0, 0, 18, "Xavier Becerra", "Steve Hilton"),
 "CO": (-6, 0, 0, 16, "Phil Weiser", "Victor Marx"),
 "CT": (-8, 4, 0, 17, "Ned Lamont", "Ryan Fazio"),
 "FL": (5, 0, 0, -9, "David Jolly", "Byron Donalds"),
 "GA": (1, 0, 0, 0.5, "Keisha Lance Bottoms", "Rick Jackson"),
 "HI": (-13, 4, 0, 18, "Josh Green", "Gary Cordery"),
 "ID": (18, -4, 0, -18, "Terri Pickens", "Brad Little"),
 "IL": (-6, 4, 0, 17, "JB Pritzker", "Darren Bailey"),
 "IA": (6, 0, 0, 4, "Rob Sand", "Zach Lahn"),
 "KS": (8, 0, 0, -4, "Cindy Holscher", "Ty Masterson"),
 "ME": (-4, 0, 0, 10, "Hannah Pingree", "Robert Charles"),
 "MD": (-15, 4, 0, 18, "Wes Moore", "Dan Cox"),
 "MA": (-14, 4, 0, 18, "Maura Healey", "Mike Minogue"),
 "MI": (0, 0, 0, 5, "Jocelyn Benson", "John James"),
 "MN": (-3, 0, 0, 14, "Amy Klobuchar", "Lisa Demuth"),
 "NE": (10, -4, 0, -17, "Lynne Walz", "Jim Pillen"),
 "NV": (1, -4, 0, -2.5, "Aaron Ford", "Joe Lombardo"),
 "NH": (-2, -4, 0, -8, "Cinde Warmington", "Kelly Ayotte"),
 "NM": (-4, 0, 0, 13, "Deb Haaland", "Gregg Hull"),
 "NY": (-8, 4, 0, 16, "Kathy Hochul", "Bruce Blakeman"),
 "OH": (5, 0, 0, -1, "Amy Acton", "Vivek Ramaswamy"),
 "OK": (17, 0, 0, -18, "Cyndi Munson", "Mike Mazzei"),
 "OR": (-8, 4, 0, 8, "Tina Kotek", "Christine Drazan"),
 "PA": (1, 4, 0, 17, "Josh Shapiro", "Stacy Garrity"),
 "RI": (-8, 0, 0, 16, "Helena Foulkes", "Aaron Guckian"),
 "SC": (8, 0, 0, -17, "Jermaine Johnson", "Alan Wilson"),
 "SD": (15, -2, 0, -17, "Dan Ahlers", "Larry Rhoden"),
 "TN": (14, 0, 0, -18, "Jerri Green", "Marsha Blackburn"),
 "TX": (6, -4, 0, -9, "Gina Hinojosa", "Greg Abbott"),
 "VT": (-17, -4, -40, -18, "Amanda Janoo", "Phil Scott"),
 "WI": (0, 0, 0, 1.5, "David Crowley", "Tom Tiffany"),
 "WY": (23, 0, 0, -18, "Kenneth Casner", "Eric Barlow"),
}
GOV_NOT_UP = {"D": 6, "I": 0, "R": 8}

GOV_POLLS = [
 ("AZ", 8, 913, 80, 1, 0), ("AZ", 13, 923, 66, 1, 0), ("AZ", 15, 400, 61, 1, 0),
 ("AZ", 6, 780, 62, 1, 0), ("AZ", 5, 900, 63, 1, 0), ("AZ", 4, 600, 80, 1, "R"),
 ("FL", -7, 625, 20, 0, 0), ("FL", 0, 800, 11, 1, 0), ("FL", -5, 848, 95, 1, 0),
 ("GA", -2, 800, 6, 1, 0), ("GA", -1, 1000, 28, 0, 0), ("GA", -2, 800, 25, 1, 0),
 ("GA", -3, 1019, 34, 1, 0),
 ("IA", 12, 500, 15, 1, 0), ("IA", 9, 800, 14, 1, 0), ("IA", 4, 700, 13, 1, 0),
 ("IA", 6, 2245, 7, 1, 0), ("IA", 7, 600, 8, 1, 0),
 ("ME", 11, 500, 8, 1, 0), ("ME", 12, 1505, 15, 0, 0), ("ME", 13, 800, 19, 1, 0),
 ("MI", 7, 682, 17, 1, 0),
 ("NV", -2, 708, 24, 1, 0), ("NV", 2, 680, 41, 1, 0),
 ("OH", 8, 900, 12, 1, 0),
 ("TX", -5, 1000, 21, 1, 0), ("TX", -2, 800, 12, 1, "D"), ("TX", -1, 500, 6, 1, 0),
 ("WI", 4, 1000, 3, 0, "D"), ("WI", 4, 500, 55, 1, 0),
]


def poll_average(polls, state, adj=0.0):
    num = den = 0.0
    neff = 0.0
    for st, m, n, age, lv, part in polls:
        if st != state:
            continue
        w = exp(-age / 14) * sqrt(n / 600) * (1.0 if lv else 0.8)
        h = 0.0
        if part == "D":
            w *= 0.6; h = 1.5
        elif part == "R":
            w *= 0.6; h = -1.5
        num += w * (m - h)
        den += w
        neff += w
    if den == 0:
        return None, 0.0
    return num / den + adj, neff


def race_means(races, polls, poll_adj=None):
    poll_adj = poll_adj or {}
    out = {}
    for st, row in races.items():
        pvi, inc, q, e = row[0], row[1], row[2], row[3]
        F = GB - 2 * pvi + inc + q
        P, neff = poll_average(polls, st, poll_adj.get(st, 0.0))
        if P is None:
            mu, sd_state = 0.25 * F + 0.75 * e, 6.0
        else:
            mu = 0.65 * P + 0.15 * F + 0.20 * e
            sd_state = 4.5 if neff >= 1.0 else 6.0
        out[st] = dict(F=F, P=P, E=e, mu=mu, sd=sd_state, neff=neff)
    return out


def simulate(means):
    states = list(means)
    mu = np.array([means[s]["mu"] for s in states])
    sd = np.array([means[s]["sd"] for s in states])
    eps_nat = rng.normal(0, 2.5, size=(N, 1))
    eps_st = rng.normal(0, 1, size=(N, len(states))) * sd
    margins = mu + eps_nat + eps_st
    return states, margins


def summarize(name, races, means, not_up, dside_party_idx=None):
    states, margins = simulate(means)
    dwin = margins > 0
    p = dwin.mean(axis=0)
    # party of D-side winner per state
    party = [races[s][6] if dside_party_idx else "D" for s in states]
    d_cols = [i for i, pt in enumerate(party) if pt == "D"]
    i_cols = [i for i, pt in enumerate(party) if pt == "I"]
    D = not_up["D"] + dwin[:, d_cols].sum(axis=1)
    I = not_up["I"] + dwin[:, i_cols].sum(axis=1)
    R = not_up["R"] + (~dwin).sum(axis=1)
    print(f"\n===== {name} =====")
    print(f"{'St':<4}{'Poll':>7}{'Fund':>7}{'Exp':>6}{'Mean':>7}{'P(D-side)':>11}  Favored")
    for k, s in enumerate(states):
        m = means[s]
        P = f"{m['P']:+.1f}" if m["P"] is not None else "  —"
        fav = races[s][4] if p[k] > 0.5 else races[s][5]
        print(f"{s:<4}{P:>7}{m['F']:>+7.1f}{m['E']:>+6.1f}{m['mu']:>+7.1f}{p[k]:>10.0%}  {fav}")
    print(f"Median seats  D {np.median(D):.0f} | I {np.median(I):.0f} | R {np.median(R):.0f}")
    print(f"Mean seats    D {D.mean():.1f} | I {I.mean():.1f} | R {R.mean():.1f}")
    print(f"80% interval  D {np.percentile(D,10):.0f}-{np.percentile(D,90):.0f} | "
          f"R {np.percentile(R,10):.0f}-{np.percentile(R,90):.0f}")
    # modal combined outcome
    combos, counts = np.unique(np.stack([D, I, R], 1), axis=0, return_counts=True)
    top = combos[np.argsort(-counts)[:3]]
    print("Most likely D/I/R splits:", [tuple(int(x) for x in c) for c in top],
          [f"{c/N:.1%}" for c in np.sort(counts)[::-1][:3]])
    return D, I, R, p, states


if __name__ == "__main__":
    sm = race_means(SEN, SEN_POLLS, POLL_ADJ)
    D, I, R, p_sen, s_sen = summarize("SENATE", SEN, sm, SEN_NOT_UP, dside_party_idx=True)
    print(f"P(Dem caucus >= 51) = {((D + I) >= 51).mean():.0%}   "
          f"P(50-50) = {((D + I) == 50).mean():.0%}")

    gm = race_means(GOV, GOV_POLLS)
    GOV6 = {k: v + ("D",) for k, v in GOV.items()}
    summarize("GOVERNORS", GOV6, gm, GOV_NOT_UP, dside_party_idx=True)

    # House
    V = rng.normal(7.0, 3.0, N)
    b, k = 1.0, 0.025
    Dh = np.rint(435 / (1 + np.exp(-k * (V - b))))
    print("\n===== HOUSE =====")
    print(f"Median D {np.median(Dh):.0f} / R {435-np.median(Dh):.0f}; "
          f"80% interval D {np.percentile(Dh,10):.0f}-{np.percentile(Dh,90):.0f}; "
          f"P(D majority) = {(Dh >= 218).mean():.0%}")
