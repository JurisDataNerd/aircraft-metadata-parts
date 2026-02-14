// Risk Profile (FR-11)
db.createCollection("part_risk_profile", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["part_number", "risk_score"],
      properties: {
        part_number: { bsonType: "string" },
        risk_score: { bsonType: "double" },
      },
    },
  },
});

db.part_risk_profile.createIndex({ risk_score: -1 });
