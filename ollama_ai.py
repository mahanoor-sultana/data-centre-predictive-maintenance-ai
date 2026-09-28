import ollama
from datetime import datetime


def analyze_incident(row):

    try:

        current_date = datetime.now().strftime("%d-%m-%Y")

        prompt = f"""
You are an AI Operations Engineer working in a modern data centre.

Investigate the predicted server failure risk using ONLY the
provided server information, predictive model output, and
sensor measurements.

IMPORTANT:
The risk score is a MACHINE LEARNING PREDICTION.
It does NOT mean that a hardware failure has already occurred.

Do not invent information.
Do not invent sensor values.
Do not claim a confirmed hardware failure.
Do not use phrases such as "[Current Date]".
Use the actual report date: {current_date}.

============================================================
SERVER INFORMATION
============================================================

Server ID: {row.get('Server_ID', 'Unknown')}
Rack ID: {row.get('Rack_ID', 'Unknown')}

============================================================
PREDICTIVE MODEL OUTPUT
============================================================

Predicted Failure Risk: {float(row.get('Risk_Score', 0)):.2f}%
Risk Level: {row.get('Risk_Level', 'Unknown')}

Explain that this is a predictive model result and not
confirmation of an actual failure.

============================================================
OBSERVED SENSOR CONDITIONS
============================================================

CPU Utilization: {float(row.get('CPU_pct', 0)):.2f}%
Memory Utilization: {float(row.get('Memory_pct', 0)):.2f}%
Disk Utilization: {float(row.get('Disk_pct', 0)):.2f}%
Temperature: {float(row.get('Temperature_C', 0)):.2f} °C
Network Traffic: {float(row.get('Network_Traffic_MBps', 0)):.2f} MB/s
Fan Speed: {float(row.get('Fan_Speed_RPM', 0)):.2f} RPM
Power Consumption: {float(row.get('Power_kW', 0)):.2f} kW
Error Count: {int(row.get('Error_Count', 0))}
Anomaly Flag: {int(row.get('Anomaly_Flag', 0))}

============================================================
ANALYSIS REQUIREMENTS
============================================================

1. Compare the sensor values with the predicted risk.

2. Identify which observed measurements may contribute to
   the elevated predicted risk.

3. Clearly mention when a sensor value appears normal or
   does not provide evidence of an immediate failure.

4. Explain that machine-learning models can identify risk
   from combinations and patterns of variables, even when
   individual sensor values are not extreme.

5. Do not assume that a high risk score means a confirmed
   hardware failure.

6. If the available measurements are insufficient to determine
   an exact root cause, explicitly state that.

7. Identify plausible contributing factors only when supported
   by the provided measurements.

8. Recommend practical actions that a data-centre operations
   team can perform.

9. Keep the report professional and technically realistic.

10. Do not introduce sensor values, hardware components,
    incidents, or events that are not present in the data.

============================================================
REPORT DATE
============================================================

Report Date: {current_date}

============================================================
REQUIRED REPORT FORMAT
============================================================

Use exactly these sections:

INCIDENT SUMMARY

State the server, rack, report date, predicted risk score,
and risk level. Clearly state that this is a predicted risk,
not a confirmed failure.

OBSERVED CONDITIONS

List the actual sensor measurements provided above.
Explain which measurements appear normal, elevated, or
potentially relevant based only on the available data.

RISK ASSESSMENT

Explain what the 82.5% predicted risk represents.
Explain that the model may be responding to a combination
of sensor patterns rather than one extreme measurement.

POSSIBLE ROOT CAUSE

Identify plausible contributing factors supported by the data.
If an exact root cause cannot be established, say so clearly.

EVIDENCE

Summarize the specific sensor measurements that support
the assessment.

OPERATIONAL IMPACT

Explain the potential operational consequences if the
predicted risk develops into an actual failure.
Do not state that an outage or failure has already occurred.

IMMEDIATE ACTIONS

Provide practical investigation and monitoring steps.

MAINTENANCE RECOMMENDATION

Provide preventive maintenance recommendations based
on the available evidence.

PRIORITY

State an operational priority based on the predicted
risk level, while making clear that the risk is predictive.

FINAL ASSESSMENT

Provide a concise final assessment explaining:
- what the model predicts
- what the sensor data currently shows
- what is still uncertain
- what the operations team should investigate next
"""

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        analysis = response["message"]["content"]

# Replace any placeholder dates/times generated by the AI
        current_datetime = datetime.now()

        report_date = current_datetime.strftime("%d-%m-%Y")
        report_time = current_datetime.strftime("%H:%M:%S")

        analysis = analysis.replace(
            "[Insert Date]",
            report_date
        )

        analysis = analysis.replace(
            "[Insert Time]",
            report_time
        )

        analysis = analysis.replace(
            "[Current Date]",
            report_date
        )

        analysis = analysis.replace(
            "[Current Time]",
            report_time
        )

        return {
            "status": "success",
            "analysis": analysis
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }