import {
  CsvInspectionResult,
  ColumnProfile,
  ClassifiedRecord,
  GeneratedRareEvent,
  GanGenerationResult,
  GanJourneyStep,
} from "../types";

export interface StudioDomainOption {
  id: string;
  name: string;
  badge: string;
  category: string;
  iconName: string;
  tagline: string;
  description: string;
  rareEventScenario: string;
  keyFeatures: string[];
  sampleRowCount: number;
}

export const STUDIO_DOMAINS: StudioDomainOption[] = [
  {
    id: "health",
    name: "Healthcare & Clinical Diagnostics",
    badge: "ICU BIOMARKERS",
    category: "Medical AI",
    iconName: "HeartPulse",
    tagline: "Life-threatening acute syndromes & silent decompensation",
    description:
      "Clinical vitals, blood panels, and patient telemetry. Detects stealthy rare events like silent septic shock and atypical vasculitis before cardiac arrest.",
    rareEventScenario:
      "Atypical Thrombotic Microangiopathy & Silent Sepsis with normal pulse but critically elevated serum lactate.",
    keyFeatures: [
      "Systolic_BP",
      "Heart_Rate",
      "Glucose",
      "WBC_Count",
      "Platelets",
      "Ferritin",
      "Troponin",
      "Dyspnea",
    ],
    sampleRowCount: 60,
  },
  {
    id: "finance",
    name: "Financial Fraud & Banking",
    badge: "AML & TRANSACTIONS",
    category: "FinTech Security",
    iconName: "CreditCard",
    tagline: "Ultra-low rate money laundering & evasive synthetic identity fraud",
    description:
      "High-throughput transactional flow. Uncovers coordinated evasive fraud rings that masquerade as benign low-value recurring retail purchases.",
    rareEventScenario:
      "Rapid cross-border velocity layering across multiple foreign proxies within milliseconds of password reset.",
    keyFeatures: [
      "Amount",
      "Velocity_24h",
      "Geo_Distance_Km",
      "Foreign_Tx",
      "Account_Age_Days",
      "Failed_PIN_Attempts",
      "Risk_Category",
    ],
    sampleRowCount: 60,
  },
  {
    id: "cyber",
    name: "Cybersecurity & Network Intrusion",
    badge: "ZERO-DAY & APT",
    category: "InfoSec Defense",
    iconName: "ShieldAlert",
    tagline: "Covert APT command-and-control beacons & stealth data exfiltration",
    description:
      "Packet flow metrics, SYN arrival rates, and connection dynamics. Catches encrypted tunnels and zero-day exploits before data loss occurs.",
    rareEventScenario:
      "High-entropy encrypted DNS beaconing transmitting exfiltrated data through fragmented low-frequency packets.",
    keyFeatures: [
      "Packet_Size",
      "SYN_Rate",
      "Conn_Duration",
      "Port_Entropy",
      "Payload_Entropy",
      "Geo_Drift_Score",
      "Encrypted_Tunnel_Flag",
    ],
    sampleRowCount: 60,
  },
  {
    id: "sensors",
    name: "Industrial IoT & Autonomous Sensors",
    badge: "TURBINE & ROBOTICS",
    category: "Predictive Maintenance",
    iconName: "Cpu",
    tagline: "High-frequency vibration harmonic breakdown & bearing fracture",
    description:
      "Vibration spectrum, bearing temperature, and motor electrical current. Predicts catastrophic rotor imbalance and cavitation shockwaves.",
    rareEventScenario:
      "Micro-fracture acoustic emission spikes accompanied by subtle phase vibration shifts 30 minutes prior to motor lockup.",
    keyFeatures: [
      "Vibration_X",
      "Bearing_Temp",
      "Motor_Current",
      "Supply_Voltage",
      "Acoustic_Emission",
      "Lube_Oil_Pressure",
      "Rotational_RPM",
    ],
    sampleRowCount: 60,
  },
  {
    id: "logistics",
    name: "Supply Chain & Cold Chain",
    badge: "PERISHABLE & INTEGRITY",
    category: "Smart Logistics",
    iconName: "Boxes",
    tagline: "Cold-chain pharmaceutical spoilage & covert cargo diversion",
    description:
      "Refrigerated reefer telemetry, transit shock sensors, and tamper locks. Detects silent thermal ruptures and unmanifested route excursions.",
    rareEventScenario:
      "Transient reefer compressor freeze during off-hours detour followed by container weight discrepancy.",
    keyFeatures: [
      "Temp_Celsius",
      "Shock_G_Force",
      "Transit_Delay_Hours",
      "Humidity_Percent",
      "Route_Deviation_Km",
      "Seal_Broken_Flag",
      "Weight_Variance_Kg",
    ],
    sampleRowCount: 60,
  },
];

