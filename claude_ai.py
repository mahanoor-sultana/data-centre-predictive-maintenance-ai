import os
import anthropic


def analyze_incident(row):

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "message": "ANTHROPIC_API_KEY is not configured."
        }

    client = anthropic.Anthropic(
        api_key=api_key
    )

    prompt = f"""
You are an AI assistant for data centre operations.

Analyze this infrastructure event using ONLY the provided sensor data.

Server ID: {row.get('Server_ID', 'Unknown')}
Rack ID: {row.get('Rack_ID', 'Unknown')}

Predicted Failure Risk: {row.get('Risk_Score', 0):.2f}%
Risk Level: {row.get('Risk_Level', 'Unknown')}

CPU: {row.get('CPU_pct', 0):.2f}%
Memory: {row.get('Memory_pct', 0):.2f}%
Disk: {row.get('Disk_pct', 0):.2f}%
Temperature: {row.get('Temperature_C', 0):.2f} C
Network: {row.get('Network_MBps', 0):.2f} MB/s
Fan RPM: {row.get('Fan_RPM', 0):.2f}
Power: {row.get('Power_kW', 0):.2f} kW
Errors: {row.get('Error_Count', 0)}
Anomaly Flag: {row.get('Anomaly_Flag', 0)}

Provide a concise data-centre operations analysis.

Return these sections:

INCIDENT SUMMARY:
ROOT CAUSE ANALYSIS:
OPERATIONAL IMPACT:
RECOMMENDED ACTIONS:
PRIORITY:
MAINTENANCE WINDOW:

Do not invent measurements or claim that a component has failed unless supported by the data.
"""

    try:

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=700,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "status": "success",
            "analysis": response.content[0].text
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }