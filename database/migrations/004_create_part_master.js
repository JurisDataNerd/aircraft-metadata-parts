// Part Master linking (FR-05)
db.createCollection("part_master", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["part_number"],
      properties: {
        part_number: { bsonType: "string" },
      },
    },
  },
});

db.part_master.createIndex({ part_number: 1 }, { unique: true });
