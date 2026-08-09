## Dataset Description

This dataset contains operational data recorded from centrifugal pumps that supply demineralized water to the boilers of a heating plant. The plant provides the steam required by the research test facilities at CIRA (Italian Aerospace Research Centre).

The dataset comprises eight CSV files, each representing data collected from a specific centrifugal pump during a single operational day. Filenames uniquely identify both the pump unit (`A`, `B`, or `C`) and the corresponding date of operation. For example, the file `A_2024-04-10.csv` contains data recorded from centrifugal pump A on April 10, 2024.

At the time of writing, the dataset includes records from three distinct operational days, each covering a different time span.

> **Note:** Data for pump **C** is not available for **October 30, 2024**, as the pump was turned off on that day.

Each CSV file contains **11 columns**: one for the timestamp and ten for measured values. The column headers are listed in the table below, where the prefix `X` represents the centrifugal pump unit label (e.g., `A`, `B`, or `C`):

### Column Descriptions

| **Column Name**       | **Description**                                                                 | **Unit of Measure** |
|-----------------------|----------------------------------------------------------------------------------|---------------------|
| `Timestamp`           | Temporal timestamp indicating when the measurement was taken (format: `YYYY-MM-DD hh:mm:ss`) | -                   |
| `X_ACR_Mot.PV`        | Displacement measured by the motor accelerometer                                | m/s                 |
| `X_ACR_Mot.SV`        | Peak value measured by the motor accelerometer                                  | m/s²                |
| `X_ACR_Mot.TV`        | Contact temperature of the motor accelerometer                                  | °C                  |
| `X_ACR_Pmp.PV`        | Displacement measured by the pump accelerometer                                 | m/s                 |
| `X_ACR_Pmp.SV`        | Peak value measured by the pump accelerometer                                   | m/s²                |
| `X_ACR_Pmp.TV`        | Contact temperature of the pump accelerometer                                   | °C                  |
| `X_Temp.SV`           | Motor casing temperature                                                         | °C                  |
| `X_Pres.SV`           | Outlet fluid pressure from the pump                                              | bar                 |
| `Barometer`           | Atmospheric pressure                                                             | mbar                |
| `Temperature`         | Ambient temperature                                                              | °C                  |

---

For any inquiries or issues regarding the dataset, please contact [a.martone@cira.it](mailto:a.martone@cira.it) and/or [g.zazzaro@cira.it](mailto:g.zazzaro@cira.it)
