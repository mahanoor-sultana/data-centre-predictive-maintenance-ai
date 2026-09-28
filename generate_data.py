import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N_SERVERS = 20
DAYS = 14

def main():
    out = Path("data/raw")
    out.mkdir(parents=True, exist_ok=True)
    timestamps = pd.date_range(
        "2026-08-01 00:00:00",
        periods=int(DAYS * 24 * 60 / 5),
        freq="5min"
    )

    rows = []
    for server_num in range(1, N_SERVERS + 1):
        server_id = f"SRV{server_num:03d}"
        rack_id = f"RACK{((server_num - 1) // 5) + 1:02d}"
        base_cpu = RNG.uniform(30, 50)
        base_mem = RNG.uniform(45, 65)
        base_temp = RNG.uniform(22, 27)
        base_power = RNG.uniform(2.2, 3.5)
        incident_starts = sorted(RNG.choice(len(timestamps) - 30, size=2, replace=False))

        for i, ts in enumerate(timestamps):
            hour = ts.hour + ts.minute / 60
            workload = 8 * np.sin((hour - 8) / 24 * 2 * np.pi) + 5

            cpu = np.clip(base_cpu + workload + RNG.normal(0, 3), 5, 100)
            memory = np.clip(base_mem + 0.25 * (cpu - 40) + RNG.normal(0, 3), 10, 100)
            disk = np.clip(45 + 0.015 * i + RNG.normal(0, 2), 10, 98)
            network = max(20, 300 + 2.5 * cpu + RNG.normal(0, 35))
            fan = np.clip(1900 + 28 * max(0, cpu - 45) + RNG.normal(0, 90), 1000, 5000)
            temp = base_temp + 0.055 * cpu + 0.0018 * (fan - 1900) + RNG.normal(0, 0.7)
            power = base_power + 0.018 * cpu + RNG.normal(0, 0.08)
            errors = max(0, int(RNG.poisson(0.15)))
            incident_type = "None"

            for start in incident_starts:
                distance = i - start
                if 0 <= distance <= 18:
                    incident_type = "Thermal Stress"
                    severity = min(distance / 18, 1)
                    cpu = min(99, cpu + 30 * severity)
                    temp += 5.5 * severity
                    power += 1.1 * severity
                    errors += int(RNG.poisson(2.5 * severity))
                    fan = min(5000, fan + 700 * severity)

            if (server_num % 7 == 0) and (3000 < i < 3500):
                incident_type = "Disk Degradation"
                disk = min(99, disk + 20)
                errors += int(RNG.poisson(4))
                network = max(10, network - 100)

            anomaly = int(
                incident_type != "None" or temp > 34 or cpu > 90 or
                errors >= 5 or disk > 90
            )

            future_failure = int(any(0 < start - i <= 288 for start in incident_starts))

            rows.append([
                ts, server_id, rack_id, round(cpu, 2), round(memory, 2),
                round(disk, 2), round(temp, 2), round(network, 2),
                round(fan, 1), round(power, 2), errors, anomaly,
                future_failure, incident_type
            ])

    columns = [
        "Timestamp", "Server_ID", "Rack_ID", "CPU_pct", "Memory_pct",
        "Disk_pct", "Temperature_C", "Network_MBps", "Fan_RPM",
        "Power_kW", "Error_Count", "Anomaly_Flag",
        "Failure_Within_24h", "Incident_Type"
    ]
    df = pd.DataFrame(rows, columns=columns)
    path = out / "data_centre_sensor_data.csv"
    df.to_csv(path, index=False)

    print(f"Created {len(df):,} rows")
    print(f"Anomaly rate: {df['Anomaly_Flag'].mean() * 100:.2f}%")
    print(f"Failure-within-24h rate: {df['Failure_Within_24h'].mean() * 100:.2f}%")
    print(f"Saved to: {path}")

if __name__ == "__main__":
    main()
