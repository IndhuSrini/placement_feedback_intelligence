const VERIFIED_WEBSITES = {
  wipro: "https://www.wipro.com/",
  "tech mahindra": "https://www.techmahindra.com/",
  tcs: "https://www.tcs.com/",
  infosys: "https://www.infosys.com/",
  accenture: "https://www.accenture.com/",
  cognizant: "https://www.cognizant.com/",
  hcl: "https://www.hcltech.com/",
  hcltech: "https://www.hcltech.com/",
  capgemini: "https://www.capgemini.com/in-en/",
  deloitte: "https://www.deloitte.com/in/en.html",
  ibm: "https://www.ibm.com/in-en",
  freshworks: "https://www.freshworks.com/company/careers/",
  zoho: "https://www.zoho.com/",
  mitsuba: "https://www.mitsuba.co.jp/en/",
  mistral: "https://www.mistralsolutions.com/",
  "mistral solutions": "https://www.mistralsolutions.com/",
  "econ systems": "https://www.e-consystems.com/",
  "e-con systems": "https://www.e-consystems.com/",
};

export function getCompanyWebsite(company) {
  if (!company) return null;
  const rawWeb = company.website || company.official_website;
  if (
    rawWeb &&
    typeof rawWeb === "string" &&
    rawWeb.trim() !== "" &&
    rawWeb !== "null" &&
    rawWeb !== "None"
  ) {
    let url = rawWeb.trim();
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = "https://" + url;
    }
    return url;
  }
  const normName = (company.name || company.company || "")
    .toLowerCase()
    .trim();
  if (VERIFIED_WEBSITES[normName]) {
    return VERIFIED_WEBSITES[normName];
  }
  return null;
}