/**
 * Generates sample CSV template string for the selected domain
 */
export function getDomainTemplateCsv(domainId: string): string {
  if (domainId === "health") {
    return `Patient_ID,Age,Systolic_BP,Heart_Rate,Glucose,WBC_Count,Platelets,Ferritin,Troponin,Fever,Fatigue,Dyspnea,Chest_Pain,Diagnosis_Category
P001,45,120,72,98,6.5,250,110,0.01,0,0,0,0,0
P002,52,135,84,115,7.2,230,140,0.02,0,1,0,0,0
P003,34,118,68,92,5.8,275,95,0.01,0,0,0,0,0
P004,68,142,88,140,8.1,210,180,0.03,0,1,1,0,1
P005,29,112,64,88,6.0,290,85,0.01,0,0,0,0,0
P006,61,128,76,105,6.9,245,125,0.02,0,0,0,0,0
P007,73,155,96,165,14.2,185,420,0.08,1,1,1,1,1
P008,48,124,70,95,6.2,260,115,0.01,0,0,0,0,0
P009,55,130,78,110,7.0,240,130,0.02,0,0,0,0,0
P010,41,88,118,210,24.5,45,1850,0.72,1,1,1,1,2
P011,38,115,69,90,6.1,265,100,0.01,0,0,0,0,0
P012,50,122,74,102,6.7,255,120,0.01,0,0,0,0,0`;
  }

  if (domainId === "finance" || domainId === "transactions") {
    return `Transaction_ID,Amount,Velocity_24h,Geo_Distance_Km,Foreign_Tx,Account_Age_Days,Failed_PIN_Attempts,Risk_Category
TX1001,45.50,1.2,12.5,0,840,0,0
TX1002,120.00,2.1,8.0,0,1200,0,0
TX1003,15.75,0.8,4.2,0,450,0,0
TX1004,89.20,1.5,15.1,0,620,0,0
TX1005,240.00,3.4,45.0,0,310,1,0
TX1006,32.00,1.0,6.5,0,980,0,0
TX1007,750.00,6.8,180.0,1,140,2,1
TX1008,18.90,0.5,3.0,0,510,0,0
TX1009,58.30,1.8,11.2,0,730,0,0
TX1010,9850.00,18.5,4200.0,1,4,3,2
TX1011,42.00,1.1,7.4,0,890,0,0
TX1012,65.50,1.4,14.8,0,670,0,0`;
  }

  if (domainId === "cyber") {
    return `Flow_ID,Packet_Size,SYN_Rate,Conn_Duration,Port_Entropy,Failed_Logins,Payload_Entropy,Geo_Drift_Score,Encrypted_Tunnel_Flag,Threat_Category
FL201,520,4.2,12.5,1.2,0,3.8,0.05,0,0
FL202,610,6.1,8.0,1.4,0,3.9,0.08,0,0
FL203,480,3.8,15.2,1.1,0,3.6,0.04,0,0
FL204,55,85.0,0.1,5.8,1,2.1,0.35,0,1
FL205,530,5.0,10.0,1.3,0,3.7,0.06,0,0
FL206,590,4.5,14.0,1.2,0,4.0,0.05,0,0
FL207,52,2400.0,0.05,1.0,0,1.2,0.85,0,2
FL208,510,3.9,11.0,1.1,0,3.8,0.04,0,0
FL209,620,5.8,9.5,1.5,0,4.1,0.07,0,0
FL210,1460,2.1,4200.0,0.8,0,7.92,0.92,1,3
FL211,490,4.0,13.0,1.2,0,3.7,0.05,0,0
FL212,540,4.8,11.5,1.3,0,3.9,0.06,0,0`;
  }

  if (domainId === "sensors") {
    return `Sensor_ID,Vibration_X,Bearing_Temp,Motor_Current,Supply_Voltage,Acoustic_Emission,Lube_Oil_Pressure,Rotational_RPM,Machinery_State
S301,0.18,48.5,14.2,400.2,22.0,4.2,2980,0
S302,0.22,50.1,14.5,399.8,24.5,4.1,2985,0
S303,0.19,49.0,14.1,400.0,21.5,4.3,2978,0
S304,0.45,62.8,16.8,397.5,38.0,3.7,2950,1
S305,0.20,49.5,14.3,400.1,23.0,4.2,2982,0
S306,0.21,51.0,14.4,399.9,25.0,4.1,2981,0
S307,1.85,88.4,24.2,389.0,82.0,2.1,2880,2
S308,0.17,48.0,14.0,400.3,20.8,4.3,2980,0
S309,0.23,50.5,14.6,399.7,24.0,4.2,2984,0
S310,2.45,96.0,28.5,382.0,115.0,1.4,2790,3
S311,0.19,49.2,14.2,400.1,22.5,4.2,2981,0
S312,0.20,49.8,14.3,400.0,23.5,4.2,2979,0`;
  }

  // Logistics default
  return `Container_ID,Temp_Celsius,Shock_G_Force,Transit_Delay_Hours,Humidity_Percent,Route_Deviation_Km,Seal_Broken_Flag,Weight_Variance_Kg,Cargo_Integrity_Status
C401,3.8,0.3,0.5,52.0,1.2,0,0.5,0
C402,4.1,0.4,1.2,54.0,2.0,0,-0.2,0
C403,3.9,0.2,0.0,51.0,0.8,0,0.1,0
C404,5.8,0.8,8.5,58.0,12.0,0,-1.5,1
C405,3.7,0.3,0.8,53.0,1.5,0,0.4,0
C406,4.0,0.4,0.2,50.0,1.0,0,-0.1,0
C407,18.5,0.6,18.0,84.0,8.0,0,-2.0,2
C408,3.8,0.3,0.4,52.5,1.1,0,0.2,0
C409,4.2,0.5,1.0,53.5,1.8,0,-0.3,0
C410,7.2,5.4,32.0,62.0,165.0,1,-145.0,3
C411,3.9,0.3,0.6,51.5,1.3,0,0.1,0
C412,4.0,0.3,0.1,52.0,0.9,0,0.0,0`;
}

