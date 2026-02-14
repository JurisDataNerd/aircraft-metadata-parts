// Document collection (FR-01, FR-02)
db.createCollection("document", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["document_id", "document_type", "document_number", "revision"],
      properties: {
        document_id: { bsonType: "string" },
        document_type: { enum: ["IPD", "DRAWING"] },
        document_number: { bsonType: "string" },
        revision: { bsonType: "string" },
        issue_date: { bsonType: "date" },
        aircraft_model: { bsonType: "string" },
        source_pdf_path: { bsonType: "string" },
      },
    },
  },
});

// Indexes
db.document.createIndex({ document_id: 1 }, { unique: true });
db.document.createIndex({ document_number: 1, revision: 1 });
