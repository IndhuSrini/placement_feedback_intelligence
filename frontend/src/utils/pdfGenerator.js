import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

function cleanText(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/^["']|["']$/g, "")
    .replace(/^\d+[.)]\s*/, "")
    .trim();
}

function formatDate(value) {
  if (!value) return "Not reported";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function addPdfHeader(doc, title, subtitle) {
  // Primary header bar
  doc.setFillColor(79, 70, 229); // Indigo #4f46e5
  doc.rect(0, 0, 210, 24, "F");

  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  doc.text(title, 14, 12);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.text(subtitle, 14, 18);

  // Report metadata bar
  doc.setFillColor(248, 250, 252);
  doc.rect(0, 24, 210, 10, "F");

  doc.setDrawColor(226, 232, 240);
  doc.line(0, 34, 210, 34);

  doc.setTextColor(71, 85, 105);
  doc.setFontSize(8);
  doc.text(`Generated: ${new Date().toLocaleDateString("en-IN")}`, 14, 30.5);
  doc.text("CSE Placement Cycle (Batch 2023-2027) • Placement Feedback Intelligence", 95, 30.5);
}

function addPdfFooter(doc) {
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(148, 163, 184);

    doc.setDrawColor(241, 245, 249);
    doc.line(14, 285, 196, 285);

    doc.text(
      "Placement Feedback Intelligence System — Official Engineering Capstone Report",
      14,
      290
    );
    doc.text(`Page ${i} of ${pageCount}`, 180, 290);
  }
}

/**
 * Generate Company Details PDF Report
 */
export function generateCompanyPdfReport(data, company, websiteUrl, normalizedRounds) {
  const doc = new jsPDF("p", "mm", "a4");
  const companyName = company?.name || data?.company || "Company";
  const cleanCompName = companyName.replace(/[^a-zA-Z0-9]/g, "_");

  addPdfHeader(
    doc,
    "PLACEMENT INTELLIGENCE — COMPANY REPORT",
    `Recruitment Intelligence & Interview Feedback Analysis for ${companyName}`
  );

  let y = 42;

  // 1. Company Overview
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("1. Company Overview", 14, y);
  y += 4;

  const overviewRows = [
    ["Company Name", companyName, "Industry / Sector", company?.industry || data?.industry || "Information Technology"],
    ["Official Website", websiteUrl || "Not reported", "Drives Analyzed", `${data?.drives_count || 1} Drive(s)`],
    ["Target Job Role", data?.job_role || "Software Engineer", "Recruitment Date", formatDate(data?.recruitment_date)],
  ];

  autoTable(doc, {
    startY: y,
    body: overviewRows,
    theme: "grid",
    styles: { fontSize: 8.5, cellPadding: 3, textColor: [51, 65, 85] },
    columnStyles: {
      0: { fontStyle: "bold", fillColor: [241, 245, 249], cellWidth: 35 },
      1: { cellWidth: 60 },
      2: { fontStyle: "bold", fillColor: [241, 245, 249], cellWidth: 35 },
      3: { cellWidth: 52 },
    },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  // 2. Eligibility Criteria
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("2. Eligibility Criteria Summary", 14, y);
  y += 4;

  const eligibility = data?.eligibility || {};
  const eligibilityRows = [
    [
      "Minimum CGPA Threshold",
      eligibility.minimum_cgpa != null ? `${eligibility.minimum_cgpa} CGPA` : "Not specified",
      "Backlog Policy",
      eligibility.maximum_backlogs != null ? `${eligibility.maximum_backlogs} max allowed` : "No backlogs policy specified",
    ],
    [
      "Eligible Branches",
      Array.isArray(eligibility.branch_eligibility) ? eligibility.branch_eligibility.join(", ") : (eligibility.branch_eligibility || "CSE, ISE, ECE, IT"),
      "Batch / Cycle",
      "Batch 2023 - 2027 CSE",
    ],
  ];

  autoTable(doc, {
    startY: y,
    body: eligibilityRows,
    theme: "grid",
    styles: { fontSize: 8.5, cellPadding: 3, textColor: [51, 65, 85] },
    columnStyles: {
      0: { fontStyle: "bold", fillColor: [241, 245, 249], cellWidth: 40 },
      1: { cellWidth: 55 },
      2: { fontStyle: "bold", fillColor: [241, 245, 249], cellWidth: 35 },
      3: { cellWidth: 52 },
    },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  // 3. Recruitment Process (Normalized rounds)
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text(`3. Recruitment Process (${normalizedRounds.length} Sequential Stages)`, 14, y);
  y += 4;

  const roundsRows = normalizedRounds.map((r, idx) => [
    `Stage ${idx + 1}`,
    r.displayName || r.round_name || r.round_type || "Assessment Round",
    r.description || r.details || "Standard evaluation round",
    r.difficulty || "Medium",
  ]);

  autoTable(doc, {
    startY: y,
    head: [["Round #", "Stage Name", "Stage Details / Focus", "Evaluated Difficulty"]],
    body: roundsRows.length > 0 ? roundsRows : [["-", "No round details recorded", "-", "-"]],
    theme: "striped",
    headStyles: { fillColor: [79, 70, 229], textColor: [255, 255, 255], fontStyle: "bold", fontSize: 8.5 },
    styles: { fontSize: 8.5, cellPadding: 3 },
    columnStyles: {
      0: { fontStyle: "bold", cellWidth: 20 },
      1: { cellWidth: 50, fontStyle: "bold" },
      2: { cellWidth: 80 },
      3: { cellWidth: 32 },
    },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  // Check if new page is needed for Technical Topics and Questions
  if (y > 210) {
    doc.addPage();
    addPdfHeader(doc, "PLACEMENT INTELLIGENCE — COMPANY REPORT", `Technical & Question Intelligence for ${companyName}`);
    y = 42;
  }

  // 4. Technical Topic Intelligence
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("4. Technical Topic Intelligence", 14, y);
  y += 4;

  const rawTopics = Array.isArray(data?.topics) ? data.topics : [];
  const topicRows = rawTopics.slice(0, 12).map((t, idx) => [
    idx + 1,
    cleanText(t.topic || t.name),
    cleanText(t.category || "Technical"),
    `${t.occurrence_count || t.count || 1} discussion(s)`,
  ]);

  autoTable(doc, {
    startY: y,
    head: [["#", "Technical Topic", "Category", "Mentions / Frequency"]],
    body: topicRows.length > 0 ? topicRows : [["-", "No technical topic metrics recorded", "-", "-"]],
    theme: "striped",
    headStyles: { fillColor: [79, 70, 229], textColor: [255, 255, 255], fontStyle: "bold", fontSize: 8.5 },
    styles: { fontSize: 8.5, cellPadding: 3 },
    columnStyles: {
      0: { cellWidth: 15 },
      1: { cellWidth: 70, fontStyle: "bold" },
      2: { cellWidth: 55 },
      3: { cellWidth: 42 },
    },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  if (y > 210) {
    doc.addPage();
    addPdfHeader(doc, "PLACEMENT INTELLIGENCE — COMPANY REPORT", `Interview Question Bank for ${companyName}`);
    y = 42;
  }

  // 5. Frequently Asked Questions
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("5. Frequently Asked Interview Questions", 14, y);
  y += 4;

  const rawQuestions = Array.isArray(data?.frequent_questions) ? data.frequent_questions : [];
  const questionRows = rawQuestions.slice(0, 12).map((q, idx) => [
    idx + 1,
    cleanText(q.question || q.question_text),
    `Asked ${q.occurrence_count || q.count || 1} time(s)`,
    q.difficulty || "Medium",
    q.confidence_score ? `${Math.round(q.confidence_score)}%` : "N/A",
    q.verification_status === "verified" ? "Verified" : "Reported",
  ]);

  autoTable(doc, {
    startY: y,
    head: [["#", "Interview Question", "Frequency", "Difficulty", "Confidence", "Status"]],
    body: questionRows.length > 0 ? questionRows : [["-", "No questions recorded", "-", "-", "-", "-"]],
    theme: "grid",
    headStyles: { fillColor: [79, 70, 229], textColor: [255, 255, 255], fontStyle: "bold", fontSize: 8 },
    styles: { fontSize: 8, cellPadding: 2.5, overflow: "linebreak" },
    columnStyles: {
      0: { cellWidth: 10 },
      1: { cellWidth: 95 },
      2: { cellWidth: 26 },
      3: { cellWidth: 20 },
      4: { cellWidth: 18 },
      5: { cellWidth: 13 },
    },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  if (y > 240) {
    doc.addPage();
    addPdfHeader(doc, "PLACEMENT INTELLIGENCE — COMPANY REPORT", `Key Placement Insights for ${companyName}`);
    y = 42;
  }

  // 6. Placement Intelligence Insights Summary
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("6. Key Placement Intelligence Insights", 14, y);
  y += 6;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(51, 65, 85);

  const insight1 = `• Recruitment Sequence: ${normalizedRounds.length} sequential rounds identified (${normalizedRounds.map((r) => r.displayName || r.round_type).join(" -> ") || "Stages mapped"}).`;
  const insight2 = `• Question Catalog: ${rawQuestions.length} interview questions extracted and indexed for placement preparation.`;
  const insight3 = `• Technical Focus: Primary focus detected on ${rawTopics.slice(0, 3).map((t) => cleanText(t.topic || t.name)).join(", ") || "core computer science topics"}.`;

  const lines1 = doc.splitTextToSize(insight1, 180);
  doc.text(lines1, 14, y);
  y += lines1.length * 4.5 + 2;

  const lines2 = doc.splitTextToSize(insight2, 180);
  doc.text(lines2, 14, y);
  y += lines2.length * 4.5 + 2;

  const lines3 = doc.splitTextToSize(insight3, 180);
  doc.text(lines3, 14, y);

  addPdfFooter(doc);
  doc.save(`Placement_Intelligence_${cleanCompName}_Report.pdf`);
}

/**
 * Generate Analytics System Overview PDF Report
 */
export function generateAnalyticsPdfReport(
  overview,
  processedTopics,
  processedCategories,
  difficultyStats,
  eligibilityChartData,
  confidence
) {
  const doc = new jsPDF("p", "mm", "a4");

  addPdfHeader(
    doc,
    "PLACEMENT INTELLIGENCE — ANALYTICS REPORT",
    "System-Wide Placement Intelligence, Topics, Questions & Eligibility Analysis"
  );

  let y = 42;

  // 1. System Overview KPIs
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("1. System Overview Metrics", 14, y);
  y += 4;

  const totalCompanies = Number(overview?.total_companies || 0);
  const totalDrives = Number(overview?.total_placement_drives || 0);
  const totalQuestions = Number(overview?.total_questions || 0);
  const totalTopics = Number(overview?.total_topics || 0);
  const totalRounds = Number(overview?.total_recruitment_rounds || 0);
  const avgConfidence = Math.min(Math.max(Number(confidence?.average_confidence || 0), 0), 100);

  const kpiRows = [
    ["Recruiting Companies Tracked", String(totalCompanies), "Campus Placement Drives", String(totalDrives)],
    ["Questions Analyzed", String(totalQuestions), "Technical Topics Catalogued", String(totalTopics)],
    ["Recruitment Rounds Mapped", String(totalRounds), "Average AI Confidence Score", `${avgConfidence.toFixed(2)}%`],
  ];

  autoTable(doc, {
    startY: y,
    body: kpiRows,
    theme: "grid",
    styles: { fontSize: 8.5, cellPadding: 3, textColor: [51, 65, 85] },
    columnStyles: {
      0: { fontStyle: "bold", fillColor: [241, 245, 249], cellWidth: 50 },
      1: { cellWidth: 42, fontStyle: "bold" },
      2: { fontStyle: "bold", fillColor: [241, 245, 249], cellWidth: 50 },
      3: { cellWidth: 40, fontStyle: "bold" },
    },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  // 2. Top Technical Topics
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("2. Frequently Discussed Technical Topics", 14, y);
  y += 4;

  const topicRows = (processedTopics || []).slice(0, 15).map((t, idx) => [
    idx + 1,
    t.name,
    t.category || "Technical",
    `${t.count} discussion(s)`,
  ]);

  autoTable(doc, {
    startY: y,
    head: [["#", "Technical Topic", "Category", "Mentions / Frequency"]],
    body: topicRows.length > 0 ? topicRows : [["-", "No topics available", "-", "-"]],
    theme: "striped",
    headStyles: { fillColor: [79, 70, 229], textColor: [255, 255, 255], fontStyle: "bold", fontSize: 8.5 },
    styles: { fontSize: 8.5, cellPadding: 2.8 },
    columnStyles: {
      0: { cellWidth: 15 },
      1: { cellWidth: 75, fontStyle: "bold" },
      2: { cellWidth: 55 },
      3: { cellWidth: 37 },
    },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  if (y > 210) {
    doc.addPage();
    addPdfHeader(doc, "PLACEMENT INTELLIGENCE — ANALYTICS REPORT", "Category, Difficulty & Eligibility Analytics");
    y = 42;
  }

  // 3. Category & Difficulty Distribution
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("3. Category & Difficulty Distribution Summary", 14, y);
  y += 4;

  const catRows = (processedCategories || []).map((c) => [
    c.name,
    `${c.value} topics`,
    `${c.percentage}%`,
  ]);

  autoTable(doc, {
    startY: y,
    head: [["Topic Category", "Occurrence Count", "Proportion (%)"]],
    body: catRows.length > 0 ? catRows : [["No categories available", "-", "-"]],
    theme: "grid",
    headStyles: { fillColor: [79, 70, 229], textColor: [255, 255, 255], fontStyle: "bold", fontSize: 8.5 },
    styles: { fontSize: 8.5, cellPadding: 2.8 },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  // 4. Eligibility Intelligence
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("4. Company Eligibility Cutoffs", 14, y);
  y += 4;

  const eligRows = (eligibilityChartData || []).slice(0, 12).map((e, idx) => [
    idx + 1,
    e.company,
    `${e.cgpa} Minimum CGPA`,
    `${e.backlogs} Max Backlogs Allowed`,
  ]);

  autoTable(doc, {
    startY: y,
    head: [["#", "Company Name", "CGPA Threshold", "Backlog Allowance Policy"]],
    body: eligRows.length > 0 ? eligRows : [["-", "No eligibility data recorded", "-", "-"]],
    theme: "striped",
    headStyles: { fillColor: [79, 70, 229], textColor: [255, 255, 255], fontStyle: "bold", fontSize: 8.5 },
    styles: { fontSize: 8.5, cellPadding: 2.8 },
    columnStyles: {
      0: { cellWidth: 15 },
      1: { cellWidth: 70, fontStyle: "bold" },
      2: { cellWidth: 48 },
      3: { cellWidth: 49 },
    },
    margin: { left: 14, right: 14 },
  });

  y = doc.lastAutoTable.finalY + 8;

  if (y > 230) {
    doc.addPage();
    addPdfHeader(doc, "PLACEMENT INTELLIGENCE — ANALYTICS REPORT", "System Placement Insights");
    y = 42;
  }

  // 5. System Insights
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.text("5. Primary System Placement Insights", 14, y);
  y += 6;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(51, 65, 85);

  const topTopicName = processedTopics?.[0]?.name || "Technical Subjects";
  const insightLines = [
    `• Dominant Domain: "${topTopicName}" is the single most discussed technical topic across student candidate feedback.`,
    `• Catalogued Questions: ${totalQuestions} unique interview questions catalogued across ${totalCompanies} recruiting companies.`,
    `• AI Extraction Reliability: System maintains an overall confidence score of ${avgConfidence.toFixed(1)}%.`,
  ];

  for (const line of insightLines) {
    const wrapped = doc.splitTextToSize(line, 180);
    doc.text(wrapped, 14, y);
    y += wrapped.length * 4.5 + 2;
  }

  addPdfFooter(doc);
  doc.save("Placement_Intelligence_Analytics_Report.pdf");
}
