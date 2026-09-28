import os
from groq import Groq


def analyze_incident(row):

    try:

        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            return {
                "status": "error",
                "message": "GROQ_API_KEY is not configured."
            }

        client = Groq(
            api_key=api_key
        )

        prompt = f"""
You are an AI operations engineer working in a modern data centre.

Analyze the following server incident using ONLY the provided
sensor measurements and predicted failure risk.

SERVER INFORMATION
Server ID: {row.get('Server_ID', 'Unknown')}
Rack ID: {row.get('Rack_ID', 'Unknown')}

PREDICTIVE RISK
Risk Score: {float(row.get('Risk_Score', 0)):.2f}%
Risk Level: {row.get('Risk_Level', 'Unknown')}

OBSERVED SENSOR CONDITIONS
CPU Utilization: {float(row.get('CPU_pct', 0)):.2f}%
Memory Utilization: {float(row.get('Memory_pct', 0)):.2f}%
Disk Utilization: {float(row.get('Disk_pct', 0)):.2f}%
Temperature: {float(row.get('Temperature_C', 0)):.2f} °C
Network Traffic: {float(row.get('Network_Traffic_MBps', 0)):.2f} MB/s
Fan Speed: {float(row.get('Fan_Speed_RPM', 0)):.2f} RPM
Power Consumption: {float(row.get('Power_kW', 0)):.2f} kW
Error Count: {int(row.get('Error_Count', 0))}
Anomaly Flag: {int(row.get('Anomaly_Flag', 0))}

Write a concise but professional data-centre incident investigation report.

IMPORTANT:
- Do not invent sensor values.
- Do not claim a hardware failure has definitely occurred.
- Distinguish predicted risk from confirmed failure.
- If the available data is insufficient to identify an exact root cause,
  say so, but identify the most plausible contributing factors.
- Base explanations on the actual sensor values.
- Recommend practical actions for a data-centre operations team.

Use exactly these sections:

INCIDENT SUMMARY

OBSERVED CONDITIONS

RISK ASSESSMENT

POSSIBLE ROOT CAUSE

EVIDENCE

OPERATIONAL IMPACT

IMMEDIATE ACTIONS

MAINTENANCE RECOMMENDATION

PRIORITY

FINAL ASSESSMENT
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        analysis = response.choices[0].message.content

        return {
            "status": "success",
            "analysis": analysis
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }