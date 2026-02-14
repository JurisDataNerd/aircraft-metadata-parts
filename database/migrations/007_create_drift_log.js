// Configuration Drift (FR-13)
db.createCollection("config_drift_log", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["line_number", "revision", "detected_at"],
      properties: {
        line_number: { bsonType: "int" },
        revision: { bsonType: "string" },
        detected_at: { bsonType: "date" },
      },
    },
  },
});

db.config_drift_log.createIndex({ line_number: 1, detected_at: -1 });
