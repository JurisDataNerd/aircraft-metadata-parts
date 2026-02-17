// 001_create_documents.js (SUDAH BENAR)
db.createCollection("documents", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["document_id", "document_type", "document_number"],
      properties: {
        document_id: { bsonType: "string" },
        document_type: { enum: ["IPD", "DRAWING"] },
        document_number: { bsonType: "string" },
        revision: { bsonType: "string" },
        issue_date: { bsonType: "date" },
        aircraft_model: { bsonType: "string" },
        source_pdf_path: { bsonType: "string" },
        file_hash: { bsonType: "string" },
        uploaded_at: { bsonType: "date" },
        parsing_status: {
          bsonType: "string",
          enum: ["pending", "processing", "completed", "failed"],
        },
        parts_count: { bsonType: "int" },
        error_message: { bsonType: "string" },
      },
    },
  },
});

db.documents.createIndex({ document_id: 1 }, { unique: true });
