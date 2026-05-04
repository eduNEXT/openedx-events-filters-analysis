import sqlite3
import argparse
import sys
from datetime import datetime, timezone

BAR_WIDTH = 36

CODE_SCRIPTS = {
    'Backend': 'adoption_search_code',
    'Frontend': 'adoption_search_fe_plugins_code',
}
ORG_PR_SCRIPTS = {
    'Backend': 'adoption_search_per_org_prs',
    'Frontend': 'adoption_search_fe_plugins_per_org_prs',
}


# ── DB helpers ────────────────────────────────────────────────────────────────

def latest_runs(conn, script, n=2):
    return conn.execute(
        "SELECT id, run_at, notes FROM runs WHERE script = ? ORDER BY run_at DESC LIMIT ?",
        (script, n),
    ).fetchall()


def repo_count(conn, run_id):
    return conn.execute(
        "SELECT COUNT(DISTINCT repository) FROM results WHERE run_id = ? AND is_fork = 0",
        (run_id,),
    ).fetchone()[0]


def repo_set(conn, run_id):
    rows = conn.execute(
        "SELECT DISTINCT repository, repository_url FROM results WHERE run_id = ? AND is_fork = 0",
        (run_id,),
    ).fetchall()
    return {r[0]: r[1] for r in rows}


def signal_breakdown(conn, run_id):
    return conn.execute(
        """SELECT signal, phase, COUNT(DISTINCT repository) AS repos
           FROM results WHERE run_id = ? AND is_fork = 0
           GROUP BY signal, phase ORDER BY repos DESC""",
        (run_id,),
    ).fetchall()


def top_orgs(conn, script, limit=15):
    runs = latest_runs(conn, script, n=1)
    if not runs:
        return None, []
    run_id, run_at, _ = runs[0]
    rows = conn.execute(
        """SELECT organization, COUNT(DISTINCT pr_url) AS prs
           FROM pr_results
           WHERE run_id = ? AND is_fork = 0 AND organization IS NOT NULL
           GROUP BY organization ORDER BY prs DESC LIMIT ?""",
        (run_id, limit),
    ).fetchall()
    return run_at, rows


def trend_data(conn, script):
    return conn.execute(
        """SELECT r.run_at, r.notes, COUNT(DISTINCT res.repository) AS repos
           FROM runs r JOIN results res ON res.run_id = r.id
           WHERE r.script = ? AND res.is_fork = 0
           GROUP BY r.id ORDER BY r.run_at""",
        (script,),
    ).fetchall()


# ── Formatting helpers ────────────────────────────────────────────────────────

def delta_str(current, previous):
    if previous is None:
        return '—'
    diff = current - previous
    if diff > 0:
        return f'+{diff}'
    if diff < 0:
        return str(diff)
    return '±0'


def ascii_bar(value, max_value):
    if max_value == 0:
        return ''
    return '█' * round(value / max_value * BAR_WIDTH)


def fmt_date(iso):
    return iso[:10] if iso else ''


# ── Report sections ───────────────────────────────────────────────────────────

def section_snapshot(conn):
    lines = ['## 1. Adoption Snapshot', '']
    lines.append('Unique repositories adopting each plugin archetype (forks excluded).\n')
    lines.append('| Archetype | Repos | vs. Previous Run | Run |')
    lines.append('|---|---|---|---|')

    total_current = 0
    total_previous = 0
    any_previous = False

    for label, script in CODE_SCRIPTS.items():
        runs = latest_runs(conn, script, n=2)
        if not runs:
            lines.append(f'| {label} | _no data_ | — | |')
            continue
        curr_id, curr_at, curr_notes = runs[0]
        prev = runs[1] if len(runs) > 1 else None
        curr_count = repo_count(conn, curr_id)
        prev_count = repo_count(conn, prev[0]) if prev else None
        if prev_count is not None:
            any_previous = True
            total_previous += prev_count
        total_current += curr_count
        run_label = f'run {curr_id} · {fmt_date(curr_at)}'
        if curr_notes:
            run_label += f' · _{curr_notes}_'
        lines.append(f'| {label} | {curr_count} | {delta_str(curr_count, prev_count)} | {run_label} |')

    total_delta = delta_str(total_current, total_previous if any_previous else None)
    lines.append(f'| **Total** | **{total_current}** | **{total_delta}** | |')
    return lines


