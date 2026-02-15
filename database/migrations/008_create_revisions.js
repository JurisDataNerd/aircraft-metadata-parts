// Migration 008: Create revisions collection (UPDATED SCHEMA)
db.createCollection("revisions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["document_id", "document_number", "revision", "parts", "metadata"],
      properties: {
        document_id: { bsonType: "string" },
        document_number: { bsonType: "string" },
        revision: { bsonType: "string" },
        previous_revision_id: { bsonType: "objectId" },
        next_revision_id: { bsonType: "objectId" },
        parts: { bsonType: "array" },
        part_count: { bsonType: "int" },
        change_summary: { bsonType: "object" },
        changes: { bsonType: "array" },
        issue_date: { bsonType: "date" },
        source_pdf_path: { bsonType: "string" },
        file_hash: { bsonType: "string" },
        metadata: {
          bsonType: "object",
          required: ["created_by", "created_at", "status"],
          properties: {
            created_by: { bsonType: "string" },
            created_at: { bsonType: "date" },
            approved_by: { bsonType: "string" },
            approved_at: { bsonType: "date" },
            approval_notes: { bsonType: "string" },
            digital_signature: { bsonType: "string" },
            status: { enum: ["draft", "under_review", "approved", "superseded", "rejected"] },
          },
        },
        version: { bsonType: "int" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
      },
    },
  },
});

// Indexes
db.revisions.createIndex({ document_id: 1, revision: 1 }, { unique: true });
db.revisions.createIndex({ document_id: 1, created_at: -1 });
db.revisions.createIndex({ previous_revision_id: 1 });
db.revisions.createIndex({ next_revision_id: 1 });
db.revisions.createIndex({ "metadata.status": 1 });
db.revisions.createIndex({ file_hash: 1 });

print("✅ Migration 008 completed: revisions collection created");
