// Decision Log (FR-05)
db.createCollection("decision_log", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "part_number", "line_number", "timestamp_open"],
      properties: {
        user_id: { bsonType: "string" },
        part_number: { bsonType: "string" },
        line_number: { bsonType: "int" },
      },
    },
  },
});

db.decision_log.createIndex({ user_id: 1, timestamp_open: -1 });
db.decision_log.createIndex({ part_number: 1, timestamp_open: -1 });