def section_new_repos(conn):
    lines = ['## 2. New Repos Since Last Run', '']

    for label, script in CODE_SCRIPTS.items():
        lines.append(f'### {label}')
        lines.append('')
        runs = latest_runs(conn, script, n=2)
        if not runs or len(runs) < 2:
            lines.append('_No previous run to compare against._')
            lines.append('')
            continue
        current = repo_set(conn, runs[0][0])
        previous = repo_set(conn, runs[1][0])
        added = {r: u for r, u in current.items() if r not in previous}
        removed = {r: u for r, u in previous.items() if r not in current}
        if not added and not removed:
            lines.append('_No changes since previous run._')
            lines.append('')
            continue
        if added:
            lines.append(f'**Added ({len(added)})**')
            lines.append('')
            for repo, url in sorted(added.items()):
                lines.append(f'- [{repo}]({url})')
            lines.append('')
        if removed:
            lines.append(f'**Removed ({len(removed)})**')
            lines.append('')
            for repo, url in sorted(removed.items()):
                lines.append(f'- [{repo}]({url})')
            lines.append('')

    return lines


def section_orgs(conn):
    lines = ['## 3. Adoption by Organization (PR signal)', '']
    lines.append('Top organizations by unique PR count from the most recent per-org run (forks excluded).')
    lines.append('')

    any_data = False
    for label, script in ORG_PR_SCRIPTS.items():
        run_at, rows = top_orgs(conn, script)
        lines.append(f'### {label}')
        lines.append('')
        if not rows:
            lines.append('_No data. Run the per-org PR scripts with `--db` to populate._')
            lines.append('')
            continue
        any_data = True
        lines.append(f'_As of {fmt_date(run_at)}_')
        lines.append('')
        lines.append('| Organization | PRs |')
        lines.append('|---|---|')
        for org, prs in rows:
            lines.append(f'| {org} | {prs} |')
        lines.append('')

    return lines


def section_signals(conn):
    lines = ['## 4. Signal Breakdown', '']
    lines.append('Which signals are driving hits in the current run (forks excluded).')
    lines.append('')

    for label, script in CODE_SCRIPTS.items():
        lines.append(f'### {label}')
        lines.append('')
        runs = latest_runs(conn, script, n=1)
        if not runs:
            lines.append('_No data._')
            lines.append('')
            continue
        rows = signal_breakdown(conn, runs[0][0])
        if not rows:
            lines.append('_No results._')
            lines.append('')
            continue
        lines.append('| Signal | Repos | Phase |')
        lines.append('|---|---|---|')
        for signal, phase, repos in rows:
            lines.append(f'| `{signal}` | {repos} | {phase} |')
        lines.append('')

    return lines


def section_trend(conn):
    lines = ['## 5. Adoption Trend', '']
    lines.append('Total adopting repositories per run (forks excluded).')
    lines.append('')

    for label, script in CODE_SCRIPTS.items():
        rows = trend_data(conn, script)
        lines.append(f'**{label}**')
        lines.append('')
        if not rows:
            lines.append('_No data._')
            lines.append('')
            continue
        max_val = max(r[2] for r in rows) or 1
        lines.append('```')
        for run_at, notes, count in rows:
            bar = ascii_bar(count, max_val)
            run_label = fmt_date(run_at)
            if notes:
                run_label += f' ({notes})'
            lines.append(f'{run_label:<32}  {bar:<{BAR_WIDTH}}  {count}')
        lines.append('```')
        lines.append('')

    return lines


# ── Main ──────────────────────────────────────────────────────────────────────

def generate_report(db_path, out):
    conn = sqlite3.connect(db_path)

    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    header = [
        '# Open edX Plugin Adoption Report',
        '',
        f'_Generated: {now}_',
        '',
    ]

    sections = (
        section_snapshot(conn)
        + ['']
        + section_new_repos(conn)
        + section_orgs(conn)
        + section_signals(conn)
        + section_trend(conn)
    )

    conn.close()
    out.write('\n'.join(header + sections) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a Markdown adoption report from the SQLite database.')
    parser.add_argument('--db', required=True, help='Path to SQLite database file')
    parser.add_argument('--out', help='Output file path (default: stdout)')
    args = parser.parse_args()

    if args.out:
        with open(args.out, 'w') as f:
            generate_report(args.db, f)
    else:
        generate_report(args.db, sys.stdout)
