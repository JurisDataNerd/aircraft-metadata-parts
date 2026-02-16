// Migration 008: Create revisions collection (UPDATED FOR STICKERS)
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

        // Parts snapshot with sticker info
        parts: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              part_number: { bsonType: "string" },
              is_sticker: { bsonType: "bool" },
              sticker_type: { bsonType: "string" },
              sticker_text: { bsonType: "string" },
            },
          },
        },

        part_count: { bsonType: "int" },
        sticker_count: { bsonType: "int" }, // New

        change_summary: {
          bsonType: "object",
          properties: {
            type: { enum: ["INITIAL", "UPDATE", "ADD", "MODIFY", "DELETE"] },
            added_parts: { bsonType: "array" },
            removed_parts: { bsonType: "array" },
            modified_parts: { bsonType: "array" },
            sticker_changes: { bsonType: "array" }, // New
          },
        },

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

// Additional indexes
db.revisions.createIndex({ "parts.is_sticker": 1 });
db.revisions.createIndex({ sticker_count: 1 });
