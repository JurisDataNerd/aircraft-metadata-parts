// IPD Parts collection (FR-01)
db.createCollection("ipd_parts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["ipd_part_id", "document_id", "part_number", "effectivity_type"],
      properties: {
        ipd_part_id: { bsonType: "string" },
        document_id: { bsonType: "objectId" },
        part_number: { bsonType: "string" },
        effectivity_type: { enum: ["LIST", "RANGE"] },
      },
    },
  },
});

// Indexes untuk performance
db.ipd_parts.createIndex({ part_number: 1 });
db.ipd_parts.createIndex({ document_id: 1 });
db.ipd_parts.createIndex({ effectivity_values: 1 });