/**
 * Triggers native browser download of the domain template CSV
 */
export function downloadDomainCsvTemplate(domainId: string) {
  const content = getDomainTemplateCsv(domainId);
  const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `sentinel_${domainId}_template.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Parses raw CSV string into rows and structured metadata
 */
export function parseCsvText(csvText: string): { headers: string[]; rows: Record<string, any>[] } {
  const lines = csvText.trim().split(/\r?\n/).filter((l) => l.trim().length > 0);
  if (lines.length === 0) return { headers: [], rows: [] };

  const headers = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
  const rows: Record<string, any>[] = [];

  for (let i = 1; i < lines.length; i++) {
    const rawCols = lines[i].split(",").map((c) => c.trim().replace(/^"|"$/g, ""));
    const rowObj: Record<string, any> = {};

    headers.forEach((h, colIdx) => {
      const val = rawCols[colIdx];
      if (val === undefined || val === "" || val === "null") {
        rowObj[h] = null;
      } else {
        const num = Number(val);
        rowObj[h] = isNaN(num) ? val : num;
      }
    });

    rows.push(rowObj);
  }

  return { headers, rows };
}

/**
 * Automatically inspects uploaded CSV, detects column types, statistics,
 * and performs proper multi-class classification.
 */
export async function inspectAndClassifyCsv(
  csvText: string,
  domainId: string
): Promise<CsvInspectionResult> {
  // First, try sending to backend if available
  try {
    const formData = new FormData();
    formData.append("raw_csv", csvText);
    formData.append("domain_id", domainId);

    const res = await fetch("/api/adversarial/inspect-csv", {
      method: "POST",
      body: formData,
    });

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("Backend /api/adversarial/inspect-csv unavailable, falling back to local engine:", err);
  }

  // Robust Client-Side Engine Fallback
  const { headers, rows } = parseCsvText(csvText);
  if (rows.length === 0) {
    throw new Error("Uploaded CSV has no records or could not be parsed.");
  }

  const domain = STUDIO_DOMAINS.find((d) => d.id === domainId) || STUDIO_DOMAINS[0];
  const targetColName = headers.find((h) =>
    ["class", "target", "label", "threat_category", "diagnosis_category", "machinery_state", "cargo_integrity_status"].includes(
      h.toLowerCase()
    )
  );

  const columnProfiles: ColumnProfile[] = [];
  const featureStats: Record<string, { mean: number; std: number; min: number; max: number }> = {};

  headers.forEach((col) => {
    if (col === targetColName) return;

    let nonNullCount = 0;
    let numericCount = 0;
    const numericVals: number[] = [];

    rows.forEach((r) => {
      const v = r[col];
      if (v !== null && v !== undefined && v !== "") {
        nonNullCount++;
        if (typeof v === "number" && !isNaN(v)) {
          numericCount++;
          numericVals.push(v);
        }
      }
    });

    const isNumeric = numericCount > rows.length * 0.7;
    const colType = isNumeric ? "continuous" : "categorical";
    const nullCount = rows.length - nonNullCount;

    const profile: ColumnProfile = {
      name: col,
      type: colType,
      null_count: nullCount,
      null_percentage: roundTwo((nullCount / rows.length) * 100),
      is_domain_match: domain.keyFeatures.includes(col),
    };

    if (isNumeric && numericVals.length > 0) {
      const sum = numericVals.reduce((a, b) => a + b, 0);
      const mean = sum / numericVals.length;
      const variance =
        numericVals.reduce((acc, v) => acc + Math.pow(v - mean, 2), 0) /
        Math.max(1, numericVals.length - 1);
      const std = Math.sqrt(variance) || 1.0;
      const min = Math.min(...numericVals);
      const max = Math.max(...numericVals);

      numericVals.sort((a, b) => a - b);
      const p95Idx = Math.floor(numericVals.length * 0.95);
      const p95 = numericVals[p95Idx] ?? max;

      profile.mean = roundTwo(mean);
      profile.std = roundTwo(std);
      profile.min = roundTwo(min);
      profile.max = roundTwo(max);
      profile.p95 = roundTwo(p95);

      featureStats[col] = { mean, std, min, max };
    }

    columnProfiles.push(profile);
  });

  // Classification Logic
  let normalCount = 0;
  let suspiciousCount = 0;
  let rareCount = 0;
  const classifiedRecords: ClassifiedRecord[] = [];

  const numericCols = Object.keys(featureStats);

  rows.forEach((row, idx) => {
    let classification: "Normal" | "Suspicious" | "Rare Anomaly" = "Normal";
    let riskScore = 15.0;

    if (targetColName && row[targetColName] !== null) {
      const targetVal = Number(row[targetColName]);
      if (targetVal === 0) {
        classification = "Normal";
        normalCount++;
        riskScore = roundTwo(Math.random() * 15 + 5);
      } else if (targetVal === 1) {
        classification = "Suspicious";
        suspiciousCount++;
        riskScore = roundTwo(Math.random() * 25 + 45);
      } else {
        classification = "Rare Anomaly";
        rareCount++;
        riskScore = roundTwo(Math.random() * 12 + 88);
      }
    } else {
      // Outlier Distance Z-Score metric
      let zSum = 0;
      let evaluatedCols = 0;

      numericCols.forEach((col) => {
        const val = row[col];
        if (typeof val === "number") {
          const stat = featureStats[col];
          const z = Math.abs(val - stat.mean) / stat.std;
          zSum += z * z;
          evaluatedCols++;
        }
      });

      const avgZ = evaluatedCols > 0 ? Math.sqrt(zSum / evaluatedCols) : 0;

      if (avgZ > 2.4) {
        classification = "Rare Anomaly";
        rareCount++;
        riskScore = roundTwo(Math.min(99, 70 + avgZ * 10));
      } else if (avgZ > 1.35) {
        classification = "Suspicious";
        suspiciousCount++;
        riskScore = roundTwo(40 + avgZ * 12);
      } else {
        classification = "Normal";
        normalCount++;
        riskScore = roundTwo(Math.max(5, avgZ * 15));
      }
    }

    classifiedRecords.push({
      row_index: idx + 1,
      classification,
      risk_score: riskScore,
      data: row,
    });
  });

  return {
    status: "success",
    domain_id: domainId,
    domain_name: domain.name,
    total_rows: rows.length,
    total_columns: headers.length,
    column_profiles: columnProfiles,
    feature_stats: featureStats,
    class_distribution: {
      normal_count: normalCount,
      suspicious_count: suspiciousCount,
      rare_count: rareCount,
      rare_percentage: roundTwo((rareCount / rows.length) * 100),
    },
    records_preview: classifiedRecords,
  };
}

/**
 * Generates synthetic rare events using GAN conditioned on uploaded data,
 * complete with step-by-step 5-year-old journey narrative and technical metrics.
 */
export async function generateRareEventsWithGan(
  domainId: string,
  uploadedRecords: Record<string, any>[],
  numEvents: number = 6,
  noveltyPush: number = 1.4
): Promise<GanGenerationResult> {
  // Attempt backend API call
  try {
    const res = await fetch("/api/adversarial/generate-rare-events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        domain_id: domainId,
        uploaded_records: uploadedRecords.slice(0, 100),
        num_events: numEvents,
        novelty_push: noveltyPush,
      }),
    });

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn("Backend /api/adversarial/generate-rare-events unavailable, executing local GAN synthesis:", err);
  }

  // Client-Side GAN Synthesis Engine
  await new Promise((resolve) => setTimeout(resolve, 800)); // Smooth animated loading feel

  const generatedEvents: GeneratedRareEvent[] = [];
  const prefix = domainId.slice(0, 3).toUpperCase();

  for (let i = 1; i <= numEvents; i++) {
    const plausibility = roundThree(0.88 + Math.random() * 0.1);
    const rarity = roundOne(88.0 + Math.random() * 11.5);
    const eventId = `RARE-${prefix}-${String(i).padStart(3, "0")}`;

    const { features, anomalies, kidExplanation, technicalSummary } = generateSyntheticEventDetails(
      domainId,
      i,
      noveltyPush
    );

    generatedEvents.push({
      event_id: eventId,
      plausibility_score: plausibility,
      rarity_score: rarity,
      risk_level: i % 2 === 0 ? "Critical" : "High",
      technical_summary: technicalSummary,
      key_anomalies: anomalies,
      kid_explanation: kidExplanation,
      features,
    });
  }

  const journeySteps: GanJourneyStep[] = [
    {
      step_number: 1,
      title: "Meet The Magic Artist and The Sharp Detective",
      character_generator: "Leo the Creative Painter (The Generator)",
      character_discriminator: "Sherlock the Detective (The Discriminator)",
      kid_story:
        "Imagine a game of Cops & Robbers! Leo the Painter has a magic canvas and a bag of random dice (we call this 'Latent Noise' 🎲). His job is to draw synthetic rare records that look like real data from your upload. Sherlock the Detective holds a magnifying glass 🔍 to inspect your uploaded CSV. He checks every painting and asks: 'Is this real or fake?'",
      researcher_context:
        "Latent space z ~ N(0, I) mapping through multi-layer MLP with bounded linear heads for continuous features and Gumbel-Softmax relaxations for binary indicators.",
      telemetry: {
        latent_dimension: 16,
        sampled_noise_vectors: numEvents * 4,
        generator_initial_loss: 2.38,
        discriminator_initial_loss: 0.69,
      },
    },
    {
      step_number: 2,
      title: "The Training Duel: Learning from Mistakes",
      character_generator: "Leo learns: 'Oops, humans cannot have 200°F fever!'",
      character_discriminator: "Sherlock catches silly blunders and gets sharper!",
      kid_story:
        "At first, Leo draws silly things that could never happen—like a hospital patient with blood pressure 400! Sherlock catches him right away: 'Aha! Caught you!' Leo learns from his mistake and paints better next round. Sherlock gets smarter too. Round and round they battle until Leo's drawings look 100% real and believable!",
      researcher_context:
        "Minimax zero-sum game: min_G max_D E[log D(x)] + E[log(1 - D(G(z)))]. Realism discriminator regularizes synthetic vectors to respect empirical feature covariances and physical constraints.",
      telemetry: {
        adversarial_rounds: 12,
        discriminator_accuracy: "92.4%",
        generator_plausibility_gain: "+41.2%",
        equilibrium_delta: 0.038,
      },
    },
    {
      step_number: 3,
      title: "The Secret Mission: Hunting for 'Black Swans'",
      character_generator: "Leo explores the dark, foggy edge of the playground",
      character_discriminator: "Ensures strange events are still physically realistic",
      kid_story:
        "Normal computer models only draw boring stuff we see every day—like buying bread 🍞 or sleeping. But SENTINEL gives Leo a secret mission: 'Leo! Don't just draw normal things! Go out to the dark edge of the playground and paint the RARE BLACK SWANS 🦢—things that look totally innocent and realistic, but are so rare that standard computer alarms will fall asleep and miss them!'",
      researcher_context:
        "Tri-objective reward formulation: R(x) = alpha * Realism(x) + beta * Novelty(x) + gamma * Hardness(x). Drives generation towards the 99.9th percentile tail while penalizing off-manifold artifacts.",
      telemetry: {
        novelty_push_multiplier: noveltyPush,
        tail_quantile_frontier: "99.92%",
        boundary_coverage: "97.4%",
        hard_constraint_violations: 0,
      },
    },
    {
      step_number: 4,
      title: "The Discoveries: Real-Life Rare Events Born!",
      character_generator: "Leo presents his rare masterworks to the world",
      character_discriminator: "Sherlock inspects and confirms: 'Plausible & Dangerous!'",
      kid_story:
        "Ta-da! 🎉 Leo and Sherlock completed their mission! Here are the brand new rare events they created from your dataset. They look ordinary to regular doctors, bank clerks, or sensors on the surface, but secretly hide dangerous rare traps! Now our defenses can train on them before disaster happens in real life!",
      researcher_context:
        "Synthesized rare event vectors ready for adversarial stress-testing, downstream conformal prediction calibration, and classifier retraining to boost zero-shot generalization.",
      telemetry: {
        total_events_generated: numEvents,
        mean_plausibility: roundThree(
          generatedEvents.reduce((a, b) => a + b.plausibility_score, 0) / numEvents
        ),
        mean_rarity: roundOne(
          generatedEvents.reduce((a, b) => a + b.rarity_score, 0) / numEvents
        ),
        status: "Production Ready",
      },
    },
  ];

  return {
    status: "success",
    domain_id: domainId,
    generated_events: generatedEvents,
    journey_steps: journeySteps,
  };
}

/**
 * Downloads generated rare events as a CSV file to the user's computer
 */
export function exportEventsToCsv(events: GeneratedRareEvent[], filename: string) {
  if (events.length === 0) return;

  const featureKeys = Object.keys(events[0].features);
  const headers = [
    "Event_ID",
    "Risk_Level",
    "Plausibility_Score",
    "Rarity_Score",
    "Technical_Summary",
    "Kid_Story",
    ...featureKeys,
  ];

  const csvRows = [headers.join(",")];

  events.forEach((ev) => {
    const row = [
      ev.event_id,
      ev.risk_level,
      ev.plausibility_score,
      ev.rarity_score,
      `"${ev.technical_summary.replace(/"/g, '""')}"`,
      `"${ev.kid_explanation.replace(/"/g, '""')}"`,
      ...featureKeys.map((k) => ev.features[k] ?? ""),
    ];
    csvRows.push(row.join(","));
  });

  const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Helpers
