#!/usr/bin/env node

/**
 * Upload a prepared dataset JSON file to the API
 *
 * Usage:
 *   node upload_dataset.js <filename>
 *   node upload_dataset.js borough_population_ranking.json
 *
 * The script will look for the file in ./prepared_data/ directory
 */

const fs = require("fs");
const path = require("path");

// Configuration
const API_URL = "http://localhost:5173/api/v1/dataset";
const PREPARED_DATA_DIR = "./data/prepared_data";

async function uploadDataset(filename) {
  try {
    // Construct file path
    const filePath = path.join(PREPARED_DATA_DIR, filename);

    // Check if file exists
    if (!fs.existsSync(filePath)) {
      console.error(`❌ Error: File not found: ${filePath}`);
      console.log(`\nAvailable files in ${PREPARED_DATA_DIR}:`);

      if (fs.existsSync(PREPARED_DATA_DIR)) {
        const files = fs
          .readdirSync(PREPARED_DATA_DIR)
          .filter((f) => f.endsWith(".json"));
        files.forEach((f) => console.log(`  - ${f}`));
      }
      process.exit(1);
    }

    // Read and parse JSON file
    console.log(`📂 Reading file: ${filePath}`);
    const fileContent = fs.readFileSync(filePath, "utf8");
    const dataset = JSON.parse(fileContent);

    // Validate required fields
    if (!dataset.title || !dataset.type || !dataset.city || !dataset.data) {
      console.error(
        "❌ Error: Dataset missing required fields (title, type, city, data)"
      );
      process.exit(1);
    }

    console.log(`📊 Dataset: ${dataset.title}`);
    console.log(`   Type: ${dataset.type}`);
    console.log(`   City: ${dataset.city}`);
    console.log(`   Data points: ${dataset.data.length}`);

    // Upload to API
    console.log(`\n🚀 Uploading to ${API_URL}...`);

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(dataset),
    });

    const result = await response.json();

    if (response.ok) {
      console.log(`✅ Success! Dataset created with ID: ${result.dataset_id}`);
      console.log(`   Message: ${result.message}`);
      console.log(
        `\n🔗 View at: http://localhost:5173/api/v1/dataset?id=${result.dataset_id}`
      );
    } else {
      console.error(`❌ Error: ${response.status} ${response.statusText}`);
      console.error(`   ${result.error || JSON.stringify(result)}`);
      process.exit(1);
    }
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
    process.exit(1);
  }
}

// Main execution
const filename = process.argv[2];

if (!filename) {
  console.error("❌ Error: No filename provided");
  console.log("\nUsage:");
  console.log("  node upload_dataset.js <filename>");
  console.log("\nExample:");
  console.log("  node upload_dataset.js borough_population_ranking.json");
  process.exit(1);
}

uploadDataset(filename);
