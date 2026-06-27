from datetime import datetime, timedelta
import calendar

START_YEAR = datetime.now().year
YEARS_AHEAD = 2


def third_friday(year, month):
    c = calendar.Calendar()
    fridays = [d for d in c.itermonthdates(year, month)
               if d.weekday() == 4 and d.month == month]
    return fridays[2]


def fourth_wednesday(year, month):
    c = calendar.Calendar()
    ws = [d for d in c.itermonthdates(year, month)
          if d.weekday() == 2 and d.month == month]
    return ws[3]


def last_business_days(year, month, n=2):
    c = calendar.Calendar()
    days = [d for d in c.itermonthdates(year, month)
            if d.month == month and d.weekday() < 5]
    return days[-n]


def add_event(events, date, title, desc):
    events.append({
        "date": date.strftime("%Y%m%d"),
        "title": title,
        "desc": desc
    })


events = []

for year in range(START_YEAR, START_YEAR + YEARS_AHEAD):
    for m in range(1, 13):

        # ========== 股指交割 ==========
        d = third_friday(year, m)
        add_event(events, d,
                  "股指期货/期权交割日（高波动）",
                  "T-2/T-1/T/T+1 风险窗口")

        for i in range(1, 3):
            add_event(events, d - timedelta(days=i),
                      "股指交割前风险窗口",
                      "流动性下降 + 移仓加速")

        add_event(events, d + timedelta(days=1),
                  "股指交割后波动延续",
                  "结算余波")

        # ========== ETF期权 ==========
        d2 = fourth_wednesday(year, m)
        add_event(events, d2,
                  "ETF期权行权日（高波动）",
                  "Gamma风险 + 归零效应")

        # ========== A50 ==========
        if m in [2, 3, 5, 6, 8, 9, 11, 12]:
            a50 = last_business_days(year, m, 2)[1]

            add_event(events, a50,
                      "富时A50交割日（极高波动）",
                      "外盘联动 + 北向影响")

            for i in range(1, 4):
                add_event(events, a50 - timedelta(days=i),
                          "A50交割风险窗口",
                          "跨市场波动放大")

        # ========== 月末窗口 ==========
        last_day = calendar.monthrange(year, m)[1]
        end = datetime(year, m, last_day)

        for i in range(0, 3):
            add_event(events, end - timedelta(days=i),
                      "月末调仓窗口",
                      "资金再平衡 + 波动放大")

        # ========== 季度窗口 ==========
        if m in [3, 6, 9, 12]:
            q_end = end
            for i in range(3):
                add_event(events, q_end - timedelta(days=i),
                          "季度结算窗口",
                          "期货/期权/ETF共振波动")


def export_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "PRODID:-//China Derivatives Calendar//CN"
    ]

    for e in events:
        lines += [
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{e['date']}",
            f"SUMMARY:{e['title']}",
            f"DESCRIPTION:{e['desc']}",
            "END:VEVENT"
        ]

    lines.append("END:VCALENDAR")
    return "\n".join(lines)


with open("calendar.ics", "w") as f:
    f.write(export_ics(events))

print("calendar.ics generated")
