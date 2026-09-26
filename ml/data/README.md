# Data Provenance & Metadata Standard

Every empirical dataset deposited into `data/` or `ml/data/` must include a companion `manifest.json` conforming to this schema:

```json
{
  "dataset_id": "usda_produce_respiration_v1",
  "source": "USDA Agricultural Handbook No. 66",
  "source_url": "https://www.ars.usda.gov/is/np/commercialcargohandbook/commercialcargohandbook.pdf",
  "collection_date": "2026-10-01",
  "curator": "PackWise Data Working Group",
  "license": "Public Domain (US Government Work)",
  "variables": {
    "commodity": "Produce name",
    "temp_c": "Storage temperature in Celsius",
    "respiration_mg_co2_kg_hr": "Respiration rate in mg CO2 per kg fresh weight per hour"
  },
  "transformations": [
    "Extracted from PDF Table 2, normalized temperature from Fahrenheit to Celsius"
  ],
  "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

No uncurated, untracked, or scraped data without explicit provenance is allowed.