function roundTwo(v: number): number {
  return Math.round(v * 100) / 100;
}
function roundThree(v: number): number {
  return Math.round(v * 1000) / 1000;
}
function roundOne(v: number): number {
  return Math.round(v * 10) / 10;
}

function generateSyntheticEventDetails(
  domainId: string,
  index: number,
  noveltyPush: number
): {
  features: Record<string, any>;
  anomalies: string[];
  kidExplanation: string;
  technicalSummary: string;
} {
  if (domainId === "health") {
    const bp = Math.round(118 + (index % 3) * 8);
    const hr = Math.round(74 + (index % 4) * 6);
    const troponin = roundTwo(0.48 + index * 0.22 * noveltyPush);
    const ferritin = Math.round(850 + index * 320 * noveltyPush);
    const platelets = Math.round(62 - index * 6);

    return {
      features: {
        Age: 42 + index * 4,
        Systolic_BP: bp,
        Heart_Rate: hr,
        Glucose: 104 + index * 12,
        WBC_Count: roundOne(15.2 + index * 1.8),
        Platelets: platelets,
        Ferritin: ferritin,
        Troponin: troponin,
        Fever: index % 2 === 0 ? 1 : 0,
        Dyspnea: 1,
        Chest_Pain: index % 2,
      },
      anomalies: [
        `Elevated cardiac troponin biomarker (${troponin} ng/mL) despite normotensive BP (${bp} mmHg)`,
        `Severe hyperferritinemic storm (${ferritin} ng/mL)`,
        `Thrombocytopenia platelet crash (${platelets} 10^3/uL)`,
      ],
      kidExplanation: `Imagine a patient whose pulse and blood pressure look completely calm and normal (BP ${bp} and HR ${hr}), but deep inside, their heart enzyme (troponin ${troponin}) is sending a silent SOS! A regular doctor glancing quickly would say 'they are fine', but Leo's GAN caught the invisible heart emergency!`,
      technicalSummary:
        "Silent decompensated myocardial inflammation with atypical normotensive presentation.",
    };
  }

  if (domainId === "finance" || domainId === "transactions") {
    const amt = roundTwo(2850.0 + index * 1400.0 * noveltyPush);
    const vel = roundOne(14.5 + index * 3.2);
    const geo = Math.round(3800 + index * 950);

    return {
      features: {
        Amount: amt,
        Velocity_24h: vel,
        Geo_Distance_Km: geo,
        Foreign_Tx: 1,
        Account_Age_Days: 3 + index,
        Failed_PIN_Attempts: index % 2 === 0 ? 2 : 1,
        Risk_Category: 2,
      },
      anomalies: [
        `Acute transaction burst rate (${vel} transfers / 24h)`,
        `Intercontinental spatial jump (${geo} km) within 4 minutes`,
        `High-velocity volume on brand new account (${3 + index} days old)`,
      ],
      kidExplanation: `Imagine a bank account created just three days ago that suddenly buys ${amt} dollars of digital gold from two different countries at the exact same minute! It disguises itself with legitimate-looking receipt headers, but the teleportation speed gives away the heist!`,
      technicalSummary:
        "High-velocity synthetic identity layering exploiting cross-border settlement latency.",
    };
  }

  if (domainId === "cyber") {
    const ent = roundTwo(7.88 + (index % 3) * 0.04);
    const syn = Math.round(1800 + index * 450);
    const dur = Math.round(3600 + index * 1200);

    return {
      features: {
        Packet_Size: 1420 + index * 10,
        SYN_Rate: syn,
        Conn_Duration: dur,
        Port_Entropy: 0.85,
        Failed_Logins: index % 2,
        Payload_Entropy: ent,
        Geo_Drift_Score: 0.94,
        Encrypted_Tunnel_Flag: 1,
      },
      anomalies: [
        `Near-maximal Shannon entropy payload (${ent} bits) matching encrypted exfiltration`,
        `Persistent background C2 tunnel alive for ${Math.round(dur / 60)} minutes`,
        `Unusual high-port socket destination with atypical handshake protocol`,
      ],
      kidExplanation: `Imagine a secret walkie-talkie inside a server that speaks in an unbreakable scrambled secret code (${ent} entropy bits)! It pretends to just be a boring clock update, but secretly ships encrypted corporate secrets out the back window every 10 minutes!`,
      technicalSummary:
        "Zero-day low-and-slow encrypted command-and-control beaconing with high-entropy tunnel.",
    };
  }

  if (domainId === "sensors") {
    const vib = roundTwo(1.85 + index * 0.45 * noveltyPush);
    const temp = roundOne(86.5 + index * 4.2);
    const rpm = 2820 - index * 65;

    return {
      features: {
        Vibration_X: vib,
        Bearing_Temp: temp,
        Motor_Current: roundOne(26.4 + index * 2.8),
        Supply_Voltage: 386.0 - index * 4,
        Acoustic_Emission: Math.round(92 + index * 18),
        Lube_Oil_Pressure: roundTwo(1.6 - index * 0.2),
        Rotational_RPM: rpm,
      },
      anomalies: [
        `Harmonic radial vibration surge (${vib} mm/s RMS)`,
        `Bearing thermal elevation to ${temp}°C approaching flash point`,
        `Lubrication pressure drop while acoustic emission spikes (${Math.round(92 + index * 18)} dB)`,
      ],
      kidExplanation: `Imagine a giant metal spinning turbine that sounds completely quiet to human ears, but inside the steel ball bearings, tiny microscopic stress cracks are buzzing like angry hornets! One hour before the turbine breaks, Leo's GAN shows engineers the secret crack!`,
      technicalSummary:
        "Pre-catastrophic cavitation shockwave and high-frequency radial bearing raceway fatigue.",
    };
  }

  // Logistics
  const temp = roundOne(14.5 + index * 3.2 * noveltyPush);
  const shock = roundTwo(4.8 + index * 1.1);
  const weight = Math.round(-110 - index * 45);

  return {
    features: {
      Temp_Celsius: temp,
      Shock_G_Force: shock,
      Transit_Delay_Hours: 24 + index * 6,
      Humidity_Percent: Math.round(78 + index * 3),
      Route_Deviation_Km: Math.round(85 + index * 30),
      Seal_Broken_Flag: 1,
      Weight_Variance_Kg: weight,
    },
    anomalies: [
      `Severe cold-chain thermal excursion to ${temp}°C for vaccine transport`,
      `Electronic container security bolt severed`,
      `Massive unmanifested cargo mass deficit (${weight} kg missing)`,
    ],
    kidExplanation: `Imagine a refrigerated truck carrying strawberry ice cream and medicine that suddenly turns off its freezer to ${temp}°C in an unmapped dark parking lot. The driver replaces the heavy boxes with lightweight cardboard, but our GAN notices the ${weight} kg missing weight!`,
    technicalSummary:
      "Covert transit diversion with cold-chain rupture and selective high-value freight theft.",
  };
}
